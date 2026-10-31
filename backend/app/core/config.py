import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Explicitly load local .env with override=True so workspace configuration takes precedence
# over stale/invalid system-level environment variables
env_file_path = BASE_DIR / ".env"
if env_file_path.exists():
    load_dotenv(dotenv_path=env_file_path, override=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Intelligent Document Management and Question Answering System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Storage paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    CHROMA_PERSIST_DIR: Path = BASE_DIR / "data" / "chroma_data"
    DATABASE_PATH: Path = BASE_DIR / "data" / "metadata.db"
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'metadata.db'}"
    
    # Ingestion Constraints
    MAX_FILE_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB limit
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".txt"}
    
    # Text Chunking parameters (IEEE / SDD specs: 800 char window, 150 char overlap)
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150
    
    # Vector Database
    CHROMA_COLLECTION_NAME: str = "enterprise_knowledge_base"
    VECTOR_DIMENSION: int = 1536
    
    # OpenAI & Cognitive Layer
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "gpt-4o"
    
    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "rag-dms-enterprise-secure-secret-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    model_config = {"env_file": ".env", "extra": "allow"}

settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
