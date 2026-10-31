import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from backend.app.core.database import Base, get_db
from backend.app.core.config import settings
from backend.app.models.models import User, UserRole
from backend.app.core.security import get_password_hash
from backend.app.services.chroma_service import chroma_service
from backend.app.main import app

TEST_DB_URL = "sqlite+aiosqlite:///./data/test_metadata.db"

@pytest_asyncio.fixture(scope="function")
async def client():
    engine = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_docs_owner_vis ON documents(owner_id, visibility);"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_messages_session ON chat_messages(session_id, timestamp);"))

    async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    # Seed default test users
    async with async_session() as session:
        admin_user = User(
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            full_name="System Administrator",
            role=UserRole.ADMIN
        )
        standard_user = User(
            email="user@example.com",
            password_hash=get_password_hash("user123"),
            full_name="Standard Research User",
            role=UserRole.USER
        )
        session.add_all([admin_user, standard_user])
        await session.commit()
    
    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

    # Reset vector store collection between tests for complete test isolation
    try:
        chroma_service.client.delete_collection(settings.CHROMA_COLLECTION_NAME)
        chroma_service.collection = chroma_service.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    except Exception:
        pass
