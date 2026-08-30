import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from ..config import settings
from ..database.mongodb import db_manager
from ..models.user import UserCreate, UserRole, UserResponse
from ..utils.errors import AppException, InvalidCredentialsException
from .security import create_access_token, hash_password, verify_password

# In-memory auth storage fallback
_memory_users: Dict[str, dict] = {}
_memory_revoked_tokens: Dict[str, datetime] = {}


def utc_now():
    return datetime.now(timezone.utc)


class AuthService:
    @classmethod
    async def get_user_by_email(cls, email: str) -> Optional[dict]:
        normalized_email = (email or "").strip().lower()
        if not normalized_email:
            return None

        if db_manager.is_connected and db_manager.users is not None:
            return await db_manager.users.find_one({"email": normalized_email})

        return _memory_users.get(normalized_email)

    @classmethod
    async def get_user_by_id(cls, user_id: str) -> Optional[dict]:
        if db_manager.is_connected and db_manager.users is not None:
            return await db_manager.users.find_one({"_id": user_id})

        for user in _memory_users.values():
            if user.get("_id") == user_id:
                return user

        return None

    @staticmethod
    def _normalize_role(role_value: Optional[str]) -> UserRole:
        if not role_value:
            return UserRole.STUDENT

        try:
            return UserRole(role_value)
        except ValueError:
            return UserRole.STUDENT

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

        # Public registration must never create an admin account.
        effective_role = UserRole.STUDENT
        user_id = str(uuid.uuid4())
        hashed_pwd = hash_password(user_in.password)
        now = utc_now()

        user_doc = {
            "_id": user_id,
            "name": user_in.name.strip(),
            "email": email_clean,
            "password_hash": hashed_pwd,
            "role": effective_role.value,
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
            role=effective_role,
            created_at=user_doc["created_at"],
            updated_at=user_doc["updated_at"],
            last_login=None,
        )

    @classmethod
    async def authenticate_user(cls, email: str, password: str) -> dict:
        email_clean = (email or "").strip().lower()
        user = await cls.get_user_by_email(email_clean)

        if not user:
            raise InvalidCredentialsException()

        stored_hash = user.get("password_hash")
        if not verify_password(password, stored_hash or ""):
            raise InvalidCredentialsException()

        role_name = cls._normalize_role(user.get("role")).value
        now = utc_now()

        if db_manager.is_connected and db_manager.users is not None:
            await db_manager.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"last_login": now, "updated_at": now}},
            )
        else:
            user["last_login"] = now
            user["updated_at"] = now

        token = create_access_token(subject=str(user["_id"]), role=role_name)

        user_response = UserResponse(
            id=user["_id"],
            name=user["name"],
            email=user["email"],
            role=cls._normalize_role(user.get("role")),
            created_at=user["created_at"],
            updated_at=user.get("updated_at", user["created_at"]),
            last_login=user.get("last_login"),
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user_response,
        }

    @classmethod
    async def revoke_token(cls, jti: str, expires_at: datetime) -> None:
        if db_manager.is_connected and db_manager.revoked_tokens is not None:
            await db_manager.revoked_tokens.update_one(
                {"_id": jti},
                {"$set": {"expires_at": expires_at}},
                upsert=True,
            )
        else:
            _memory_revoked_tokens[jti] = expires_at

    @classmethod
    async def is_token_revoked(cls, jti: str) -> bool:
        if not jti:
            return False

        if db_manager.is_connected and db_manager.revoked_tokens is not None:
            return await db_manager.revoked_tokens.count_documents({"_id": jti}) > 0

        return jti in _memory_revoked_tokens

    @classmethod
    async def reset_existing_admin_password(cls, email: str, password: str) -> bool:
        """Set or update the password for the existing admin record without creating a new admin user."""
        normalized_email = (email or "").strip().lower()
        if not normalized_email or not password:
            return False

        user = await cls.get_user_by_email(normalized_email)
        if not user:
            return False

        user_role = cls._normalize_role(user.get("role"))
        if user_role != UserRole.ADMIN:
            user["role"] = UserRole.ADMIN.value

        user["password_hash"] = hash_password(password)
        user["updated_at"] = utc_now()

        if db_manager.is_connected and db_manager.users is not None:
            await db_manager.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"role": UserRole.ADMIN.value, "password_hash": user["password_hash"], "updated_at": user["updated_at"]}},
            )
            return True

        _memory_users[normalized_email] = user
        return True

    @classmethod
    async def apply_initial_admin_password_if_configured(cls) -> bool:
        password = settings.ADMIN_INITIAL_PASSWORD
        if not password:
            return False

        return await cls.reset_existing_admin_password(settings.ADMIN_EMAIL, password)


auth_service = AuthService()
