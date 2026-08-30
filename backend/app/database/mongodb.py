import logging
import asyncio
import re
from typing import Optional
from urllib.parse import urlparse, urlunparse
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
from ..config import settings

logger = logging.getLogger("college_ai.database")


def redact_mongodb_uri(uri: str) -> str:
    """Mask credentials in MongoDB connection strings before logging or surfacing errors."""
    if not uri:
        return ""

    try:
        parsed = urlparse(uri)
    except Exception:
        return "***redacted***"

    if parsed.scheme.startswith("mongodb") and parsed.hostname:
        username = parsed.username
        password = parsed.password
        if username or password:
            netloc = parsed.hostname
            if parsed.port:
                netloc = f"{netloc}:{parsed.port}"
            netloc = f"***:***@{netloc}"
            parsed = parsed._replace(netloc=netloc)
            return urlunparse(parsed)

    redacted = re.sub(r"(?<=://)[^@/]+(?=@)", "***", uri)
    if redacted != uri:
        return redacted

    return uri


class DatabaseManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    is_connected: bool = False

    async def connect_to_database(self):
        """Establish connection to MongoDB Atlas in production, or a local MongoDB instance for development."""
        redacted_uri = redact_mongodb_uri(settings.MONGODB_URI)
        logger.info(
            "Connecting to MongoDB: %s (database=%s)",
            redacted_uri,
            settings.MONGODB_DATABASE,
        )
        try:
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
            )
            # Verify connection
            await self.client.admin.command("ping")
            self.db = self.client[settings.MONGODB_DATABASE]
            self.is_connected = True
            logger.info(
                "Successfully connected to MongoDB database '%s'.",
                settings.MONGODB_DATABASE,
            )
            await self.init_indexes()
        except Exception as e:
            self.is_connected = False
            logger.warning(
                "MongoDB connection failed: %s. Falling back to in-memory/offline mode for local development.",
                redact_mongodb_uri(str(e)),
            )
            if not settings.MONGODB_USE_LOCAL_FALLBACK:
                logger.error(
                    "Local fallback is disabled; MongoDB connectivity is required for this environment."
                )

    async def close_database_connection(self):
        """Close MongoDB connection gracefully."""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("MongoDB connection closed.")

    async def init_indexes(self):
        """Create necessary database indexes for fast query performance."""
        if not self.is_connected or self.db is None:
            return

        try:
            # Users collection indexes
            await self.db.users.create_index("email", unique=True)
            await self.db.users.create_index("role")

            # Documents collection indexes
            await self.db.documents.create_index("status")
            await self.db.documents.create_index("category")
            await self.db.documents.create_index("is_active")
            await self.db.documents.create_index("created_at")

            # Document Chunks collection indexes
            await self.db.document_chunks.create_index("document_id")
            await self.db.document_chunks.create_index("category")
            await self.db.document_chunks.create_index("is_active")

            # Conversations collection indexes
            await self.db.conversations.create_index("user_id")
            await self.db.conversations.create_index("updated_at")

            # Messages collection indexes
            await self.db.messages.create_index("conversation_id")
            await self.db.messages.create_index("user_id")

            # Feedback collection indexes
            await self.db.feedback.create_index("message_id")
            await self.db.feedback.create_index("user_id")

            # Revoked JWT identifiers, with expiry for automatic cleanup
            await self.db.revoked_tokens.create_index("jti", unique=True)
            await self.db.revoked_tokens.create_index(
                "expires_at", expireAfterSeconds=0
            )

            logger.info("MongoDB indexes verified and initialized.")
        except Exception as e:
            logger.error(f"Error initializing indexes: {e}")

    # Helper getters for collections
    @property
    def users(self):
        return self.db.users if self.db is not None else None

    @property
    def documents(self):
        return self.db.documents if self.db is not None else None

    @property
    def document_chunks(self):
        return self.db.document_chunks if self.db is not None else None

    @property
    def conversations(self):
        return self.db.conversations if self.db is not None else None

    @property
    def messages(self):
        return self.db.messages if self.db is not None else None

    @property
    def feedback(self):
        return self.db.feedback if self.db is not None else None

    @property
    def revoked_tokens(self):
        return self.db.revoked_tokens if self.db is not None else None


db_manager = DatabaseManager()


async def get_database() -> Optional[AsyncIOMotorDatabase]:
    return db_manager.db
