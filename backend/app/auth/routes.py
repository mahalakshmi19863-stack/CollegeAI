from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from ..models.user import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from ..utils.responses import ApiResponse, success_response
from .dependencies import get_current_user, security_scheme
from .security import decode_access_token
from .service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=ApiResponse[UserResponse])
async def register(user_in: UserCreate):
    """Register a new student or admin account."""
    user = await auth_service.register_user(user_in)
    return success_response(user)


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(credentials: UserLogin):
    """Authenticate user with email/password and receive JWT token."""
    auth_data = await auth_service.authenticate_user(
        credentials.email, credentials.password
    )
    return success_response(auth_data)


@router.post("/logout", response_model=ApiResponse[dict])
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    current_user: UserResponse = Depends(get_current_user),
):
    """Revoke the current JWT so it cannot be reused after logout."""
    payload = decode_access_token(credentials.credentials)
    if payload and payload.get("jti") and payload.get("exp"):
        from datetime import datetime, timezone

        await auth_service.revoke_token(
            payload["jti"], datetime.fromtimestamp(payload["exp"], timezone.utc)
        )
    return success_response({"message": "Successfully logged out"})


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """Retrieve profile of the currently logged-in user."""
    return success_response(current_user)
