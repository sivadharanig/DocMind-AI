from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict
from backend.app.models.models import UserRole, VisibilityType, SearchModeType

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = UserRole.USER

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    model_config = ConfigDict(extra="ignore")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None

# Document Schemas
class DocumentResponse(BaseModel):
    id: int
    document_uuid: str
    owner_id: int
    filename: str
    file_type: str
    file_size_bytes: int
    visibility: VisibilityType
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DocumentUpdate(BaseModel):
    visibility: Optional[VisibilityType] = None
    filename: Optional[str] = None

# Citation Schema
class CitationItem(BaseModel):
    document_uuid: str
    filename: str
    file_type: str
    download_url: str
    snippet: Optional[str] = None

# Chat & RAG Schemas
class ChatQueryRequest(BaseModel):
    query: str
    search_mode: Optional[SearchModeType] = SearchModeType.PRIVATE
    session_uuid: Optional[str] = None

class ChatMessageResponse(BaseModel):
    id: int
    sender_role: str
    message_text: str
    source_documents: Optional[List[CitationItem]] = []
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class ChatSessionResponse(BaseModel):
    id: int
    session_uuid: str
    search_mode: SearchModeType
    created_at: datetime
    messages: List[ChatMessageResponse] = []
    model_config = ConfigDict(from_attributes=True)

class ChatQueryResponse(BaseModel):
    session_uuid: str
    query: str
    answer: str
    sources: List[CitationItem]
    search_mode: SearchModeType

# Admin Schemas
class SystemStatsResponse(BaseModel):
    total_users: int
    total_documents: int
    personal_documents: int
    public_documents: int
    total_chunks: int
    total_sessions: int
    total_messages: int
    vector_collection_name: str
