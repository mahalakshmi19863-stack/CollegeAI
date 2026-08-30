import os
import secrets
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "CollegeAI"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = Field(default=8002)

    # MongoDB settings
    MONGODB_URI: str = Field(
        default_factory=lambda: os.getenv(
            "MONGODB_URI", "mongodb://localhost:27017"
        ),
        description="MongoDB Atlas production URI or local MongoDB URL for development",
    )
    MONGODB_DATABASE: str = Field(
        default_factory=lambda: os.getenv("MONGODB_DATABASE", "college_ai"),
        description="MongoDB database name",
    )
    MONGODB_USE_LOCAL_FALLBACK: bool = Field(
        default=True,
        description="Keep the in-memory fallback active when Atlas or local MongoDB is unavailable",
    )

    ADMIN_EMAIL: str = Field(
        default="phase5.live.e28f8a94d7@college.edu",
        description="Canonical admin email used for the existing CollegeAI administrator account.",
    )
    ADMIN_INITIAL_PASSWORD: Optional[str] = Field(
        default=None,
        description="Optional one-time reset password for the existing admin account. Never commit this value; set it in Render/Env only.",
    )

    # JWT Authentication
    JWT_SECRET: str = Field(
        default_factory=lambda: os.getenv("JWT_SECRET") or secrets.token_urlsafe(32),
        description="Secret key for signing JWT tokens",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # LLM Provider Configuration
    LLM_PROVIDER: str = Field(
        default="GEMINI", description="LLM provider: GEMINI, OPENAI, MOCK"
    )
    GEMINI_API_KEY: Optional[str] = Field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY"),
        description="Gemini API key for production generation and embeddings",
    )
    LLM_API_KEY: Optional[str] = Field(
        default_factory=lambda: os.getenv("LLM_API_KEY") or os.getenv("GEMINI_API_KEY"),
        description="API Key for the LLM Provider",
    )
    LLM_MODEL: str = Field(
        default="gemini-3.6-flash", description="Model name for generation"
    )

    # Embedding Provider Configuration
    EMBEDDING_PROVIDER: str = Field(
        default="GEMINI", description="Embedding provider: GEMINI, OPENAI, LOCAL"
    )
    EMBEDDING_API_KEY: Optional[str] = Field(
        default_factory=lambda: os.getenv("EMBEDDING_API_KEY") or os.getenv("GEMINI_API_KEY"),
        description="API key for embedding generation",
    )
    EMBEDDING_MODEL: str = Field(
        default="gemini-embedding-001", description="Embedding model name"
    )
    EMBEDDING_DIMENSION: int = 768

    # RAG Settings
    TOP_K: int = 5
    RELEVANCE_THRESHOLD: float = 0.20
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 120
    MAX_FILE_SIZE_MB: int = 20
    PROCESSING_STALE_MINUTES: int = 30

    # CORS Configuration
    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="Allowed frontend origin for CORS",
    )
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
        "https://*.vercel.app",
    ]

    # Uploads Storage
    UPLOAD_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads"
    )
    STORAGE_PROVIDER: str = "local"
    STORAGE_PATH: str = Field(
        default_factory=lambda: os.path.abspath(
            os.getenv("STORAGE_PATH", "./storage")
        ),
        description="Persistent local storage root for uploaded source files",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()

# Ensure uploads folder exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
