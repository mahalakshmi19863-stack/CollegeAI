import uuid
from datetime import datetime, timezone
from typing import Dict, Optional
from ..database.mongodb import db_manager
from ..models.user import UserCreate, UserInDB, UserResponse, UserRole
from ..utils.errors import AppException, InvalidCredentialsException
from .security import hash_password, verify_password, create_access_token

# In-memory store fallback when MongoDB is not connected
_memory_users: Dict[str, dict] = {}
_memory_revoked_tokens: Dict[str, datetime] = {}


def utc_now():
    return datetime.now(timezone.utc)


class AuthService:
    @staticmethod
    async def revoke_token(jti: str, expires_at: datetime) -> None:
        if db_manager.is_connected and db_manager.revoked_tokens is not None:
            await db_manager.revoked_tokens.update_one(
                {"jti": jti},
                {"$set": {"jti": jti, "expires_at": expires_at}},
                upsert=True,
            )
        else:
            _memory_revoked_tokens[jti] = expires_at

    @staticmethod
    async def is_token_revoked(jti: str) -> bool:
        if not jti:
            return False

        if db_manager.is_connected and db_manager.revoked_tokens is not None:
            return await db_manager.revoked_tokens.find_one({"jti": jti}) is not None

        expires_at = _memory_revoked_tokens.get(jti)
        if expires_at and expires_at <= utc_now():
            _memory_revoked_tokens.pop(jti, None)
            return False
        return expires_at is not None

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[dict]:
        email_clean = email.strip().lower()
        if db_manager.is_connected and db_manager.users is not None:
            user = await db_manager.users.find_one({"email": email_clean})
            return user
        return _memory_users.get(email_clean)

    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[dict]:
        if db_manager.is_connected and db_manager.users is not None:
            user = await db_manager.users.find_one({"_id": user_id})
            return user
        for user in _memory_users.values():
            if user["_id"] == user_id:
                return user
        return None

    @classmethod
    async def register_user(cls, user_in: UserCreate) -> UserResponse:
        email_clean = user_in.email.strip().lower()
        existing = await cls.get_user_by_email(email_clean)
        if existing:
            raise AppException(
                code="EMAIL_ALREADY_REGISTERED",
                message="An account with this email already exists.",
                status_code=400,
            )

        user_id = str(uuid.uuid4())
        hashed_pwd = hash_password(user_in.password)
        now = utc_now()

        user_doc = {
            "_id": user_id,
            "name": user_in.name.strip(),
            "email": email_clean,
            "password_hash": hashed_pwd,
            "role": UserRole.STUDENT.value,
            "created_at": now,
            "updated_at": now,
            "last_login": None,
        }

        if db_manager.is_connected and db_manager.users is not None:
            await db_manager.users.insert_one(user_doc)
        else:
            _memory_users[email_clean] = user_doc

        return UserResponse(
            id=user_id,
            name=user_doc["name"],
            email=user_doc["email"],
            role=UserRole(user_doc["role"]),
            created_at=user_doc["created_at"],
            updated_at=user_doc["updated_at"],
            last_login=None,
        )

    @classmethod
    async def authenticate_user(cls, email: str, password: str) -> dict:
        email_clean = email.strip().lower()
        user = await cls.get_user_by_email(email_clean)
        if not user:
            raise InvalidCredentialsException()

        if not verify_password(password, user["password_hash"]):
            raise InvalidCredentialsException()

        now = utc_now()
        if db_manager.is_connected and db_manager.users is not None:
            await db_manager.users.update_one(
                {"_id": user["_id"]}, {"$set": {"last_login": now}}
            )
        else:
            user["last_login"] = now

        user_response = UserResponse(
            id=user["_id"],
            name=user["name"],
            email=user["email"],
            role=UserRole(user["role"]),
            created_at=user["created_at"],
            updated_at=user.get("updated_at", user["created_at"]),
            last_login=now,
        )

        token = create_access_token(
            subject=user["_id"],
            role=user["role"],
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user_response,
        }


auth_service = AuthService()
