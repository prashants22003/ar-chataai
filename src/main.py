"""
AR-Chataai Unified Backend
Complete Python backend for 3D model generation and AR viewing
"""

import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AR-Chataai Backend",
    description="Unified backend for 3D carpet model generation and AR viewing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import API components
from api.routes import upload, ar_viewer, health
from api.services.supabase_client import SupabaseService
from api.services.file_manager import FileManagerService
from api.services.model_generator import ModelGenerationService
from config import Settings

# Initialize services
settings = Settings()
supabase_service = SupabaseService()
file_manager = FileManagerService()
model_generator = ModelGenerationService()

# Mount static files for AR viewer
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Include routers
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(ar_viewer.router, prefix="/api/ar-viewer", tags=["ar-viewer"])
app.include_router(health.router, prefix="/api/health", tags=["health"])

@app.get("/")
async def root():
    """Root endpoint with backend information."""
    return {
        "name": "AR-Chataai Backend",
        "version": "1.0.0",
        "description": "Unified backend for 3D model generation and AR viewing",
        "components": {
            "api_server": "FastAPI web server",
            "model_generation": "3D model generation pipeline",
            "supabase_integration": "File storage and hosting",
            "ar_viewer": "Web-based AR experience"
        },
        "endpoints": {
            "upload": "/api/upload",
            "ar_viewer": "/api/ar-viewer",
            "health": "/api/health",
            "docs": "/docs"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting AR-Chataai Unified Backend...")
    logger.info("=" * 60)
    
    # Ensure uploads directory exists
    file_manager.ensure_uploads_dir()
    
    # Test Supabase connection
    if supabase_service.is_configured():
        try:
            is_connected = await supabase_service.test_connection()
            if is_connected:
                logger.info("✅ Supabase connection successful")
            else:
                logger.warning("⚠️ Supabase connection failed")
        except Exception as e:
            logger.error(f"❌ Supabase connection error: {e}")
    else:
        logger.warning("⚠️ Supabase not configured - set PROJECT_URL and API_KEY environment variables")
    
    # Test model generation service
    try:
        model_status = model_generator.get_model_generation_status()
        logger.info("✅ Model generation service ready")
        logger.info(f"   Python path: {model_status.get('python_path', 'Unknown')}")
    except Exception as e:
        logger.error(f"❌ Model generation service error: {e}")
    
    logger.info("=" * 60)
    logger.info("🚀 AR-Chataai Backend started successfully! (Updated)")
    logger.info(f"📍 API Server: http://localhost:{settings.port}")
    logger.info(f"📚 API Documentation: http://localhost:{settings.port}/docs")
    logger.info(f"🔍 Health Check: http://localhost:{settings.port}/api/health")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down AR-Chataai Backend...")
    # Cleanup any temporary files
    file_manager.cleanup_old_files()

if __name__ == "__main__":
    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
