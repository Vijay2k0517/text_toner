from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from ..models import (
    FeedbackCreate, FeedbackResponse, UserInDB
)
from ..services.feedback_service import feedback_service
from ..routes.auth import get_current_user

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback_data: FeedbackCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Create new feedback for a message"""
    try:
        # Set user_id from authenticated user
        feedback_data.user_id = current_user.id
        
        feedback = await feedback_service.create_feedback(feedback_data)
        return feedback
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create feedback: {str(e)}"
        )

@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
    feedback_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get a specific feedback by ID"""
    try:
        feedback = await feedback_service.get_feedback(feedback_id)
        
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        
        # Check if user owns the feedback
        if feedback.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return feedback
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feedback: {str(e)}"
        )

@router.get("/message/{message_id}", response_model=List[FeedbackResponse])
async def get_feedback_by_message(
    message_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get all feedback for a specific message"""
    try:
        feedback_list = await feedback_service.get_feedback_by_message(message_id)
        
        # Filter to only show user's feedback
        user_feedback = [fb for fb in feedback_list if fb.user_id == current_user.id]
        
        return user_feedback
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feedback by message: {str(e)}"
        )

@router.get("/user/me", response_model=List[FeedbackResponse])
async def get_user_feedback(
    limit: int = Query(50, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get feedback submitted by the current user"""
    try:
        feedback_list = await feedback_service.get_user_feedback(
            current_user.id, limit=limit
        )
        return feedback_list
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user feedback: {str(e)}"
        )

@router.put("/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback(
    feedback_id: str,
    update_data: dict,
    current_user: UserInDB = Depends(get_current_user)
):
    """Update feedback (only by the owner)"""
    try:
        feedback = await feedback_service.update_feedback(
            feedback_id, current_user.id, update_data
        )
        
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found or access denied"
            )
        
        return feedback
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update feedback: {str(e)}"
        )

@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Delete feedback (only by the owner)"""
    try:
        success = await feedback_service.delete_feedback(feedback_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found or access denied"
            )
        
        return {"message": "Feedback deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete feedback: {str(e)}"
        )

@router.get("/stats/overall")
async def get_feedback_stats():
    """Get overall feedback statistics (public endpoint)"""
    try:
        stats = await feedback_service.get_feedback_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feedback stats: {str(e)}"
        )
