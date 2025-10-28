"""
Main orchestration pipeline for carpet 3D model generation.

This script coordinates the entire process from input image to 3D model exports.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, Tuple

from .image_processing import (
    correct_perspective,
    generate_basecolor,
    generate_normal_map
)
from .model_generation import generate_carpet_model
from .utils.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_carpet(
    input_image_path: str,
    output_name: Optional[str] = None,
    manual_corners: Optional[list] = None
) -> Tuple[str, str]:
    """
    Complete pipeline to process a carpet image into 3D models.
    
    Steps:
    1. Perspective correction
    2. Generate basecolor texture
    3. Generate normal map
    4. Create 3D model with displaced geometry
    5. Export to GLB and USDZ formats
    
    Args:
        input_image_path: Path to input carpet image
        output_name: Optional custom name for output files
        manual_corners: Optional list of 4 corner points [(x,y), ...] for manual perspective correction
        
    Returns:
        Tuple of (GLB path, USDZ path)
    """
    logger.info("=" * 60)
    logger.info("Starting Carpet 3D Model Generation Pipeline")
    logger.info("=" * 60)
    
    # Ensure output directories exist
    Config.ensure_directories()
    
    # Determine output name
    if output_name is None:
        output_name = Path(input_image_path).stem
    
    try:
        # Step 1: Perspective Correction
        logger.info("\n[1/5] Applying perspective correction...")
        corrected_image, corrected_path = correct_perspective(
            input_image_path,
            manual_corners=manual_corners
        )
        logger.info(f"✓ Perspective correction complete: {corrected_path}")
        
        # Step 2: Generate Basecolor
        logger.info("\n[2/5] Generating basecolor texture...")
        basecolor_path = generate_basecolor(corrected_image, output_name=output_name)
        logger.info(f"✓ Basecolor texture generated: {basecolor_path}")
        
        # Step 3: Generate Normal Map
        logger.info("\n[3/5] Generating normal map...")
        normal_map_path = generate_normal_map(corrected_path, output_name=output_name)
        logger.info(f"✓ Normal map generated: {normal_map_path}")
        
        # Step 4 & 5: Create 3D Model and Export
        logger.info("\n[4/5] Creating 3D mesh with displaced geometry...")
        logger.info("[5/5] Exporting to GLB and USDZ formats...")
        glb_path, usdz_path = generate_carpet_model(
            basecolor_path,
            normal_map_path,
            output_name
        )
        
        logger.info("\n" + "=" * 60)
        logger.info("Pipeline completed successfully!")
        logger.info("=" * 60)
        logger.info(f"\nGenerated files:")
        logger.info(f"  - Corrected Image: {corrected_path}")
        logger.info(f"  - Basecolor:       {basecolor_path}")
        logger.info(f"  - Normal Map:      {normal_map_path}")
        logger.info(f"  - GLB Model:       {glb_path}")
        logger.info(f"  - USDZ Model:      {usdz_path}")
        logger.info("\n✓ Ready for AR viewing!")
        
        return glb_path, usdz_path
        
    except Exception as e:
        logger.error(f"\n✗ Pipeline failed: {str(e)}", exc_info=True)
        raise


def main():
    """Command-line interface for the carpet model generator."""
    parser = argparse.ArgumentParser(
        description="Generate 3D carpet models from images for AR viewing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --input my_carpet.jpg
  python main.py --input carpet.png --output my_carpet
  python main.py --input carpet.jpg --resolution 1024
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Path to input carpet image'
    )
    
    parser.add_argument(
        '--output', '-o',
        default=None,
        help='Output name for generated files (default: input filename)'
    )
    
    parser.add_argument(
        '--resolution', '-r',
        type=int,
        default=Config.TEXTURE_RESOLUTION,
        help=f'Texture resolution (default: {Config.TEXTURE_RESOLUTION})'
    )
    
    parser.add_argument(
        '--subdivisions', '-s',
        type=int,
        default=Config.MESH_SUBDIVISION,
        help=f'Mesh subdivision level (default: {Config.MESH_SUBDIVISION})'
    )
    
    parser.add_argument(
        '--displacement', '-d',
        type=float,
        default=Config.DISPLACEMENT_SCALE,
        help=f'Displacement scale (default: {Config.DISPLACEMENT_SCALE})'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {args.input}")
        sys.exit(1)
    
    # Update config if custom values provided
    if args.resolution != Config.TEXTURE_RESOLUTION:
        Config.TEXTURE_RESOLUTION = args.resolution
        logger.info(f"Using custom texture resolution: {args.resolution}")
    
    if args.subdivisions != Config.MESH_SUBDIVISION:
        Config.MESH_SUBDIVISION = args.subdivisions
        logger.info(f"Using custom mesh subdivisions: {args.subdivisions}")
    
    if args.displacement != Config.DISPLACEMENT_SCALE:
        Config.DISPLACEMENT_SCALE = args.displacement
        logger.info(f"Using custom displacement scale: {args.displacement}")
    
    # Run the pipeline
    try:
        glb_path, usdz_path = process_carpet(
            str(input_path),
            output_name=args.output
        )
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to process carpet: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

