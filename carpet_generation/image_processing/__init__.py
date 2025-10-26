"""
Image Processing Module

Handles perspective correction, texture generation, and normal map creation.
"""

from .perspective import correct_perspective, validate_corners
from .texture_gen import generate_basecolor
from .normal_map import generate_normal_map

__all__ = [
    'correct_perspective',
    'validate_corners',
    'generate_basecolor',
    'generate_normal_map'
]

