from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from .config import settings
from .database import db_manager
from .services.tone_analyzer import tone_analyzer
from .routes import auth, tone_analysis, feedback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Tone Analyzer Backend...")
    
    try:
        # Connect to database
        await db_manager.connect()
        logger.info("Database connected successfully")
        
        # Load tone analysis model
        await tone_analyzer.load_model()
        logger.info("Tone analysis model loaded successfully")
        
        logger.info("Application startup completed")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Tone Analyzer Backend...")
    
    try:
        # Disconnect from database
        await db_manager.disconnect()
        logger.info("Database disconnected successfully")
        
        logger.info("Application shutdown completed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Create FastAPI app
app = FastAPI(
    title="Tone Analyzer API",
    description="A comprehensive API for analyzing text tone and providing improvement suggestions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(tone_analysis.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_connected = db_manager.database is not None
        
        # Check model status
        model_loaded = tone_analyzer.is_loaded
        
        return {
            "status": "healthy" if db_connected and model_loaded else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database_connected": db_connected,
            "model_loaded": model_loaded,
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Tone Analyzer API",
        "version": "1.0.0",
        "description": "A comprehensive API for analyzing text tone and providing improvement suggestions",
        "docs": "/docs",
        "health": "/health",
        "timestamp": datetime.utcnow().isoformat()
    }

# API info endpoint
@app.get("/api/v1/info", tags=["API Info"])
async def api_info():
    """Get API information and available endpoints"""
    return {
        "name": "Tone Analyzer API",
        "version": "1.0.0",
        "description": "A comprehensive API for analyzing text tone and providing improvement suggestions",
        "endpoints": {
            "authentication": {
                "register": "POST /api/v1/auth/register",
                "login": "POST /api/v1/auth/login",
                "me": "GET /api/v1/auth/me",
                "change_password": "POST /api/v1/auth/change-password",
                "deactivate": "DELETE /api/v1/auth/deactivate"
            },
            "tone_analysis": {
                "analyze": "POST /api/v1/tone/analyze",
                "create_message": "POST /api/v1/tone/messages",
                "get_messages": "GET /api/v1/tone/messages",
                "get_message": "GET /api/v1/tone/messages/{message_id}",
                "get_by_tone": "GET /api/v1/tone/messages/tone/{tone}",
                "search": "GET /api/v1/tone/messages/search",
                "delete_message": "DELETE /api/v1/tone/messages/{message_id}",
                "user_stats": "GET /api/v1/tone/stats",
                "supported_tones": "GET /api/v1/tone/supported-tones"
            },
            "feedback": {
                "create": "POST /api/v1/feedback/",
                "get": "GET /api/v1/feedback/{feedback_id}",
                "get_by_message": "GET /api/v1/feedback/message/{message_id}",
                "get_user_feedback": "GET /api/v1/feedback/user/me",
                "update": "PUT /api/v1/feedback/{feedback_id}",
                "delete": "DELETE /api/v1/feedback/{feedback_id}",
                "stats": "GET /api/v1/feedback/stats/overall"
            }
        },
        "supported_tones": settings.SUPPORTED_TONES,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
