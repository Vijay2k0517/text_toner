from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ToneType(str, Enum):
    SAD = "sad"
    ANGRY = "angry"
    FRIENDLY = "friendly"

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: str
    created_at: datetime
    is_active: bool = True

class UserInDB(UserResponse):
    hashed_password: str

class ToneAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)

class ToneAnalysisResponse(BaseModel):
    tone: str
    improved_text: str

class MessageCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    user_id: str
    context: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    text: str
    user_id: str
    tone_analysis: ToneAnalysisResponse
    created_at: datetime
    updated_at: datetime

class FeedbackCreate(BaseModel):
    message_id: str
    user_id: str
    tone_accuracy: int = Field(..., ge=1, le=5)  # 1-5 scale
    suggestion_helpfulness: int = Field(..., ge=1, le=5)  # 1-5 scale
    comments: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: str
    message_id: str
    user_id: str
    tone_accuracy: int
    suggestion_helpfulness: int
    comments: Optional[str]
    created_at: datetime

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    database_connected: bool
    model_loaded: bool

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(UserCreate):
    confirm_password: str

class UserStatsResponse(BaseModel):
    total_messages: int
    most_common_tone: Optional[str] = None
    average_confidence: float
    messages_this_week: int
    favorite_suggestions: List[str]
