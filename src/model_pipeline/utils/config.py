"""
Configuration settings for the carpet 3D model generation pipeline.

All adjustable parameters are centralized here for easy maintenance.
"""

import os
from pathlib import Path


class Config:
    """Centralized configuration for carpet model generation."""
    
    # Base directories
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    OUTPUT_DIR = BASE_DIR / "output"
    STATIC_DIR = OUTPUT_DIR / "static"
    
    # Input/Output directories
    UPLOADS_DIR = STATIC_DIR / "uploads"
    TEXTURES_DIR = STATIC_DIR / "textures"
    
    # Organized output directories
    CORRECTED_DIR = STATIC_DIR / "corrected"
    BASECOLOR_DIR = STATIC_DIR / "basecolor"
    NORMAL_DIR = STATIC_DIR / "normal"
    GLB_EXPORTS_DIR = STATIC_DIR / "glb_exports"
    USDZ_EXPORTS_DIR = STATIC_DIR / "usdz_exports"
    
    # Texture settings
    TEXTURE_RESOLUTION = 2048  # Output texture size (power of 2)
    CORRECTED_IMAGE_SIZE = (2048, 2048)  # Size after perspective correction
    
    # Normal map settings
    NORMAL_MAP_STRENGTH = 1.0  # Intensity of normal map (0.0 - 2.0)
    NORMAL_MAP_BLUR = 3  # Gaussian blur kernel size for smoothing (odd number)
    SOBEL_KERNEL_SIZE = 3  # Sobel filter kernel size (3, 5, or 7)
    
    # 3D Model settings
    MESH_SUBDIVISION = 20  # Number of vertices per side (higher = more detail)
    DISPLACEMENT_SCALE = 0.02  # Height scale for displacement (in model units)
    CARPET_WIDTH = 2.0  # Physical width in meters
    CARPET_HEIGHT = 3.0  # Physical length in meters
    
    # Material properties (PBR) - iOS compatible values
    MATERIAL_ROUGHNESS = 0.8  # Surface roughness (0.0 = smooth, 1.0 = rough)
    MATERIAL_METALLIC = 0.0  # Metallic property (0.0 = non-metal, 1.0 = metal)
    
    # Export settings
    GLB_COMPRESSION = False  # Enable Draco compression for smaller files
    EXPORT_TEXTURES_EMBEDDED = True  # Embed textures in GLB file
    
    # Image processing
    CANNY_THRESHOLD1 = 50
    CANNY_THRESHOLD2 = 150
    BILATERAL_FILTER_D = 9  # Diameter for bilateral filter
    BILATERAL_FILTER_SIGMA_COLOR = 75
    BILATERAL_FILTER_SIGMA_SPACE = 75
    
    @classmethod
    def ensure_directories(cls):
        """Create all necessary directories if they don't exist."""
        for directory in [
            cls.UPLOADS_DIR,
            cls.TEXTURES_DIR,
            cls.CORRECTED_DIR,
            cls.BASECOLOR_DIR,
            cls.NORMAL_DIR,
            cls.GLB_EXPORTS_DIR,
            cls.USDZ_EXPORTS_DIR
        ]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_texture_path(cls, filename: str) -> Path:
        """Get full path for a texture file."""
        return cls.TEXTURES_DIR / filename
    
    @classmethod
    def get_corrected_path(cls, filename: str) -> Path:
        """Get full path for a corrected image."""
        return cls.CORRECTED_DIR / filename
    
    @classmethod
    def get_basecolor_path(cls, filename: str) -> Path:
        """Get full path for a basecolor texture."""
        return cls.BASECOLOR_DIR / filename
    
    @classmethod
    def get_normal_path(cls, filename: str) -> Path:
        """Get full path for a normal map."""
        return cls.NORMAL_DIR / filename
    
    @classmethod
    def get_glb_path(cls, filename: str) -> Path:
        """Get full path for a GLB export."""
        return cls.GLB_EXPORTS_DIR / filename
    
    @classmethod
    def get_usdz_path(cls, filename: str) -> Path:
        """Get full path for a USDZ export."""
        return cls.USDZ_EXPORTS_DIR / filename
    

