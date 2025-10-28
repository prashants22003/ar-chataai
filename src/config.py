"""
Unified configuration for AR-Chataai Backend
Combines API server and model generation settings
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Unified application settings."""
    
    # Server settings
    port: int = 3000
    host: str = "0.0.0.0"
    debug: bool = False
    
    # Supabase settings
    project_url: Optional[str] = None
    api_key: Optional[str] = None
    
    # File settings
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_file_types: list = ["image/jpeg", "image/jpg", "image/png"]
    
    # Model generation settings
    model_timeout: int = 300  # 5 minutes
    cleanup_interval: int = 24  # hours
    
    # Model generation pipeline settings
    texture_resolution: int = 1024
    mesh_subdivision: int = 20
    displacement_scale: float = 0.02
    carpet_width: float = 2.0  # meters
    carpet_height: float = 3.0  # meters
    carpet_thickness: float = 0.005  # meters (5mm)
    
    class Config:
        env_file = ".env"
        env_prefix = ""
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from environment
    
    @property
    def supabase_configured(self) -> bool:
        """Check if Supabase is properly configured."""
        return bool(self.project_url and self.api_key)
    
    @property
    def upload_dir(self) -> str:
        """Get upload directory path."""
        return os.path.join(os.path.dirname(__file__), "uploads")
    
    @property
    def static_dir(self) -> str:
        """Get static directory path."""
        return os.path.join(os.path.dirname(__file__), "static")
    
    @property
    def output_dir(self) -> str:
        """Get output directory path."""
        return os.path.join(os.path.dirname(__file__), "output")
    
    def ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.upload_dir,
            self.static_dir,
            self.output_dir,
            os.path.join(self.output_dir, "static"),
            os.path.join(self.output_dir, "static", "glb_exports"),
            os.path.join(self.output_dir, "static", "usdz_exports"),
            os.path.join(self.output_dir, "textures"),
            os.path.join(self.output_dir, "textures", "basecolor"),
            os.path.join(self.output_dir, "textures", "normal_maps"),
            os.path.join(self.output_dir, "corrected_images")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
