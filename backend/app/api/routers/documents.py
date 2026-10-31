import os
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, desc

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models.models import User, UserRole, Document, VisibilityType
from backend.app.models.schemas import DocumentResponse, DocumentUpdate
from backend.app.api.deps import get_current_user
from backend.app.services.sync_service import vector_sync_service

router = APIRouter(prefix="/documents", tags=["Document Management"])

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    visibility: VisibilityType = Form(VisibilityType.PERSONAL),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Validate File Extension (IEEE/SDD Requirement: Only PDF, DOCX, TXT allowed)
    orig_filename = file.filename or "unknown"
    file_ext = Path(orig_filename).suffix.lower()

    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported file format '{file_ext}'. Allowed formats: .pdf, .docx, .txt"
        )

    # 2. Read content and validate size (Max 25MB)
    file_bytes = await file.read()
    file_size = len(file_bytes)

    if file_size > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_BYTES // (1024*1024)}MB"
        )
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File content is empty"
        )

    # 3. Generate unique UUID and persist binary to disk
    doc_uuid = str(uuid.uuid4())
    stored_filename = f"{doc_uuid}_{orig_filename}"
    saved_file_path = settings.UPLOAD_DIR / stored_filename

    try:
        with open(saved_file_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to persist file binary: {str(e)}"
        )

    # 4. Save metadata record to SQLite Database
    doc_record = Document(
        document_uuid=doc_uuid,
        owner_id=current_user.id,
        filename=orig_filename,
        file_path=str(saved_file_path),
        file_type=file_ext.replace(".", ""),
        file_size_bytes=file_size,
        visibility=visibility
    )
    db.add(doc_record)
    await db.commit()
    await db.refresh(doc_record)

    # 5. Ingestion Pipeline: Parse text, chunk, embed, and index into ChromaDB
    try:
        vector_sync_service.index_document_content(
            document_uuid=doc_uuid,
            owner_id=current_user.id,
            visibility=visibility.value,
            filename=orig_filename,
            file_bytes=file_bytes,
            file_ext=file_ext
        )
    except Exception as e:
        print(f"[DocumentUpload] Warning: vector indexing failed: {e}")

    return doc_record

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    scope: str = Query("all", pattern="^(personal|public|all)$"),
    search: Optional[str] = None,
    file_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Document)

    # Apply Scope Restrictions
    if scope == "personal":
        query = query.where(and_(Document.owner_id == current_user.id, Document.visibility == VisibilityType.PERSONAL))
    elif scope == "public":
        query = query.where(Document.visibility == VisibilityType.PUBLIC)
    else:  # "all"
        if current_user.role == UserRole.ADMIN:
            pass  # Admin can see all
        else:
            query = query.where(
                or_(
                    Document.owner_id == current_user.id,
                    Document.visibility == VisibilityType.PUBLIC
                )
            )

    # Keyword filter
    if search:
        query = query.where(Document.filename.ilike(f"%{search}%"))

    # File type filter
    if file_type:
        clean_ext = file_type.replace(".", "").lower()
        query = query.where(Document.file_type == clean_ext)

    query = query.order_by(desc(Document.created_at))
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{document_uuid}", response_model=DocumentResponse)
async def get_document(
    document_uuid: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Document).where(Document.document_uuid == document_uuid))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Access control
    if doc.visibility != VisibilityType.PUBLIC and doc.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this document")

    return doc

@router.get("/{document_uuid}/download")
async def download_document(
    document_uuid: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Document).where(Document.document_uuid == document_uuid))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Access control
    if doc.visibility != VisibilityType.PUBLIC and doc.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this document")

    path = Path(doc.file_path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Physical file missing from storage")

    return FileResponse(
        path=str(path),
        filename=doc.filename,
        media_type="application/octet-stream"
    )

@router.put("/{document_uuid}", response_model=DocumentResponse)
async def update_document_metadata_or_file(
    document_uuid: str,
    visibility: Optional[VisibilityType] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Document).where(Document.document_uuid == document_uuid))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Ownership check
    if doc.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner or admin can update document")

    if visibility:
        doc.visibility = visibility

    if file:
        orig_filename = file.filename or doc.filename
        file_ext = Path(orig_filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unsupported file format '{file_ext}'"
            )
        file_bytes = await file.read()
        if len(file_bytes) > settings.MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="File exceeds maximum 25MB limit"
            )

        # Update physical file
        vector_sync_service.remove_physical_file(doc.file_path)
        stored_filename = f"{doc_uuid}_{orig_filename}" if 'doc_uuid' in locals() else f"{doc.document_uuid}_{orig_filename}"
        saved_file_path = settings.UPLOAD_DIR / stored_filename
        with open(saved_file_path, "wb") as f:
            f.write(file_bytes)

        doc.filename = orig_filename
        doc.file_path = str(saved_file_path)
        doc.file_type = file_ext.replace(".", "")
        doc.file_size_bytes = len(file_bytes)

        # Trigger Vector Re-indexing (TC-SYNC-02)
        vector_sync_service.reindex_document(
            document_uuid=doc.document_uuid,
            owner_id=doc.owner_id,
            visibility=doc.visibility.value,
            filename=doc.filename,
            new_file_bytes=file_bytes,
            file_ext=file_ext
        )
    elif visibility:
        # Re-index existing file to refresh visibility metadata in ChromaDB
        if Path(doc.file_path).exists():
            with open(doc.file_path, "rb") as f:
                content = f.read()
            vector_sync_service.reindex_document(
                document_uuid=doc.document_uuid,
                owner_id=doc.owner_id,
                visibility=doc.visibility.value,
                filename=doc.filename,
                new_file_bytes=content,
                file_ext=f".{doc.file_type}"
            )

    await db.commit()
    await db.refresh(doc)
    return doc

@router.delete("/{document_uuid}", status_code=status.HTTP_200_OK)
async def delete_document(
    document_uuid: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Document).where(Document.document_uuid == document_uuid))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Security check: owner or admin
    if doc.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner or admin can delete document")

    # 1. Cascade Vector Purge (TC-SYNC-01)
    vector_sync_service.purge_vectors(doc.document_uuid)

    # 2. Remove physical binary from disk
    vector_sync_service.remove_physical_file(doc.file_path)

    # 3. Delete metadata record from SQLite
    await db.delete(doc)
    await db.commit()

    return {"detail": "Document and associated vectors purged successfully", "document_uuid": document_uuid}
