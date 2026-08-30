from fastapi import APIRouter, Depends
from ..auth.dependencies import require_admin
from ..models.user import UserResponse
from ..utils.responses import ApiResponse, success_response
from .service import admin_service

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=ApiResponse[dict])
async def get_admin_dashboard(
    current_user: UserResponse = Depends(require_admin),
):
    """Retrieve administrative overview dashboard stats (Admin only)."""
    data = await admin_service.get_dashboard_metrics()
    return success_response(data)


@router.get("/analytics", response_model=ApiResponse[dict])
async def get_admin_analytics(
    current_user: UserResponse = Depends(require_admin),
):
    """Retrieve knowledge base and usage analytics (Admin only)."""
    data = await admin_service.get_analytics()
    return success_response(data)
