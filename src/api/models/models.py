"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

class DimensionsModel(BaseModel):
    """Model dimensions for carpet generation."""
    
    length: float = Field(..., ge=0.5, le=10.0, description="Length in meters")
    width: float = Field(..., ge=0.5, le=10.0, description="Width in meters")
    thickness: float = Field(..., ge=1.0, le=20.0, description="Thickness in millimeters")
    
    @validator('length', 'width', 'thickness')
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError('Value must be positive')
        return v

class UploadRequest(BaseModel):
    """Request model for file upload."""
    
    dimensions: DimensionsModel
    skip_perspective: bool = Field(default=True, description="Skip perspective correction")

class UploadResponse(BaseModel):
    """Response model for successful upload."""
    
    success: bool = True
    filename: str
    public_url: str
    ar_viewer_link: str
    size: int
    dimensions: DimensionsModel
    message: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    """Error response model."""
    
    success: bool = False
    error: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = "ok"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    service: str = "AR-Chataai API Server"
    version: str = "1.0.0"
    dependencies: Optional[Dict[str, Any]] = None

class DetailedHealthResponse(HealthResponse):
    """Detailed health check response."""
    
    system: Optional[Dict[str, Any]] = None
    uptime: Optional[str] = None

class ModelGenerationStatus(BaseModel):
    """Model generation status for background tasks."""
    
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: int = Field(ge=0, le=100)
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
