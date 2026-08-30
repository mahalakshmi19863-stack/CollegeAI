from fastapi import APIRouter, Depends
from ..auth.dependencies import get_current_user
from ..models.feedback import FeedbackCreate, FeedbackResponse
from ..models.user import UserResponse
from ..utils.responses import ApiResponse, success_response
from .service import _memory_feedback, feedback_service

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.post("", response_model=ApiResponse[FeedbackResponse])
async def submit_feedback(
    feedback_in: FeedbackCreate,
    current_user: UserResponse = Depends(get_current_user),
):
    """Submit student feedback on assistant response."""
    response = await feedback_service.submit(feedback_in, current_user)
    return success_response(response)
