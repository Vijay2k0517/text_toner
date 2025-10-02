import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # MongoDB Configuration
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "tone_analyzer_db")
    
    # Hugging Face Model Configuration
    # Using FLAN-T5 XL for better text generation and tone analysis
    HUGGINGFACE_MODEL: str = os.getenv("HUGGINGFACE_MODEL", "google/flan-t5-xl")
    HUGGINGFACE_TOKEN: str = os.getenv("HUGGINGFACE_TOKEN", "")
    
    # Alternative model options (uncomment to use)
    # HUGGINGFACE_MODEL: str = os.getenv("HUGGINGFACE_MODEL", "EleutherAI/gpt-neo-1.3B")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8081",
        "http://localhost:19006",  # React Native Expo
        "http://localhost:19000",  # React Native Expo
    ]
    
    # Tone Analysis Configuration - Updated to emotional tones
    SUPPORTED_TONES = ["sad", "angry", "friendly"]
    
    # Model Configuration
    MAX_TEXT_LENGTH: int = 512
    CONFIDENCE_THRESHOLD: float = 0.3

settings = Settings()
