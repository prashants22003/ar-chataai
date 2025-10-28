"""
Python Supabase client service
"""

import os
import logging
from typing import Optional, Dict, Any
from supabase import create_client, Client
from config import Settings

logger = logging.getLogger(__name__)

class SupabaseService:
    """Supabase storage service."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.settings = Settings()
        self.client: Optional[Client] = None
        self.bucket_name = "3d-models"
        
        if self.settings.supabase_configured:
            try:
                self.client = create_client(
                    self.settings.project_url,
                    self.settings.api_key
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.client = None
        else:
            logger.warning("Supabase not configured - set PROJECT_URL and API_KEY")
    
    def is_configured(self) -> bool:
        """Check if Supabase is properly configured."""
        return self.client is not None
    
    async def test_connection(self) -> bool:
        """Test Supabase connection."""
        if not self.client:
            return False
        
        try:
            # Try to list buckets to test connection
            buckets = self.client.storage.list_buckets()
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False
    
    async def upload_file(self, filename: str, file_data: bytes) -> Dict[str, Any]:
        """
        Upload file to Supabase storage.
        
        Args:
            filename: Name of the file
            file_data: File data as bytes
            
        Returns:
            Dict with success status and public URL
        """
        if not self.client:
            return {
                "success": False,
                "error": "Supabase client not configured"
            }
        
        try:
            logger.info(f"Uploading {filename} to Supabase...")
            
            # Upload to Supabase storage
            result = self.client.storage.from_(self.bucket_name).upload(
                filename,
                file_data,
                file_options={"content-type": "model/gltf-binary"}
            )
            
            if result.get("error"):
                logger.error(f"Upload error: {result['error']}")
                return {
                    "success": False,
                    "error": result["error"]["message"]
                }
            
            # Get public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(filename)
            
            logger.info(f"Upload successful: {filename}")
            logger.info(f"Public URL: {public_url}")
            
            return {
                "success": True,
                "public_url": public_url,
                "filename": filename
            }
            
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        if not self.client:
            return {"error": "Supabase client not configured"}
        
        try:
            buckets = self.client.storage.list_buckets()
            
            models_bucket = None
            for bucket in buckets:
                if bucket.name == self.bucket_name:
                    models_bucket = bucket
                    break
            
            return {
                "bucket_exists": models_bucket is not None,
                "bucket_info": models_bucket,
                "all_buckets": [b.name for b in buckets],
                "supabase_url": self.settings.project_url
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {"error": str(e)}
    
    async def delete_file(self, filename: str) -> bool:
        """Delete file from Supabase storage."""
        if not self.client:
            return False
        
        try:
            result = self.client.storage.from_(self.bucket_name).remove([filename])
            return not result.get("error")
        except Exception as e:
            logger.error(f"Failed to delete file {filename}: {e}")
            return False
