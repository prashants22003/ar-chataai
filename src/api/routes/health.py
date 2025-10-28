"""
Health check routes for system monitoring
"""

import os
import psutil
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from api.models import HealthResponse, DetailedHealthResponse
from api.services.supabase_client import SupabaseService
from api.services.file_manager import FileManagerService
from api.services.model_generator import ModelGenerationService
from config import Settings

logger = logging.getLogger(__name__)

router = APIRouter()
settings = Settings()
supabase_service = SupabaseService()
file_manager = FileManagerService()
model_generator = ModelGenerationService()

@router.get("/", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint."""
    return HealthResponse(
        status="ok",
        service="AR-Chataai API Server",
        version="1.0.0"
    )

@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """Detailed health check with system information."""
    try:
        health = DetailedHealthResponse(
            status="ok",
            service="AR-Chataai API Server",
            version="1.0.0",
            dependencies={}
        )
        
        # Check Supabase connection
        try:
            supabase_connected = await supabase_service.test_connection()
            health.dependencies["supabase"] = {
                "status": "connected" if supabase_connected else "disconnected",
                "configured": supabase_service.is_configured()
            }
        except Exception as e:
            health.dependencies["supabase"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Check file system
        try:
            uploads_dir = file_manager.uploads_dir
            health.dependencies["filesystem"] = {
                "status": "ok",
                "uploads_directory": str(uploads_dir),
                "writable": os.access(uploads_dir, os.W_OK)
            }
        except Exception as e:
            health.dependencies["filesystem"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Check model generation service
        try:
            model_status = model_generator.get_model_generation_status()
            health.dependencies["model_generation"] = model_status
        except Exception as e:
            health.dependencies["model_generation"] = {
                "status": "error",
                "error": str(e)
            }
        
        # System information
        memory = psutil.virtual_memory()
        health.system = {
            "memory": {
                "total": f"{memory.total // (1024**3)} GB",
                "available": f"{memory.available // (1024**3)} GB",
                "used": f"{memory.percent}%"
            },
            "cpu": {
                "count": psutil.cpu_count(),
                "usage": f"{psutil.cpu_percent()}%"
            },
            "disk": {
                "total": f"{psutil.disk_usage('/').total // (1024**3)} GB",
                "free": f"{psutil.disk_usage('/').free // (1024**3)} GB",
                "used": f"{psutil.disk_usage('/').percent}%"
            }
        }
        
        # Determine overall status
        has_errors = any(
            dep.get("status") == "error" 
            for dep in health.dependencies.values()
        )
        health.status = "degraded" if has_errors else "ok"
        
        return health
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

@router.get("/supabase")
async def supabase_health():
    """Supabase-specific health check."""
    try:
        stats = await supabase_service.get_storage_stats()
        return stats
    except Exception as e:
        logger.error(f"Supabase health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Supabase health check failed: {str(e)}"
        )

@router.get("/system")
async def system_info():
    """System information endpoint."""
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "memory": {
                "total": f"{memory.total // (1024**3)} GB",
                "available": f"{memory.available // (1024**3)} GB",
                "used_percent": f"{memory.percent}%"
            },
            "cpu": {
                "count": psutil.cpu_count(),
                "usage_percent": f"{psutil.cpu_percent()}%"
            },
            "disk": {
                "total": f"{disk.total // (1024**3)} GB",
                "free": f"{disk.free // (1024**3)} GB",
                "used_percent": f"{disk.percent}%"
            },
            "python": {
                "version": os.sys.version,
                "executable": os.sys.executable
            },
            "uptime": f"{psutil.boot_time()} seconds since boot"
        }
    except Exception as e:
        logger.error(f"System info failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"System info failed: {str(e)}"
        )
