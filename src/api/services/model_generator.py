"""
Model generation service
Direct Python integration for 3D model generation
"""

import os
import sys
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from config import Settings
from api.models import DimensionsModel

logger = logging.getLogger(__name__)

class ModelGenerationService:
    """Service for generating 3D models from images."""
    
    def __init__(self):
        """Initialize model generation service."""
        self.settings = Settings()
        
        # Add model_generation to path
        src_path = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(src_path))
    
    async def generate_model_from_image(
        self,
        image_path: str,
        dimensions: DimensionsModel,
        output_filename: str,
        skip_perspective: bool = True
    ) -> Dict[str, Any]:
        """
        Generate 3D model from image using Python model generation.
        
        Args:
            image_path: Path to uploaded image
            dimensions: Model dimensions
            output_filename: Output GLB filename
            skip_perspective: Whether to skip perspective correction
            
        Returns:
            Dict with success status and GLB path
        """
        try:
            logger.info("Starting Python model generation...")
            logger.info(f"Image: {image_path}")
            logger.info(f"Dimensions: {dimensions.length}m x {dimensions.width}m x {dimensions.thickness}mm")
            logger.info(f"Skip perspective: {skip_perspective}")
            
            # Import model generation
            from model_generation.main import process_carpet
            
            # Prepare dimensions dict
            dimensions_dict = {
                'length': dimensions.length,
                'width': dimensions.width,
                'thickness': dimensions.thickness
            }
            
            # Run model generation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            glb_path, usdz_path = await loop.run_in_executor(
                None,
                self._run_model_generation,
                image_path,
                dimensions_dict,
                output_filename,
                skip_perspective
            )
            
            # Check if GLB file was created
            if os.path.exists(glb_path):
                logger.info(f"Model generation successful: {glb_path}")
                return {
                    "success": True,
                    "glb_path": glb_path,
                    "usdz_path": usdz_path,
                    "filename": output_filename
                }
            else:
                raise Exception("GLB file was not generated")
                
        except Exception as e:
            logger.error(f"Model generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _run_model_generation(
        self,
        image_path: str,
        dimensions: Dict[str, float],
        output_filename: str,
        skip_perspective: bool
    ) -> tuple:
        """Run model generation in executor."""
        from model_generation.main import process_carpet
        from pathlib import Path
        
        output_name = Path(output_filename).stem
        
        return process_carpet(
            image_path,
            output_name=output_name,
            dimensions=dimensions,
            skip_perspective=skip_perspective
        )
    
    async def cleanup_generated_files(self, glb_path: str, usdz_path: str):
        """Clean up generated files after upload."""
        try:
            if os.path.exists(glb_path):
                os.unlink(glb_path)
                logger.info(f"Cleaned up GLB: {glb_path}")
            
            if os.path.exists(usdz_path):
                os.unlink(usdz_path)
                logger.info(f"Cleaned up USDZ: {usdz_path}")
                
        except Exception as e:
            logger.error(f"Failed to cleanup generated files: {e}")
    
    def get_model_generation_status(self) -> Dict[str, Any]:
        """Get model generation service status."""
        return {
            "service": "Model Generation Service",
            "status": "ready",
            "python_path": sys.executable,
            "model_generation_path": str(Path(__file__).parent.parent.parent / "model_generation")
        }
