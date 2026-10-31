from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any

from backend.app.core.database import get_db
from backend.app.models.models import User, Document, ChatSession, ChatMessage, VisibilityType, UserRole
from backend.app.models.schemas import SystemStatsResponse, UserResponse, UserUpdate
from backend.app.api.deps import get_current_admin_user
from backend.app.services.chroma_service import chroma_service
from backend.app.services.sync_service import vector_sync_service
from backend.app.core.config import settings
from backend.app.core.security import get_password_hash

router = APIRouter(prefix="/admin", tags=["Admin Management"])

@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    user_count = (await db.execute(select(func.count(User.id)))).scalar() or 0
    doc_count = (await db.execute(select(func.count(Document.id)))).scalar() or 0
    personal_count = (await db.execute(select(func.count(Document.id)).where(Document.visibility == VisibilityType.PERSONAL))).scalar() or 0
    public_count = (await db.execute(select(func.count(Document.id)).where(Document.visibility == VisibilityType.PUBLIC))).scalar() or 0
    session_count = (await db.execute(select(func.count(ChatSession.id)))).scalar() or 0
    message_count = (await db.execute(select(func.count(ChatMessage.id)))).scalar() or 0

    chunk_count = chroma_service.count()

    return SystemStatsResponse(
        total_users=user_count,
        total_documents=doc_count,
        personal_documents=personal_count,
        public_documents=public_count,
        total_chunks=chunk_count,
        total_sessions=session_count,
        total_messages=message_count,
        vector_collection_name=settings.CHROMA_COLLECTION_NAME
    )

@router.get("/users-overview")
async def get_users_overview(
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    result = await db.execute(select(User).order_by(User.id.asc()))
    users = result.scalars().all()

    overview = []
    for u in users:
        d_count = (await db.execute(select(func.count(Document.id)).where(Document.owner_id == u.id))).scalar() or 0
        s_count = (await db.execute(select(func.count(ChatSession.id)).where(ChatSession.user_id == u.id))).scalar() or 0
        overview.append({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role.value,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "documents_count": d_count,
            "sessions_count": s_count,
        })
    return overview

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user_account(
    user_id: int,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete own administrator account"
        )

    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Purge vectors for all documents owned by user
    doc_res = await db.execute(select(Document).where(Document.owner_id == user_id))
    user_docs = doc_res.scalars().all()
    for d in user_docs:
        vector_sync_service.purge_vectors(d.document_uuid)
        vector_sync_service.remove_physical_file(d.file_path)

    await db.delete(user)
    await db.commit()
    return {"detail": f"User {user.email} and all associated documents and vector records purged."}

@router.put("/users/{user_id}", response_model=UserResponse)
@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user_account(
    user_id: int,
    user_in: UserUpdate,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user_in.email is not None and user_in.email != user.email:
        check_res = await db.execute(select(User).where(User.email == user_in.email))
        existing_user = check_res.scalar_one_or_none()
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists"
            )
        user.email = user_in.email

    if user_in.full_name is not None and user_in.full_name.strip():
        user.full_name = user_in.full_name.strip()

    if user_in.role is not None:
        user.role = user_in.role

    if user_in.password is not None and user_in.password.strip():
        user.password_hash = get_password_hash(user_in.password.strip())

    await db.commit()
    await db.refresh(user)
    return user

from pydantic import BaseModel
class OpenAIKeyUpdate(BaseModel):
    api_key: str

@router.get("/ai-status")
async def get_ai_status(admin: User = Depends(get_current_admin_user)):
    key = settings.OPENAI_API_KEY
    if not key:
        return {
            "status": "not_configured",
            "mode": "OpenAI Only (Not Configured)",
            "message": (
                "No OpenAI API key configured. "
                "The system requires a valid OpenAI API key to generate embeddings and answer questions. "
                "Please add your OPENAI_API_KEY via the Admin panel or .env file."
            ),
            "has_key": False
        }
    
    # Test key with OpenAI
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        client.models.list()
        return {
            "status": "connected",
            "mode": "OpenAI Cloud Engine (GPT-4o + text-embedding-3-small)",
            "message": "OpenAI API connection verified and active.",
            "has_key": True,
            "key_preview": f"{key[:7]}...{key[-4:]}"
        }
    except Exception as e:
        return {
            "status": "invalid_key",
            "mode": "Deterministic Fallback Activated",
            "message": f"OpenAI authentication error: {str(e)}",
            "has_key": True,
            "key_preview": f"{key[:7]}...{key[-4:]}" if len(key) > 11 else "Invalid"
        }

@router.post("/update-ai-key")
async def update_ai_key(
    payload: OpenAIKeyUpdate,
    admin: User = Depends(get_current_admin_user)
):
    new_key = payload.api_key.strip()
    if not new_key:
        raise HTTPException(status_code=400, detail="API Key cannot be empty")
    
    # Validate with OpenAI
    try:
        from openai import OpenAI
        test_client = OpenAI(api_key=new_key)
        test_client.models.list()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"OpenAI Authentication Failed: {str(e)}"
        )
    
    # Update active service and config
    from backend.app.services.embedding_service import embedding_service
    embedding_service.update_api_key(new_key)
    
    # Save into .env
    env_file = settings.BASE_DIR / ".env"
    try:
        content = ""
        if env_file.exists():
            content = env_file.read_text(encoding="utf-8")
        import re
        if "OPENAI_API_KEY=" in content:
            content = re.sub(r"OPENAI_API_KEY=.*", f"OPENAI_API_KEY={new_key}", content)
        else:
            content += f"\nOPENAI_API_KEY={new_key}\n"
        env_file.write_text(content, encoding="utf-8")
    except Exception as err:
        print(f"Warning: could not write to .env: {err}")
        
    return {
        "success": True,
        "detail": "OpenAI API key validated and activated successfully!",
        "key_preview": f"{new_key[:7]}...{new_key[-4:]}"
    }
