"""
File manager service for handling file operations
"""

import os
import uuid
import shutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from config import Settings

logger = logging.getLogger(__name__)

class FileManagerService:
    """File management service."""
    
    def __init__(self):
        """Initialize file manager."""
        self.settings = Settings()
        self.uploads_dir = Path(self.settings.upload_dir)
        self.ensure_uploads_dir()
    
    def ensure_uploads_dir(self):
        """Ensure uploads directory exists."""
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Uploads directory: {self.uploads_dir}")
    
    def generate_unique_filename(self, original_name: str) -> str:
        """Generate unique filename."""
        file_ext = Path(original_name).suffix
        base_name = Path(original_name).stem
        unique_id = str(uuid.uuid4())[:8]
        return f"{base_name}_{unique_id}{file_ext}"
    
    def format_file_size(self, bytes_size: int) -> str:
        """Format file size in human readable format."""
        sizes = ['Bytes', 'KB', 'MB', 'GB']
        if bytes_size == 0:
            return '0 Bytes'
        i = 0
        while bytes_size >= 1024 and i < len(sizes) - 1:
            bytes_size /= 1024.0
            i += 1
        return f"{bytes_size:.2f} {sizes[i]}"
    
    def validate_file_type(self, filename: str) -> bool:
        """Validate file type."""
        ext = Path(filename).suffix.lower()
        allowed_extensions = ['.jpg', '.jpeg', '.png']
        return ext in allowed_extensions
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file to disk."""
        file_path = self.uploads_dir / filename
        with open(file_path, 'wb') as f:
            f.write(file_content)
        return str(file_path)
    
    def cleanup_file(self, file_path: str):
        """Clean up temporary file."""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.info(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup file {file_path}: {e}")
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file information."""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            return {
                "size": stat.st_size,
                "size_formatted": self.format_file_size(stat.st_size),
                "created": datetime.fromtimestamp(stat.st_ctime),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "is_file": os.path.isfile(file_path),
                "is_directory": os.path.isdir(file_path)
            }
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            return None
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old temporary files."""
        try:
            if not self.uploads_dir.exists():
                return
            
            now = datetime.now()
            max_age = timedelta(hours=max_age_hours)
            cleaned_count = 0
            
            for file_path in self.uploads_dir.iterdir():
                if file_path.is_file():
                    file_info = self.get_file_info(str(file_path))
                    if file_info:
                        file_age = now - file_info["created"]
                        if file_age > max_age:
                            self.cleanup_file(str(file_path))
                            cleaned_count += 1
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old temporary files")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old files: {e}")
    
    def get_temp_file_path(self, filename: str) -> str:
        """Get temporary file path."""
        return str(self.uploads_dir / filename)
