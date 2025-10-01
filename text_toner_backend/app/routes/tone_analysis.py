from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from ..models import ToneAnalysisRequest, ToneAnalysisResponse
from ..services.tone_analyzer import tone_analyzer
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tone", tags=["Tone Analysis"])

@router.post("/analyze-tone", response_model=ToneAnalysisResponse)
async def analyze_tone(request: ToneAnalysisRequest):
    """
    Analyze the tone of input text and provide improved version
    
    Input:
    {
        "text": "<user_input_text>",
        "target_tone": "<optional_desired_tone>"
    }
    
    Output:
    {
        "original_text": "<user_input_text>",
        "detected_tone": "<general_tone>",
        "improvised_text": "<text_with_improved_tone>"
    }
    """
    try:
        logger.info(f"Analyzing tone for text: {request.text[:100]}...")
        
        # Validate target tone if provided
        if request.target_tone and request.target_tone not in ["positive", "negative", "neutral", "professional", "friendly", "formal"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid target tone. Must be one of: positive, negative, neutral, professional, friendly, formal"
            )
        
        # Analyze tone and improve text
        result = await tone_analyzer.analyze_tone(request.text, request.target_tone)
        
        logger.info(f"Analysis completed. Detected tone: {result['detected_tone']}")
        
        return ToneAnalysisResponse(
            original_text=result["original_text"],
            detected_tone=result["detected_tone"],
            improvised_text=result["improvised_text"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze tone: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze tone: {str(e)}"
        )

@router.get("/supported-tones")
async def get_supported_tones():
    """Get list of supported tone types"""
    from ..config import settings
    
    return {
        "supported_tones": settings.SUPPORTED_TONES,
        "target_tones": settings.TARGET_TONES,
        "description": "Available tone types for analysis and improvement"
    }