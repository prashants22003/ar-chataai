"""
Basecolor texture generation from corrected carpet images.

Processes corrected images to create clean, optimized basecolor textures
for 3D rendering.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Union
import logging

from ..utils.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_basecolor(
    corrected_image: Union[np.ndarray, str],
    output_resolution: int = None,
    output_name: str = None
) -> str:
    """
    Generate basecolor texture from corrected carpet image.
    
    Applies color correction, enhancement, and denoising to create
    a clean texture suitable for 3D rendering.
    
    Args:
        corrected_image: Either numpy array or path to corrected image
        output_resolution: Target resolution (will be square). Defaults to Config.TEXTURE_RESOLUTION
        
    Returns:
        Path to saved basecolor texture
    """
    if output_resolution is None:
        output_resolution = Config.TEXTURE_RESOLUTION
    
    # Load image if path is provided
    if isinstance(corrected_image, str):
        image = cv2.imread(corrected_image)
        if image is None:
            raise ValueError(f"Could not load image from {corrected_image}")
        input_name = Path(corrected_image).stem
    else:
        image = corrected_image.copy()
        input_name = output_name if output_name else "image"
    
    logger.info("Generating basecolor texture...")
    
    # Use LAB color space for better color preservation
    # Convert to LAB color space for gentle enhancement
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply gentle CLAHE to L channel only (preserves original colors)
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))  # Gentler than original 2.0
    l_enhanced = clahe.apply(l)
    
    # Merge channels back (preserves original A, B color channels)
    lab_enhanced = cv2.merge([l_enhanced, a, b])
    enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
    
    # Gentle denoising to reduce noise while preserving colors
    denoised = cv2.fastNlMeansDenoisingColored(
        enhanced,
        None,
        h=5,  # Reduced from 10
        hColor=5,  # Reduced from 10
        templateWindowSize=7,
        searchWindowSize=21
    )
    
    # Slight sharpening to bring back texture details
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]]) / 1.0
    sharpened = cv2.filter2D(denoised, -1, kernel * 0.1)
    sharpened = cv2.addWeighted(denoised, 0.9, sharpened, 0.1, 0)
    
    # Resize to target resolution (power of 2 for optimal rendering)
    final_size = (output_resolution, output_resolution)
    basecolor = cv2.resize(sharpened, final_size, interpolation=cv2.INTER_LANCZOS4)
    
    # Generate output filename
    output_filename = f"{input_name}_basecolor.png"
    output_path = Config.get_basecolor_path(output_filename)
    
    # Export in correct RGB format using our export function
    from ..export_functions.texture_export import export_png_rgb
    export_png_rgb(basecolor, str(output_path))
    logger.info(f"Saved basecolor texture to: {output_path}")
    
    return str(output_path)


def normalize_lighting(image: np.ndarray) -> np.ndarray:
    """
    Normalize lighting across the image to reduce shadows and highlights.
    
    Args:
        image: Input image
        
    Returns:
        Image with normalized lighting
    """
    # Convert to float for processing
    img_float = image.astype(np.float32) / 255.0
    
    # Apply bilateral filter to estimate illumination
    illumination = cv2.bilateralFilter(
        img_float,
        d=9,
        sigmaColor=0.1,
        sigmaSpace=9
    )
    
    # Divide original by illumination to remove lighting variations
    normalized = np.divide(
        img_float,
        illumination + 0.01,  # Add small value to avoid division by zero
        out=np.zeros_like(img_float),
        where=illumination != 0
    )
    
    # Clip and scale back to 0-255
    normalized = np.clip(normalized * 255, 0, 255).astype(np.uint8)
    
    return normalized

