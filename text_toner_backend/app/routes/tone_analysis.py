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
        "text": "<user_input_text>"
    }
    
    Output:
    {
        "tone": "<detected_tone>",
        "improved_text": "<text_with_improved_grammar_and_flow>"
    }
    """
    try:
        logger.info(f"Analyzing tone for text: {request.text[:100]}...")
        
        # Analyze tone and improve text
        result = await tone_analyzer.analyze_tone(request.text)
        
        logger.info(f"Analysis completed. Detected tone: {result['tone']}")
        
        return ToneAnalysisResponse(
            tone=result["tone"],
            improved_text=result["improved_text"]
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
        "description": "Available tone types for analysis: sad, angry, friendly"
    }