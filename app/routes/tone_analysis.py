from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from ..models import (
    ToneAnalysisRequest, ToneAnalysisResponse, MessageCreate, 
    MessageResponse, UserStatsResponse, UserInDB
)
from ..services.tone_analyzer import tone_analyzer
from ..services.message_service import message_service
from ..routes.auth import get_current_user

router = APIRouter(prefix="/tone", tags=["Tone Analysis"])

@router.post("/analyze", response_model=ToneAnalysisResponse)
async def analyze_tone(request: ToneAnalysisRequest):
    """Analyze the tone of input text"""
    try:
        analysis = await tone_analyzer.analyze_tone(request.text)
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze tone: {str(e)}"
        )

@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    message_data: MessageCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Create a new message with tone analysis"""
    try:
        # Set user_id from authenticated user
        message_data.user_id = current_user.id
        
        message = await message_service.create_message(message_data)
        return message
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create message: {str(e)}"
        )

@router.get("/messages", response_model=List[MessageResponse])
async def get_user_messages(
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get messages for the current user"""
    try:
        messages = await message_service.get_user_messages(
            current_user.id, limit=limit, skip=skip
        )
        return messages
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get messages: {str(e)}"
        )

@router.get("/messages/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get a specific message by ID"""
    try:
        message = await message_service.get_message(message_id)
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Check if user owns the message
        if message.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return message
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get message: {str(e)}"
        )

@router.get("/messages/tone/{tone}", response_model=List[MessageResponse])
async def get_messages_by_tone(
    tone: str,
    limit: int = Query(50, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get messages filtered by tone"""
    try:
        messages = await message_service.get_messages_by_tone(tone, limit=limit)
        
        # Filter to only show user's messages
        user_messages = [msg for msg in messages if msg.user_id == current_user.id]
        
        return user_messages
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get messages by tone: {str(e)}"
        )

@router.get("/messages/search", response_model=List[MessageResponse])
async def search_messages(
    query: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=50),
    current_user: UserInDB = Depends(get_current_user)
):
    """Search messages by text content"""
    try:
        messages = await message_service.search_messages(
            current_user.id, query, limit=limit
        )
        return messages
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search messages: {str(e)}"
        )

@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Delete a message"""
    try:
        success = await message_service.delete_message(message_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found or access denied"
            )
        
        return {"message": "Message deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete message: {str(e)}"
        )

@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(current_user: UserInDB = Depends(get_current_user)):
    """Get user statistics"""
    try:
        stats = await message_service.get_user_stats(current_user.id)
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user stats: {str(e)}"
        )

@router.get("/supported-tones")
async def get_supported_tones():
    """Get list of supported tone types"""
    from ..config import settings
    
    return {
        "supported_tones": settings.SUPPORTED_TONES,
        "description": "Available tone types for analysis"
    }
