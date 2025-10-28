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
import pygltflib
from pygltflib import GLTF2, Buffer, BufferView, Accessor, Mesh, Primitive, Attributes, Material, PbrMetallicRoughness, TextureInfo, Image as GLTFImage, Texture, Sampler

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
    # Scale displacement by thickness to maintain proportional detail
    displacement_scale = Config.DISPLACEMENT_SCALE * (Config.CARPET_THICKNESS / 0.005)  # Scale relative to 5mm default
    vertices = apply_displacement(
        vertices,
        uvs,
        height_map,
        scale=displacement_scale
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
    
    # Compute tangent vectors for consistent normal mapping across platforms
    tangents = compute_tangents(vertices, faces, uvs, mesh.vertex_normals)
    
    # Store tangents as vertex attributes for GLB export
    mesh.vertex_attributes['tangent'] = tangents
    
    logger.info(f"Created mesh with {len(vertices)} vertices and {len(faces)} faces")
    logger.info(f"Added tangent vectors for consistent normal mapping")
    
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


def compute_tangents(
    vertices: np.ndarray,
    faces: np.ndarray,
    uvs: np.ndarray,
    normals: np.ndarray
) -> np.ndarray:
    """
    Compute tangent vectors for each vertex using the standard tangent space algorithm.
    
    This implementation follows the industry-standard method for generating consistent
    tangent spaces across different platforms, ensuring proper normal mapping.
    
    Args:
        vertices: Vertex positions (N, 3)
        faces: Face indices (M, 3)
        uvs: UV coordinates (N, 2)
        normals: Vertex normals (N, 3)
        
    Returns:
        tangents: Tangent vectors (N, 3)
    """
    logger.info("Computing tangent vectors for consistent normal mapping...")
    
    # Initialize tangent and bitangent arrays
    tangents = np.zeros_like(vertices)
    bitangents = np.zeros_like(vertices)
    
    # Process each triangle
    for face_idx, face in enumerate(faces):
        # Get vertex indices for this triangle
        i1, i2, i3 = face
        
        # Get vertex positions
        v1, v2, v3 = vertices[i1], vertices[i2], vertices[i3]
        
        # Get UV coordinates
        w1, w2, w3 = uvs[i1], uvs[i2], uvs[i3]
        
        # Compute edges of the triangle
        edge1 = v2 - v1
        edge2 = v3 - v1
        
        # Compute UV deltas
        deltaUV1 = w2 - w1
        deltaUV2 = w3 - w1
        
        # Avoid division by zero
        denominator = deltaUV1[0] * deltaUV2[1] - deltaUV2[0] * deltaUV1[1]
        if abs(denominator) < 1e-8:
            # Degenerate UV triangle, skip
            continue
            
        f = 1.0 / denominator
        
        # Compute tangent and bitangent for this triangle
        tangent = f * (deltaUV2[1] * edge1 - deltaUV1[1] * edge2)
        bitangent = f * (-deltaUV2[0] * edge1 + deltaUV1[0] * edge2)
        
        # Accumulate tangents for each vertex of the triangle
        tangents[i1] += tangent
        tangents[i2] += tangent
        tangents[i3] += tangent
        
        bitangents[i1] += bitangent
        bitangents[i2] += bitangent
        bitangents[i3] += bitangent
    
    # Normalize tangents
    tangent_lengths = np.linalg.norm(tangents, axis=1)
    valid_tangents = tangent_lengths > 1e-8
    tangents[valid_tangents] = tangents[valid_tangents] / tangent_lengths[valid_tangents, np.newaxis]
    
    # Ensure tangents are orthogonal to normals (Gram-Schmidt process)
    for i in range(len(tangents)):
        if valid_tangents[i]:
            # Project tangent onto the plane perpendicular to normal
            tangent_proj = tangents[i] - np.dot(tangents[i], normals[i]) * normals[i]
            tangent_length = np.linalg.norm(tangent_proj)
            
            if tangent_length > 1e-8:
                tangents[i] = tangent_proj / tangent_length
            else:
                # If tangent is parallel to normal, generate a perpendicular vector
                # Use the cross product with an arbitrary vector
                arbitrary = np.array([1.0, 0.0, 0.0])
                if abs(np.dot(normals[i], arbitrary)) > 0.9:
                    arbitrary = np.array([0.0, 1.0, 0.0])
                
                tangents[i] = np.cross(normals[i], arbitrary)
                tangents[i] = tangents[i] / np.linalg.norm(tangents[i])
    
    logger.info(f"Computed tangents for {np.sum(valid_tangents)} vertices")
    return tangents


def export_glb_with_pygltflib(
    mesh: trimesh.Trimesh,
    basecolor_path: str,
    normal_map_path: str,
    output_name: str = "carpet"
) -> str:
    """
    Export mesh to GLB format using pygltflib for proper buffer view targets.
    
    This implementation ensures:
    - Proper bufferView.target values (34962 for vertex data, 34963 for indices)
    - Correct tangent attribute naming (TANGENT instead of _tangent)
    - Full glTF 2.0 compliance
    
    Args:
        mesh: Trimesh object with tangent data
        basecolor_path: Path to basecolor texture
        normal_map_path: Path to normal map texture
        output_name: Base name for output file
        
    Returns:
        Path to exported GLB file
    """
    logger.info("Exporting to GLB format using pygltflib...")
    
    # Load textures using PIL
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
            
    except Exception as e:
        raise ValueError(f"Could not load texture images: {e}")
    
    logger.info(f"Loaded textures (RGB) - Basecolor: {basecolor_image.size}, Normal: {normal_map_image.size}")
    
    # Create GLTF2 object
    gltf = GLTF2()
    
    # Prepare mesh data
    vertices = mesh.vertices.astype(np.float32)
    faces = mesh.faces.astype(np.uint32)
    uvs = mesh.visual.uv.astype(np.float32)
    normals = mesh.vertex_normals.astype(np.float32)
    
    # Get tangent data (our previous fix)
    if 'tangent' in mesh.vertex_attributes:
        tangents = mesh.vertex_attributes['tangent'].astype(np.float32)
        logger.info(f"Using computed tangent vectors: {tangents.shape}")
    else:
        logger.warning("No tangent data found in mesh - computing now")
        tangents = compute_tangents(vertices, faces, uvs, normals)
    
    # Convert tangents from VEC3 to VEC4 (add handedness component)
    tangents_vec4 = np.zeros((len(tangents), 4), dtype=np.float32)
    tangents_vec4[:, :3] = tangents  # Copy X, Y, Z components
    tangents_vec4[:, 3] = 1.0  # Set W component (handedness) to 1.0
    logger.info(f"Converted tangents to VEC4 format: {tangents_vec4.shape}")
    
    # Convert faces to indices (flatten)
    indices = faces.flatten().astype(np.uint32)
    
    # Create binary data buffer
    binary_data = bytearray()
    
    # Helper function to add data to buffer and return buffer view info
    def add_to_buffer(data, target=None):
        start_offset = len(binary_data)
        binary_data.extend(data.tobytes())
        return start_offset, len(data.tobytes())
    
    # Add vertex data to buffer
    pos_offset, pos_size = add_to_buffer(vertices, pygltflib.ARRAY_BUFFER)
    uv_offset, uv_size = add_to_buffer(uvs, pygltflib.ARRAY_BUFFER)
    normal_offset, normal_size = add_to_buffer(normals, pygltflib.ARRAY_BUFFER)
    tangent_offset, tangent_size = add_to_buffer(tangents_vec4, pygltflib.ARRAY_BUFFER)
    
    # Add index data to buffer
    index_offset, index_size = add_to_buffer(indices, pygltflib.ELEMENT_ARRAY_BUFFER)
    
    # Create buffer without URI (for binary embedding)
    buffer = Buffer()
    buffer.byteLength = len(binary_data)
    gltf.buffers = [buffer]
    
    # Embed binary data directly in GLB
    gltf.set_binary_blob(binary_data)
    
    # Create buffer views with proper targets
    buffer_views = []
    
    # Position buffer view
    pos_bv = BufferView()
    pos_bv.buffer = 0
    pos_bv.byteOffset = pos_offset
    pos_bv.byteLength = pos_size
    pos_bv.target = pygltflib.ARRAY_BUFFER  # 34962
    buffer_views.append(pos_bv)
    
    # UV buffer view
    uv_bv = BufferView()
    uv_bv.buffer = 0
    uv_bv.byteOffset = uv_offset
    uv_bv.byteLength = uv_size
    uv_bv.target = pygltflib.ARRAY_BUFFER  # 34962
    buffer_views.append(uv_bv)
    
    # Normal buffer view
    normal_bv = BufferView()
    normal_bv.buffer = 0
    normal_bv.byteOffset = normal_offset
    normal_bv.byteLength = normal_size
    normal_bv.target = pygltflib.ARRAY_BUFFER  # 34962
    buffer_views.append(normal_bv)
    
    # Tangent buffer view
    tangent_bv = BufferView()
    tangent_bv.buffer = 0
    tangent_bv.byteOffset = tangent_offset
    tangent_bv.byteLength = tangent_size
    tangent_bv.target = pygltflib.ARRAY_BUFFER  # 34962
    buffer_views.append(tangent_bv)
    
    # Index buffer view
    index_bv = BufferView()
    index_bv.buffer = 0
    index_bv.byteOffset = index_offset
    index_bv.byteLength = index_size
    index_bv.target = pygltflib.ELEMENT_ARRAY_BUFFER  # 34963
    buffer_views.append(index_bv)
    
    gltf.bufferViews = buffer_views
    
    # Create accessors
    accessors = []
    
    # Position accessor
    pos_acc = Accessor()
    pos_acc.bufferView = 0
    pos_acc.byteOffset = 0
    pos_acc.componentType = pygltflib.FLOAT
    pos_acc.count = len(vertices)
    pos_acc.type = pygltflib.VEC3
    pos_acc.min = vertices.min(axis=0).tolist()
    pos_acc.max = vertices.max(axis=0).tolist()
    accessors.append(pos_acc)
    
    # UV accessor
    uv_acc = Accessor()
    uv_acc.bufferView = 1
    uv_acc.byteOffset = 0
    uv_acc.componentType = pygltflib.FLOAT
    uv_acc.count = len(uvs)
    uv_acc.type = pygltflib.VEC2
    accessors.append(uv_acc)
    
    # Normal accessor
    normal_acc = Accessor()
    normal_acc.bufferView = 2
    normal_acc.byteOffset = 0
    normal_acc.componentType = pygltflib.FLOAT
    normal_acc.count = len(normals)
    normal_acc.type = pygltflib.VEC3
    accessors.append(normal_acc)
    
    # Tangent accessor
    tangent_acc = Accessor()
    tangent_acc.bufferView = 3
    tangent_acc.byteOffset = 0
    tangent_acc.componentType = pygltflib.FLOAT
    tangent_acc.count = len(tangents_vec4)
    tangent_acc.type = pygltflib.VEC4  # Changed from VEC3 to VEC4
    accessors.append(tangent_acc)
    
    # Index accessor
    index_acc = Accessor()
    index_acc.bufferView = 4
    index_acc.byteOffset = 0
    index_acc.componentType = pygltflib.UNSIGNED_INT
    index_acc.count = len(indices)
    index_acc.type = pygltflib.SCALAR
    accessors.append(index_acc)
    
    gltf.accessors = accessors
    
    # Create textures and images
    # Convert PIL images to bytes
    import io
    basecolor_bytes = io.BytesIO()
    basecolor_image.save(basecolor_bytes, format='PNG')
    basecolor_data = basecolor_bytes.getvalue()
    
    normal_bytes = io.BytesIO()
    normal_map_image.save(normal_bytes, format='PNG')
    normal_data = normal_bytes.getvalue()
    
    # Add texture data to buffer
    basecolor_texture_offset, basecolor_texture_size = add_to_buffer(np.frombuffer(basecolor_data, dtype=np.uint8))
    normal_texture_offset, normal_texture_size = add_to_buffer(np.frombuffer(normal_data, dtype=np.uint8))
    
    # Update buffer length
    gltf.buffers[0].byteLength = len(binary_data)
    
    # Create texture buffer views (textures don't need targets)
    basecolor_texture_bv = BufferView()
    basecolor_texture_bv.buffer = 0
    basecolor_texture_bv.byteOffset = basecolor_texture_offset
    basecolor_texture_bv.byteLength = basecolor_texture_size
    # Textures don't need targets (target=None is correct)
    buffer_views.append(basecolor_texture_bv)
    
    normal_texture_bv = BufferView()
    normal_texture_bv.buffer = 0
    normal_texture_bv.byteOffset = normal_texture_offset
    normal_texture_bv.byteLength = normal_texture_size
    # Textures don't need targets (target=None is correct)
    buffer_views.append(normal_texture_bv)
    
    # Update buffer views
    gltf.bufferViews = buffer_views
    
    # Create images
    basecolor_img = GLTFImage()
    basecolor_img.bufferView = len(buffer_views) - 2
    basecolor_img.mimeType = "image/png"
    
    normal_img = GLTFImage()
    normal_img.bufferView = len(buffer_views) - 1
    normal_img.mimeType = "image/png"
    
    gltf.images = [basecolor_img, normal_img]
    
    # Create samplers
    sampler = Sampler()
    sampler.magFilter = pygltflib.LINEAR
    sampler.minFilter = pygltflib.LINEAR_MIPMAP_LINEAR
    sampler.wrapS = pygltflib.REPEAT
    sampler.wrapT = pygltflib.REPEAT
    gltf.samplers = [sampler]
    
    # Create textures
    basecolor_texture = Texture()
    basecolor_texture.source = 0
    basecolor_texture.sampler = 0
    
    normal_texture = Texture()
    normal_texture.source = 1
    normal_texture.sampler = 0
    
    gltf.textures = [basecolor_texture, normal_texture]
    
    # Create material
    pbr = PbrMetallicRoughness()
    pbr.baseColorFactor = [1.0, 1.0, 1.0, 1.0]
    pbr.metallicFactor = 0.0
    pbr.roughnessFactor = 0.8
    
    basecolor_texture_info = TextureInfo()
    basecolor_texture_info.index = 0
    
    normal_texture_info = TextureInfo()
    normal_texture_info.index = 1
    
    material = Material()
    material.pbrMetallicRoughness = pbr
    material.pbrMetallicRoughness.baseColorTexture = basecolor_texture_info  # Add basecolor texture
    material.normalTexture = normal_texture_info
    material.name = "carpet_material"
    
    gltf.materials = [material]
    
    # Create mesh primitive with proper attributes
    attributes = Attributes()
    attributes.POSITION = 0
    attributes.TEXCOORD_0 = 1
    attributes.NORMAL = 2
    attributes.TANGENT = 3  # Proper tangent attribute name
    
    primitive = Primitive()
    primitive.attributes = attributes
    primitive.indices = 4
    primitive.material = 0
    
    mesh_obj = Mesh()
    mesh_obj.primitives = [primitive]
    mesh_obj.name = "carpet_mesh"
    
    gltf.meshes = [mesh_obj]
    
    # Create scene
    from pygltflib import Node, Scene
    node = Node()
    node.mesh = 0
    
    scene = Scene()
    scene.nodes = [0]
    
    gltf.nodes = [node]
    gltf.scenes = [scene]
    gltf.scene = 0
    
    # Generate output path
    output_filename = f"{output_name}.glb"
    output_path = Config.get_glb_path(output_filename)
    
    # Ensure output directory exists
    Config.ensure_directories()
    
    try:
        # Save GLB with binary data
        gltf.save_binary(str(output_path))
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


def export_glb(
    mesh: trimesh.Trimesh,
    basecolor_path: str,
    normal_map_path: str,
    output_name: str = "carpet"
) -> str:
    """
    Export mesh to GLB format with embedded textures using pygltflib.
    
    This function now uses pygltflib to ensure:
    - Proper bufferView.target values (34962 for vertex data, 34963 for indices)
    - Correct tangent attribute naming (TANGENT instead of _tangent)
    - Full glTF 2.0 compliance
    
    Args:
        mesh: Trimesh object with tangent data
        basecolor_path: Path to basecolor texture
        normal_map_path: Path to normal map texture
        output_name: Base name for output file
        
    Returns:
        Path to exported GLB file
    """
    # Use the new pygltflib implementation
    return export_glb_with_pygltflib(mesh, basecolor_path, normal_map_path, output_name)


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

