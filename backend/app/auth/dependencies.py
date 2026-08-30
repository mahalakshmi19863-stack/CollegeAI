from typing import Optional
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..models.user import UserResponse, UserRole
from ..utils.errors import ForbiddenException, UnauthorizedException
from .security import decode_access_token
from .service import auth_service

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> UserResponse:
    """Validate JWT token and return current authenticated user."""
    if not credentials or not credentials.credentials:
        raise UnauthorizedException("Authorization token is missing")

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedException("Invalid or expired token")

    if await auth_service.is_token_revoked(payload.get("jti", "")):
        raise UnauthorizedException("Token has been revoked")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")

    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise UnauthorizedException("User no longer exists")

    return UserResponse(
        id=user["_id"],
        name=user["name"],
        email=user["email"],
        role=UserRole(user["role"]),
        created_at=user["created_at"],
        updated_at=user.get("updated_at", user["created_at"]),
        last_login=user.get("last_login"),
    )


def require_role(required_role: UserRole):
    """Dependency factory enforcing specific user role."""
    async def role_checker(
        current_user: UserResponse = Depends(get_current_user),
    ) -> UserResponse:
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise ForbiddenException(
                f"Access requires {required_role.value} privileges."
            )
        return current_user

    return role_checker


async def require_admin(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """Shortcut dependency for requiring ADMIN role."""
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException("Administrator privileges required.")
    return current_user
