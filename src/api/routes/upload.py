"""
Upload routes for file handling and model generation
"""

import os
import logging
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional

from api.models import DimensionsModel, UploadResponse, ErrorResponse
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

@router.post("/generate-ar-link", response_model=UploadResponse)
async def generate_model_with_ar_link(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(..., description="Carpet image file"),
    length: float = Form(..., ge=0.5, le=10.0, description="Length in meters"),
    width: float = Form(..., ge=0.5, le=10.0, description="Width in meters"),
    thickness: float = Form(..., ge=1.0, le=20.0, description="Thickness in millimeters"),
    skip_perspective: bool = Form(True, description="Skip perspective correction")
):
    """
    Generate 3D model from uploaded image and create AR viewer link.
    """
    try:
        # Validate file type
        if not file_manager.validate_file_type(image.filename):
            raise HTTPException(
                status_code=400,
                detail="Only JPG, PNG, and JPEG images are allowed"
            )
        
        # Check file size
        if image.size > settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {settings.max_file_size // (1024*1024)}MB"
            )
        
        # Create dimensions model
        dimensions = DimensionsModel(
            length=length,
            width=width,
            thickness=thickness
        )
        
        logger.info(f"Processing image: {image.filename}")
        logger.info(f"Dimensions: {dimensions.length}m x {dimensions.width}m x {dimensions.thickness}mm")
        
        # Generate unique filename for the processed model
        glb_filename = file_manager.generate_unique_filename(f"{Path(image.filename).stem}.glb")
        
        # Save uploaded image temporarily
        image_content = await image.read()
        temp_image_path = file_manager.save_uploaded_file(image_content, image.filename)
        
        try:
            # Generate 3D model
            generation_result = await model_generator.generate_model_from_image(
                temp_image_path,
                dimensions,
                glb_filename,
                skip_perspective
            )
            
            if not generation_result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail=f"Model generation failed: {generation_result['error']}"
                )
            
            # Upload generated GLB to Supabase
            with open(generation_result["glb_path"], "rb") as f:
                glb_data = f.read()
            
            upload_result = await supabase_service.upload_file(glb_filename, glb_data)
            
            if not upload_result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload model: {upload_result['error']}"
                )
            
            # Generate AR viewer link
            ar_viewer_link = f"/api/ar-viewer?model_url={upload_result['public_url']}"
            
            # Schedule cleanup of temporary files
            background_tasks.add_task(
                file_manager.cleanup_file,
                temp_image_path
            )
            background_tasks.add_task(
                model_generator.cleanup_generated_files,
                generation_result["glb_path"],
                generation_result["usdz_path"]
            )
            
            logger.info(f"Model generation successful: {glb_filename}")
            logger.info(f"Public URL: {upload_result['public_url']}")
            logger.info(f"AR Viewer Link: {ar_viewer_link}")
            
            return UploadResponse(
                filename=glb_filename,
                public_url=upload_result["public_url"],
                ar_viewer_link=ar_viewer_link,
                size=len(glb_data),
                dimensions=dimensions,
                message="3D model generated and AR link created successfully!"
            )
            
        except Exception as e:
            # Clean up temporary image file on error
            file_manager.cleanup_file(temp_image_path)
            raise e
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/stats")
async def get_upload_stats():
    """Get upload statistics."""
    try:
        stats = await supabase_service.get_storage_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get upload stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get upload stats: {str(e)}"
        )
