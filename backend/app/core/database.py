from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from backend.app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    from backend.app.models.models import User, UserRole
    from backend.app.core.security import get_password_hash

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Create required performance indexes per Review-II Section 3.3
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_docs_owner_vis ON documents(owner_id, visibility);"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_messages_session ON chat_messages(session_id, timestamp);"))

    # Seed initial Administrator and Default User if table is empty
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        if count == 0:
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
