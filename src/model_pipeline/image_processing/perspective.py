"""
Perspective correction for carpet images.

Automatically detects carpet corners and applies perspective transform
to create a rectangular top-down view.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List
from pathlib import Path
import logging

from ..utils.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_corners(corners: List[Tuple[int, int]]) -> Optional[np.ndarray]:
    """
    Validate and order manual corner points.
    
    Args:
        corners: List of 4 (x, y) corner points
        
    Returns:
        Array of 4 corner points in order: top-left, top-right, bottom-right, bottom-left
        Returns None if validation fails
    """
    if len(corners) != 4:
        logger.error("Must provide exactly 4 corner points")
        return None
    
    # Convert to numpy array
    corners_array = np.array(corners, dtype=np.float32)
    
    # Order the corners: top-left, top-right, bottom-right, bottom-left
    ordered_corners = order_points(corners_array)
    
    logger.info("Using manual corner selection")
    return ordered_corners


def order_points(pts: np.ndarray) -> np.ndarray:
    """
    Order points in the sequence: top-left, top-right, bottom-right, bottom-left.
    
    Uses a robust method that ensures 4 unique corners.
    
    Args:
        pts: Array of 4 points
        
    Returns:
        Ordered array of points
    """
    # Initialize ordered points
    rect = np.zeros((4, 2), dtype=np.float32)
    
    # Calculate sums and differences
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1).flatten()
    
    # Find indices for each corner
    indices = np.arange(4)
    
    # Top-left: smallest sum
    top_left_idx = indices[np.argmin(s)]
    rect[0] = pts[top_left_idx]
    
    # Bottom-right: largest sum
    bottom_right_idx = indices[np.argmax(s)]
    rect[2] = pts[bottom_right_idx]
    
    # Get remaining indices
    remaining_indices = [i for i in indices if i != top_left_idx and i != bottom_right_idx]
    
    if len(remaining_indices) == 2:
        # Use x-coordinate to determine top-right vs bottom-left
        if pts[remaining_indices[0]][0] > pts[remaining_indices[1]][0]:
            rect[1] = pts[remaining_indices[0]]  # top-right (larger x)
            rect[3] = pts[remaining_indices[1]]  # bottom-left (smaller x)
        else:
            rect[1] = pts[remaining_indices[1]]  # top-right (larger x)
            rect[3] = pts[remaining_indices[0]]  # bottom-left (smaller x)
    
    return rect


def correct_perspective(
    image_path: str,
    output_size: Tuple[int, int] = None,
    manual_corners: Optional[List[Tuple[int, int]]] = None
) -> Tuple[np.ndarray, str]:
    """
    Correct perspective distortion in a carpet image.
    
    Args:
        image_path: Path to input image
        output_size: Desired output size (width, height). Defaults to Config.CORRECTED_IMAGE_SIZE
        manual_corners: Optional list of 4 corner points for manual selection
        
    Returns:
        Tuple of (corrected image as numpy array, output path)
    """
    if output_size is None:
        output_size = Config.CORRECTED_IMAGE_SIZE
    
    # Load image
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    logger.info(f"Processing image: {image_path}")
    logger.info(f"Original image shape: {image.shape}")
    
    # Use manual corners if provided, otherwise use full image
    if manual_corners is not None:
        corners = validate_corners(manual_corners)
        if corners is None:
            raise ValueError("Invalid manual corner points provided")
        
        # Define destination points for perspective transform
        dst_points = np.array([
            [0, 0],
            [output_size[0] - 1, 0],
            [output_size[0] - 1, output_size[1] - 1],
            [0, output_size[1] - 1]
        ], dtype=np.float32)
        
        # Compute perspective transform matrix
        matrix = cv2.getPerspectiveTransform(corners, dst_points)
        
        # Apply perspective transform
        corrected = cv2.warpPerspective(image, matrix, output_size)
        logger.info("Perspective correction applied successfully")
    else:
        logger.info("Using entire image (no perspective correction)")
        # Use entire image: just resize
        corrected = cv2.resize(image, output_size)
    
    # Generate output filename
    input_path = Path(image_path)
    output_filename = f"{input_path.stem}_corrected.png"
    output_path = Config.get_corrected_path(output_filename)
    
    # Save corrected image in original BGR format
    Config.ensure_directories()
    cv2.imwrite(str(output_path), corrected)
    logger.info(f"Saved corrected image to: {output_path}")
    
    return corrected, str(output_path)

