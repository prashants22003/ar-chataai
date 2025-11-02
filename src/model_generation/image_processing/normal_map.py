"""
Normal map generation using traditional computer vision techniques.

Creates normal maps from basecolor textures using gradient-based methods.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Union
import logging

from ..utils.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_normal_map(
    original_image_path: str,
    strength: float = None,
    output_name: str = None
) -> str:
    """
    Generate a normal map from the original corrected image (before basecolor processing).
    
    Args:
        original_image_path: Path to the original corrected image (before CLAHE/denoising)
        strength: Normal map intensity (0.0 - 2.0). Defaults to Config.NORMAL_MAP_STRENGTH
        output_name: Base name for output file
        
    Returns:
        Path to saved normal map
    """
    if strength is None:
        strength = Config.NORMAL_MAP_STRENGTH
    
    # Load original corrected image
    image = cv2.imread(original_image_path)
    if image is None:
        raise ValueError(f"Could not load image from {original_image_path}")
    
    logger.info("Generating normal map from original corrected image...")
    
    # Convert to grayscale to create height map
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    if Config.NORMAL_MAP_BLUR > 0:
        gray = cv2.GaussianBlur(gray, (Config.NORMAL_MAP_BLUR, Config.NORMAL_MAP_BLUR), 0)
    
    # Normalize to 0-1 range
    height_map = gray.astype(np.float32) / 255.0
    
    # Calculate gradients using Sobel filters
    sobel_x = cv2.Sobel(
        height_map,
        cv2.CV_32F,
        1, 0,
        ksize=Config.SOBEL_KERNEL_SIZE
    )
    
    sobel_y = cv2.Sobel(
        height_map,
        cv2.CV_32F,
        0, 1,
        ksize=Config.SOBEL_KERNEL_SIZE
    )
    
    # Apply strength multiplier (reduced for flatter surfaces)
    sobel_x = sobel_x * (strength * 0.3)  # Reduce strength for more subtle normals
    sobel_y = sobel_y * (strength * 0.3)
    
    # Create normal vectors
    # In tangent space: X points right, Y points up, Z points out of surface
    # Normal = (-dh/dx, -dh/dy, 1) normalized
    
    normal_x = -sobel_x
    normal_y = -sobel_y
    normal_z = np.ones_like(sobel_x)
    
    # Normalize the normal vectors
    magnitude = np.sqrt(normal_x**2 + normal_y**2 + normal_z**2)
    normal_x = normal_x / magnitude
    normal_y = normal_y / magnitude
    normal_z = normal_z / magnitude
    
    # Convert from [-1, 1] to [0, 255] range for RGB encoding
    # R = X component, G = Y component, B = Z component
    normal_r = ((normal_x + 1.0) * 0.5 * 255).astype(np.uint8)
    normal_g = ((normal_y + 1.0) * 0.5 * 255).astype(np.uint8)
    normal_b = ((normal_z + 1.0) * 0.5 * 255).astype(np.uint8)
    
    # Merge channels to create RGB normal map (correct order for iOS)
    normal_map = cv2.merge([normal_r, normal_g, normal_b])  # RGB format
    
    # Optional: apply slight blur to smooth the normal map
    normal_map = cv2.GaussianBlur(normal_map, (3, 3), 0)
    
    # Generate output filename
    if output_name:
        output_filename = f"{output_name}_normal.png"
    else:
        input_path = Path(original_image_path)
        output_filename = f"{input_path.stem.replace('_corrected', '')}_normal.png"
    output_path = Config.get_normal_path(output_filename)
    
    # Export as linear RGB (no ICC/gAMA/sRGB) for normal maps
    from ..export_functions.texture_export import export_png_linear_rgb
    export_png_linear_rgb(normal_map, str(output_path))
    logger.info(f"Saved normal map to: {output_path}")
    
    return str(output_path)


def create_height_map(basecolor_path: str) -> np.ndarray:
    """
    Create a height map from basecolor texture.
    
    This converts the image to grayscale and can be used for displacement.
    
    Args:
        basecolor_path: Path to basecolor texture
        
    Returns:
        Height map as numpy array (values 0-1)
    """
    image = cv2.imread(basecolor_path)
    if image is None:
        raise ValueError(f"Could not load image from {basecolor_path}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Normalize to 0-1 range
    height_map = blurred.astype(np.float32) / 255.0
    
    return height_map


def visualize_normal_map(normal_map_path: str, output_path: str = None):
    """
    Create a visualization of the normal map for debugging.
    
    Args:
        normal_map_path: Path to normal map
        output_path: Optional output path for visualization
    """
    normal_map = cv2.imread(normal_map_path)
    if normal_map is None:
        raise ValueError(f"Could not load normal map from {normal_map_path}")
    
    # The normal map already looks correct, but we can enhance visualization
    # by applying slight lighting
    
    if output_path is None:
        output_path = normal_map_path.replace('.png', '_viz.png')
    
    cv2.imwrite(output_path, normal_map)
    logger.info(f"Saved normal map visualization to: {output_path}")

