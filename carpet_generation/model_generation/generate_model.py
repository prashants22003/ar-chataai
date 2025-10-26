"""
3D model generation with displaced geometry.

Creates carpet meshes with displacement based on height maps and exports
to GLB and USDZ formats for AR viewing.
"""

import cv2
import numpy as np
import trimesh
from pathlib import Path
from typing import Tuple, Optional
import logging
import base64
import json
from PIL import Image

from ..utils.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_carpet_mesh(
    basecolor_path: str,
    normal_map_path: str,
    output_name: str = "carpet"
) -> trimesh.Trimesh:
    """
    Create a 3D carpet mesh with displaced geometry.
    
    Args:
        basecolor_path: Path to basecolor texture
        normal_map_path: Path to normal map texture
        output_name: Base name for output files
        
    Returns:
        Trimesh object representing the carpet
    """
    logger.info("Creating carpet mesh with displaced geometry...")
    
    # Load normal map to use for displacement
    normal_map = cv2.imread(normal_map_path)
    if normal_map is None:
        raise ValueError(f"Could not load normal map from {normal_map_path}")
    
    # Convert normal map to height map (use blue channel which represents Z)
    height_map = cv2.cvtColor(normal_map, cv2.COLOR_BGR2GRAY)
    height_map = height_map.astype(np.float32) / 255.0
    
    # Create subdivided plane mesh
    vertices, faces, uvs = create_subdivided_plane(
        width=Config.CARPET_WIDTH,
        height=Config.CARPET_HEIGHT,
        subdivisions=Config.MESH_SUBDIVISION
    )
    
    # Apply displacement based on height map
    vertices = apply_displacement(
        vertices,
        uvs,
        height_map,
        scale=Config.DISPLACEMENT_SCALE
    )
    
    # Create trimesh object
    mesh = trimesh.Trimesh(
        vertices=vertices,
        faces=faces,
        process=False
    )
    
    # Add UV coordinates only (material will be applied during export)
    mesh.visual = trimesh.visual.TextureVisuals(
        uv=uvs
    )
    
    # Fix face normals to point upward (+Y direction)
    # This ensures the carpet face is visible when lying on the ground
    mesh.fix_normals()
    
    # Explicitly compute vertex normals for proper lighting
    mesh.vertex_normals
    
    logger.info(f"Created mesh with {len(vertices)} vertices and {len(faces)} faces")
    
    return mesh


def create_subdivided_plane(
    width: float,
    height: float,
    subdivisions: int
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Create a subdivided plane mesh.
    
    Args:
        width: Plane width in meters
        height: Plane height in meters
        subdivisions: Number of subdivisions per side
        
    Returns:
        Tuple of (vertices, faces, uvs)
    """
    # Create grid of vertices
    # For carpets: lay flat on ground (XZ plane, Y-up coordinate system)
    x = np.linspace(-width/2, width/2, subdivisions)
    z = np.linspace(-height/2, height/2, subdivisions)
    
    # Create meshgrid
    xv, zv = np.meshgrid(x, z)
    
    # Flatten to get vertex positions (Y = 0 initially, carpet lies on XZ plane)
    vertices = np.zeros((subdivisions * subdivisions, 3), dtype=np.float32)
    vertices[:, 0] = xv.flatten()  # X-axis: width
    vertices[:, 1] = 0.0           # Y-axis: height (up direction)
    vertices[:, 2] = zv.flatten()  # Z-axis: depth
    
    # Create UV coordinates
    u = np.linspace(0, 1, subdivisions)
    v = np.linspace(0, 1, subdivisions)
    uv, vv = np.meshgrid(u, v)
    uvs = np.zeros((subdivisions * subdivisions, 2), dtype=np.float32)
    uvs[:, 0] = uv.flatten()
    uvs[:, 1] = 1.0 - vv.flatten()  # Flip V coordinate
    
    # Create faces (two triangles per quad)
    # Use counter-clockwise winding when viewed from below (-Y direction, looking up)
    # This ensures the carpet face points upward when lying on the ground
    faces = []
    for i in range(subdivisions - 1):
        for j in range(subdivisions - 1):
            # Bottom-left vertex of quad (in XZ plane)
            idx = i * subdivisions + j
            
            # Two triangles per quad with counter-clockwise winding (viewed from below)
            # Triangle 1: bottom-left -> top-left -> bottom-right
            faces.append([idx, idx + subdivisions, idx + 1])
            # Triangle 2: bottom-right -> top-left -> top-right
            faces.append([idx + 1, idx + subdivisions, idx + subdivisions + 1])
    
    faces = np.array(faces, dtype=np.int32)
    
    return vertices, faces, uvs


def apply_displacement(
    vertices: np.ndarray,
    uvs: np.ndarray,
    height_map: np.ndarray,
    scale: float
) -> np.ndarray:
    """
    Apply displacement to vertices based on height map.
    
    For carpets lying flat on the ground, displacement is applied along Y-axis (up).
    
    Args:
        vertices: Vertex positions
        uvs: UV coordinates
        height_map: Height map (0-1 values)
        scale: Displacement scale
        
    Returns:
        Displaced vertices
    """
    height, width = height_map.shape
    displaced_vertices = vertices.copy()
    
    for i, uv in enumerate(uvs):
        # Convert UV to pixel coordinates
        u, v = uv
        x = int(u * (width - 1))
        y = int(v * (height - 1))
        
        # Get height value
        h = height_map[y, x]
        
        # Displace along Y-axis (up direction for carpet pile/texture depth)
        displaced_vertices[i, 1] = (h - 0.5) * scale
    
    return displaced_vertices


def export_glb(
    mesh: trimesh.Trimesh,
    basecolor_path: str,
    normal_map_path: str,
    output_name: str = "carpet"
) -> str:
    """
    Export mesh to GLB format with embedded textures.
    
    Args:
        mesh: Trimesh object
        basecolor_path: Path to basecolor texture
        normal_map_path: Path to normal map texture
        output_name: Base name for output file
        
    Returns:
        Path to exported GLB file
    """
    logger.info("Exporting to GLB format...")
    
    # Load textures using PIL with format validation for iOS compatibility
    try:
        basecolor_image = Image.open(basecolor_path)
        normal_map_image = Image.open(normal_map_path)
        
        # Validate and ensure RGB format for iOS compatibility
        if basecolor_image.mode != 'RGB':
            logger.info(f"Converting basecolor from {basecolor_image.mode} to RGB")
            basecolor_image = basecolor_image.convert('RGB')
        
        if normal_map_image.mode != 'RGB':
            logger.info(f"Converting normal map from {normal_map_image.mode} to RGB")
            normal_map_image = normal_map_image.convert('RGB')
        
        # Validate texture dimensions (must be power of 2 for iOS compatibility)
        if not (basecolor_image.width & (basecolor_image.width - 1) == 0):
            logger.warning(f"Basecolor texture width ({basecolor_image.width}) is not power of 2 - may cause iOS issues")
        if not (basecolor_image.height & (basecolor_image.height - 1) == 0):
            logger.warning(f"Basecolor texture height ({basecolor_image.height}) is not power of 2 - may cause iOS issues")
            
        if not (normal_map_image.width & (normal_map_image.width - 1) == 0):
            logger.warning(f"Normal map width ({normal_map_image.width}) is not power of 2 - may cause iOS issues")
        if not (normal_map_image.height & (normal_map_image.height - 1) == 0):
            logger.warning(f"Normal map height ({normal_map_image.height}) is not power of 2 - may cause iOS issues")
            
    except Exception as e:
        raise ValueError(f"Could not load texture images: {e}")
    
    logger.info(f"Loaded textures (RGB) - Basecolor: {basecolor_image.size}, Normal: {normal_map_image.size}")
    
    # Debug: Sample basecolor texture pixels to verify colors
    try:
        sample_pixels = [
            basecolor_image.getpixel((100, 100)),
            basecolor_image.getpixel((500, 500)),
            basecolor_image.getpixel((1000, 1000))
        ]
        logger.info(f"Basecolor sample pixels: {sample_pixels}")
    except Exception as e:
        logger.debug(f"Could not sample basecolor pixels: {e}")
    
    # Validate normal map format (should be blue-dominant for flat surfaces)
    try:
        sample_pixel = normal_map_image.getpixel((100, 100))
        if len(sample_pixel) == 3:
            r, g, b = sample_pixel
            if b > r and b > g:
                logger.debug("Normal map appears correct (blue-dominant)")
            else:
                logger.debug(f"Normal map may have channel issues - B({b}) not dominant over R({r}), G({g})")
    except Exception as e:
        logger.debug(f"Could not validate normal map format: {e}")
    
    # Create PBR material with textures for iOS compatibility
    # Use original textures without gamma modification
    basecolor_image_rgb = basecolor_image
    normal_map_image_rgb = normal_map_image
    
    # Create PBR material - trimesh expects PIL Images for proper texture embedding in GLB
    material = trimesh.visual.material.PBRMaterial(
        baseColorFactor=[1.0, 1.0, 1.0, 1.0],  # White multiplier for true texture colors
        metallicFactor=0.0,
        roughnessFactor=0.8,  # Higher roughness for carpet texture
        baseColorTexture=basecolor_image_rgb,
        normalTexture=normal_map_image_rgb,
        alphaMode='OPAQUE',
        doubleSided=False
    )
    
    # Apply material to mesh with original UV coordinates
    # Get original UV coordinates from mesh creation
    original_uvs = mesh.visual.uv
    mesh.visual = trimesh.visual.TextureVisuals(
        uv=original_uvs,
        material=material
    )
    
    # Verify texture application
    if hasattr(mesh.visual, 'material'):
        logger.info("Material successfully applied to mesh")
        if hasattr(mesh.visual.material, 'baseColorTexture') and mesh.visual.material.baseColorTexture is not None:
            logger.info(f"Basecolor texture attached: {type(mesh.visual.material.baseColorTexture)}")
        else:
            logger.warning("Basecolor texture not attached!")
    else:
        logger.warning("Material not applied to mesh!")
    
    # Generate output path
    output_filename = f"{output_name}.glb"
    output_path = Config.get_glb_path(output_filename)
    
    # Export to GLB with iOS-compatible settings
    Config.ensure_directories()
    try:
        mesh.export(
            str(output_path), 
            file_type='glb',
            include_normals=False  # iOS prefers computed normals
        )
        logger.info(f"Successfully exported GLB to: {output_path}")
        
        # Verify file was created and has reasonable size
        import os
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            logger.info(f"GLB file size: {file_size:.2f} MB")
        else:
            logger.error("GLB file was not created!")
            
    except Exception as e:
        logger.error(f"Failed to export GLB: {e}")
        raise
    
    return str(output_path)


def export_usdz(
    glb_path: str,
    output_name: str = "carpet"
) -> str:
    """
    Convert GLB file to USDZ format using the USDZ conversion script.
    
    Args:
        glb_path: Path to GLB file
        output_name: Base name for output file
        
    Returns:
        Path to exported USDZ file
    """
    logger.info("Converting GLB to USDZ format...")
    
    # Import the conversion function
    from ..usdz_conversion import convert_glb_to_usdz
    
    # Generate output path
    output_filename = f"{output_name}.usdz"
    usdz_path = Config.get_usdz_path(output_filename)
    
    # Ensure output directory exists
    Config.ensure_directories()
    
    try:
        # Convert GLB to USDZ
        convert_glb_to_usdz(glb_path, str(usdz_path))
        
        # Verify file was created
        import os
        if os.path.exists(usdz_path):
            file_size = os.path.getsize(usdz_path) / (1024 * 1024)  # MB
            logger.info(f"USDZ file created successfully: {usdz_path}")
            logger.info(f"USDZ file size: {file_size:.2f} MB")
        else:
            logger.error("USDZ file was not created!")
            raise RuntimeError("USDZ conversion failed - file not created")
            
    except Exception as e:
        logger.error(f"Failed to convert GLB to USDZ: {e}")
        
        # Clean up any temporary files that might be causing issues
        import os
        import glob
        temp_files = glob.glob(str(usdz_path).replace('.usdz', '.*'))
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file) and not temp_file.endswith('.usdz'):
                    os.remove(temp_file)
                    logger.info(f"Cleaned up temporary file: {temp_file}")
            except Exception as cleanup_error:
                logger.warning(f"Could not clean up temporary file {temp_file}: {cleanup_error}")
        
        # Re-raise the original exception
        raise
    
    return str(usdz_path)


def generate_carpet_model(
    basecolor_path: str,
    normal_map_path: str,
    output_name: str = "carpet"
) -> Tuple[str, str]:
    """
    Complete pipeline: create mesh and export to both GLB and USDZ.
    
    Args:
        basecolor_path: Path to basecolor texture
        normal_map_path: Path to normal map texture
        output_name: Base name for output files
        
    Returns:
        Tuple of (GLB path, USDZ path)
    """
    # Create mesh
    mesh = create_carpet_mesh(basecolor_path, normal_map_path, output_name)
    
    # Export to GLB
    glb_path = export_glb(mesh, basecolor_path, normal_map_path, output_name)
    
    # Export to USDZ
    usdz_path = export_usdz(glb_path, output_name)
    
    return glb_path, usdz_path

