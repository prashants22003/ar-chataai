"""
Model Generation API Client
Python client for integrating model generation with the API server
"""

import requests
import os
import sys
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)

class ModelGenerationAPIClient:
    """Client for communicating with the API server."""
    
    def __init__(self, api_base_url: str = "http://localhost:3000"):
        """
        Initialize the API client.
        
        Args:
            api_base_url: Base URL of the API server
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.upload_url = f"{self.api_base_url}/api/upload"
        self.ar_viewer_url = f"{self.api_base_url}/api/ar-viewer"
        self.health_url = f"{self.api_base_url}/api/health"
        
    def check_health(self) -> bool:
        """
        Check if the API server is healthy.
        
        Returns:
            bool: True if server is healthy, False otherwise
        """
        try:
            response = requests.get(self.health_url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.warning(f"API server health check failed: {e}")
            return False
    
    def upload_model(self, glb_path: str, model_name: Optional[str] = None) -> Optional[Tuple[str, str]]:
        """
        Upload GLB model to Supabase and get AR viewer link.
        
        Args:
            glb_path: Path to the GLB file
            model_name: Optional name for the model
            
        Returns:
            Tuple of (ar_viewer_link, public_url) if successful, None otherwise
        """
        if not self.check_health():
            logger.error("API server is not healthy")
            return None
        
        if not os.path.exists(glb_path):
            logger.error(f"GLB file not found: {glb_path}")
            return None
        
        try:
            # Upload file to API server
            with open(glb_path, 'rb') as f:
                files = {'glb': f}
                response = requests.post(
                    f"{self.upload_url}/generate-ar-link",
                    files=files,
                    timeout=60
                )
            
            if response.status_code == 200:
                result = response.json()
                ar_viewer_link = result.get('ar_viewer_link')
                public_url = result.get('public_url')
                
                logger.info(f"Upload successful: {result.get('filename')}")
                logger.info(f"Public URL: {public_url}")
                logger.info(f"AR Viewer Link: {ar_viewer_link}")
                
                return (ar_viewer_link, public_url)
            else:
                error_msg = response.json().get('error', 'Unknown error')
                logger.error(f"Upload failed: {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading model: {e}")
            return None
    
    def get_ar_viewer_link(self, model_url: str) -> str:
        """
        Generate AR viewer link for a given model URL.
        
        Args:
            model_url: URL of the model
            
        Returns:
            AR viewer link
        """
        return f"{self.ar_viewer_url}?model_url={model_url}"
    
    def get_server_info(self) -> Optional[Dict[str, Any]]:
        """
        Get API server information.
        
        Returns:
            Server info dict or None if failed
        """
        try:
            response = requests.get(f"{self.api_base_url}/", timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get server info: {e}")
            return None

def get_api_client() -> ModelGenerationAPIClient:
    """Get the API client instance."""
    return ModelGenerationAPIClient()

