import json
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from backend.app.core.database import get_db
from backend.app.models.models import User, ChatSession, ChatMessage, Document, SearchModeType
from backend.app.models.schemas import (
    ChatQueryRequest, ChatQueryResponse, ChatSessionResponse,
    ChatMessageResponse, CitationItem
)
from backend.app.api.deps import get_current_user
from backend.app.services.rag_service import rag_query_engine

router = APIRouter(prefix="/chat", tags=["AI Chatbot & RAG QA Engine"])

@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    search_mode: SearchModeType = SearchModeType.PRIVATE,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    session = ChatSession(
        session_uuid=str(uuid.uuid4()),
        user_id=current_user.id,
        search_mode=search_mode
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return ChatSessionResponse(
        id=session.id,
        session_uuid=session.session_uuid,
        search_mode=session.search_mode,
        created_at=session.created_at,
        messages=[]
    )

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def list_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(desc(ChatSession.created_at))
    )
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    
    response_list = []
    for s in sessions:
        response_list.append(
            ChatSessionResponse(
                id=s.id,
                session_uuid=s.session_uuid,
                search_mode=s.search_mode,
                created_at=s.created_at,
                messages=[]
            )
        )
    return response_list

@router.get("/sessions/{session_uuid}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_uuid: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.session_uuid == session_uuid)
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to session")

    # Build messages with citations
    formatted_messages = []
    for msg in session.messages:
        citations = []
        if msg.source_document_uuids:
            try:
                uuids = json.loads(msg.source_document_uuids)
                if uuids:
                    doc_res = await db.execute(select(Document).where(Document.document_uuid.in_(uuids)))
                    docs = doc_res.scalars().all()
                    for d in docs:
                        citations.append(
                            CitationItem(
                                document_uuid=d.document_uuid,
                                filename=d.filename,
                                file_type=d.file_type,
                                download_url=f"/api/v1/documents/{d.document_uuid}/download",
                                snippet=None
                            )
                        )
            except Exception:
                pass

        formatted_messages.append(
            ChatMessageResponse(
                id=msg.id,
                sender_role=msg.sender_role,
                message_text=msg.message_text,
                source_documents=citations,
                timestamp=msg.timestamp
            )
        )

    return ChatSessionResponse(
        id=session.id,
        session_uuid=session.session_uuid,
        search_mode=session.search_mode,
        created_at=session.created_at,
        messages=formatted_messages
    )

@router.delete("/sessions/{session_uuid}", status_code=status.HTTP_200_OK)
async def delete_chat_session(
    session_uuid: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ChatSession).where(ChatSession.session_uuid == session_uuid))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    await db.delete(session)
    await db.commit()
    return {"detail": "Chat session deleted"}

@router.post("/query", response_model=ChatQueryResponse)
async def query_rag_chat(
    req: ChatQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Resolve or create chat session
    search_mode = req.search_mode or SearchModeType.PRIVATE
    session = None
    if req.session_uuid:
        res = await db.execute(select(ChatSession).where(ChatSession.session_uuid == req.session_uuid))
        session = res.scalar_one_or_none()

    if not session:
        session = ChatSession(
            session_uuid=str(uuid.uuid4()),
            user_id=current_user.id,
            search_mode=search_mode
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
    else:
        if session.search_mode != search_mode:
            session.search_mode = search_mode
            await db.commit()

    # 2. Retrieve context from ChromaDB with pre-filtered Search Mode Strategy
    matched_chunks = rag_query_engine.retrieve_context(
        query=req.query,
        mode=search_mode,
        user_id=current_user.id,
        top_k=5
    )

    # 3. Synthesize grounded answer via LLM (GPT-4o / fallback)
    answer = rag_query_engine.synthesize_answer(query=req.query, chunks=matched_chunks)

    # 4. Extract unique source Document UUIDs from chunks
    source_uuids = []
    chunk_snippets = {}
    for c in matched_chunks:
        doc_uuid = c.get("metadata", {}).get("document_uuid")
        if doc_uuid and doc_uuid not in source_uuids:
            source_uuids.append(doc_uuid)
            chunk_snippets[doc_uuid] = c.get("chunk_text", "")[:200]

    # 5. Resolve source documents metadata from SQLite
    citations: List[CitationItem] = []
    if source_uuids:
        res = await db.execute(select(Document).where(Document.document_uuid.in_(source_uuids)))
        docs = res.scalars().all()
        for doc in docs:
            citations.append(
                CitationItem(
                    document_uuid=doc.document_uuid,
                    filename=doc.filename,
                    file_type=doc.file_type,
                    download_url=f"/api/v1/documents/{doc.document_uuid}/download",
                    snippet=chunk_snippets.get(doc.document_uuid)
                )
            )

    # 6. Record conversation in SQLite: User message and Assistant response
    user_msg = ChatMessage(
        session_id=session.id,
        sender_role="USER",
        message_text=req.query,
        source_document_uuids=None
    )
    asst_msg = ChatMessage(
        session_id=session.id,
        sender_role="ASSISTANT",
        message_text=answer,
        source_document_uuids=json.dumps(source_uuids) if source_uuids else None
    )
    db.add_all([user_msg, asst_msg])
    await db.commit()

    return ChatQueryResponse(
        session_uuid=session.session_uuid,
        query=req.query,
        answer=answer,
        sources=citations,
        search_mode=search_mode
    )
