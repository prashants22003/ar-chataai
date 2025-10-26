"""
Example usage script for the Carpet 3D Model Generator.

This demonstrates how to use the pipeline programmatically.
"""

from pathlib import Path
from main import process_carpet
from carpet_generation.utils.config import Config

def example_basic_usage():
    """Basic usage example."""
    print("Example 1: Basic Usage")
    print("-" * 50)
    
    # Place your carpet image in static/uploads/
    input_image = "static/uploads/my_carpet.jpg"
    
    if not Path(input_image).exists():
        print(f"Please place a carpet image at: {input_image}")
        return
    
    # Process the carpet
    glb_path, usdz_path = process_carpet(input_image)
    
    print(f"\nSuccess! Models generated:")
    print(f"  GLB: {glb_path}")
    print(f"  USDZ: {usdz_path}")


def example_custom_settings():
    """Example with custom settings."""
    print("\nExample 2: Custom Settings")
    print("-" * 50)
    
    # Customize settings before processing
    Config.TEXTURE_RESOLUTION = 1024  # Lower resolution for faster processing
    Config.MESH_SUBDIVISION = 150  # Less detail for smaller files
    Config.DISPLACEMENT_SCALE = 0.03  # More pronounced displacement
    
    input_image = "static/uploads/test_carpet.jpg"
    
    if not Path(input_image).exists():
        print(f"Please place a carpet image at: {input_image}")
        return
    
    glb_path, usdz_path = process_carpet(input_image, output_name="custom_carpet")
    
    print(f"\nSuccess! Custom models generated:")
    print(f"  GLB: {glb_path}")
    print(f"  USDZ: {usdz_path}")


def example_manual_corners():
    """Example with manual corner detection."""
    print("\nExample 3: Manual Corner Detection")
    print("-" * 50)
    
    input_image = "static/uploads/difficult_carpet.jpg"
    
    if not Path(input_image).exists():
        print(f"Please place a carpet image at: {input_image}")
        return
    
    # Define corner points manually (top-left, top-right, bottom-right, bottom-left)
    # These are pixel coordinates in the original image
    manual_corners = [
        (100, 150),   # Top-left
        (800, 120),   # Top-right
        (850, 900),   # Bottom-right
        (50, 950)     # Bottom-left
    ]
    
    glb_path, usdz_path = process_carpet(
        input_image,
        manual_corners=manual_corners
    )
    
    print(f"\nSuccess! Models with manual corners:")
    print(f"  GLB: {glb_path}")
    print(f"  USDZ: {usdz_path}")


if __name__ == "__main__":
    print("=" * 60)
    print("Carpet 3D Model Generator - Example Usage")
    print("=" * 60)
    
    # Run basic example
    # Uncomment the example you want to run:
    
    # example_basic_usage()
    # example_custom_settings()
    # example_manual_corners()
    
    print("\nNote: Uncomment one of the examples in the code to run it.")
    print("Make sure to place test images in static/uploads/ directory.")

