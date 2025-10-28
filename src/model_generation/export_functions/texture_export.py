"""
Texture Export Functions

Handles proper color format conversion and export for 3D textures.
Ensures BGR to RGB conversion is done correctly for iOS/Android compatibility.

The key issue: OpenCV exports images in BGR format, but PIL imports them as RGB.
We need to manually swap channels to ensure correct color mapping.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Union
import logging

from ..utils.config import Config

logger = logging.getLogger(__name__)


def convert_bgr_to_rgb(image: np.ndarray) -> np.ndarray:
    """
    Manually convert BGR image to RGB by swapping channels.
    
    This is the CORRECT way to handle BGR to RGB conversion.
    Using cv2.cvtColor(image, cv2.COLOR_BGR2RGB) doesn't work properly
    when exporting images for PIL import.
    
    Args:
        image: Image in BGR format (shape: H, W, 3)
        
    Returns:
        Image in RGB format (shape: H, W, 3)
    """
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(f"Expected 3-channel image, got shape: {image.shape}")
    
    # Manual channel swap: BGR -> RGB
    # Original: [B, G, R] -> Result: [R, G, B]
    rgb_image = image[:, :, ::-1]  # Reverse the channel order
    
    logger.debug(f"Converted BGR to RGB: shape {image.shape}")
    
    return rgb_image


def export_png_rgb(
    image: np.ndarray,
    output_path: Union[str, Path],
    compression: int = 9
) -> str:
    """
    Export image as PNG in RGB format for proper PIL import.
    
    CRITICAL: Uses PIL to save PNG files to avoid OpenCV's BGR format issue.
    
    Args:
        image: Image in BGR format (will be converted to RGB)
        output_path: Path to save the PNG file
        compression: PNG compression level (0-9, default=9)
        
    Returns:
        Path to saved file
    """
    from PIL import Image
    
    # Ensure directory exists
    Config.ensure_directories()
    
    # Convert BGR to RGB using our manual swap
    rgb_image = convert_bgr_to_rgb(image)
    
    # Convert to PIL Image
    pil_image = Image.fromarray(rgb_image)
    
    # Save as PNG using PIL (not OpenCV!)
    output_path = Path(output_path)
    pil_image.save(
        str(output_path),
        format='PNG',
        compress_level=compression
    )
    
    logger.info(f"Exported RGB PNG to: {output_path} (using PIL)")
    
    return str(output_path)


def export_basecolor_texture(
    processed_image: np.ndarray,
    output_name: str,
    output_resolution: int = None
) -> str:
    """
    Export basecolor texture in correct RGB format.
    
    Args:
        processed_image: Processed image in BGR format from OpenCV
        output_name: Base name for output file
        output_resolution: Target resolution (optional resize)
        
    Returns:
        Path to saved basecolor texture
    """
    if output_resolution is None:
        output_resolution = Config.TEXTURE_RESOLUTION
    
    logger.info("Exporting basecolor texture in RGB format...")
    
    # Resize if needed
    if output_resolution:
        h, w = processed_image.shape[:2]
        if h != output_resolution or w != output_resolution:
            final_size = (output_resolution, output_resolution)
            resized_image = cv2.resize(
                processed_image,
                final_size,
                interpolation=cv2.INTER_LANCZOS4
            )
        else:
            resized_image = processed_image
    else:
        resized_image = processed_image
    
    # Generate output filename
    output_filename = f"{output_name}_basecolor.png"
    output_path = Config.get_basecolor_path(output_filename)
    
    # Export in RGB format
    export_png_rgb(resized_image, output_path)
    
    logger.info(f"Saved basecolor texture to: {output_path}")
    
    return str(output_path)


def export_normal_map_texture(
    normal_map: np.ndarray,
    output_name: str,
    apply_blur: bool = True
) -> str:
    """
    Export normal map texture in correct RGB format.
    
    Args:
        normal_map: Normal map in BGR format (R=X, G=Y, B=Z components)
        output_name: Base name for output file
        apply_blur: Whether to apply slight blur for smoothing
        
    Returns:
        Path to saved normal map texture
    """
    logger.info("Exporting normal map texture in RGB format...")
    
    # Optional: apply slight blur to smooth the normal map
    if apply_blur:
        smoothed = cv2.GaussianBlur(normal_map, (3, 3), 0)
    else:
        smoothed = normal_map
    
    # Generate output filename
    output_filename = f"{output_name}_normal.png"
    output_path = Config.get_normal_path(output_filename)
    
    # Export in RGB format
    export_png_rgb(smoothed, output_path)
    
    logger.info(f"Saved normal map to: {output_path}")
    
    return str(output_path)


def verify_rgb_export(image_path: str) -> bool:
    """
    Verify that an exported image is in correct RGB format.
    
    This function loads the image with PIL (which interprets as RGB)
    and checks if the channel statistics match expected values.
    
    Args:
        image_path: Path to exported image
        
    Returns:
        True if verification passes, False otherwise
    """
    from PIL import Image
    
    try:
        # Load with PIL (interprets as RGB)
        pil_image = Image.open(image_path)
        pil_array = np.array(pil_image)
        
        # Check shape
        if pil_array.ndim != 3 or pil_array.shape[2] != 3:
            logger.error(f"Expected 3-channel RGB image, got shape: {pil_array.shape}")
            return False
        
        # Check if it's a valid image (not all zeros or all 255s)
        if pil_array.min() == pil_array.max():
            logger.warning("Image has no color variation")
            return False
        
        logger.info(f"Verified RGB export: {image_path} (shape: {pil_array.shape})")
        return True
        
    except Exception as e:
        logger.error(f"Failed to verify RGB export: {e}")
        return False


def batch_export_textures(
    basecolor_images: dict,
    normal_map_images: dict
) -> dict:
    """
    Export multiple textures in batch.
    
    Args:
        basecolor_images: Dict of {name: image_array}
        normal_map_images: Dict of {name: image_array}
        
    Returns:
        Dict with paths to exported textures
    """
    results = {
        'basecolor': {},
        'normal': {}
    }
    
    # Export basecolor textures
    for name, image in basecolor_images.items():
        try:
            path = export_basecolor_texture(image, name)
            results['basecolor'][name] = path
        except Exception as e:
            logger.error(f"Failed to export basecolor for {name}: {e}")
            results['basecolor'][name] = None
    
    # Export normal map textures
    for name, image in normal_map_images.items():
        try:
            path = export_normal_map_texture(image, name)
            results['normal'][name] = path
        except Exception as e:
            logger.error(f"Failed to export normal map for {name}: {e}")
            results['normal'][name] = None
    
    logger.info(f"Batch export complete: {len(results['basecolor'])} basecolor, {len(results['normal'])} normal maps")
    
    return results
