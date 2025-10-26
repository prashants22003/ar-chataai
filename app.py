"""
Streamlit UI for Carpet 3D Model Generator

A simple frontend interface for testing the carpet 3D model generation pipeline.
"""

import streamlit as st
import os
import time
import numpy as np
from pathlib import Path
import tempfile
from PIL import Image
import cv2

from main import process_carpet
from carpet_generation.utils.config import Config


# Page configuration
st.set_page_config(
    page_title="Carpet 3D Model Generator",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .step-container {
        padding: 1rem;
        border-radius: 8px;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'corrected_image_path' not in st.session_state:
        st.session_state.corrected_image_path = None
    if 'basecolor_path' not in st.session_state:
        st.session_state.basecolor_path = None
    if 'normal_map_path' not in st.session_state:
        st.session_state.normal_map_path = None
    if 'glb_path' not in st.session_state:
        st.session_state.glb_path = None
    if 'usdz_path' not in st.session_state:
        st.session_state.usdz_path = None
    if 'error_message' not in st.session_state:
        st.session_state.error_message = None


def reset_results():
    """Clear previous results."""
    st.session_state.corrected_image_path = None
    st.session_state.basecolor_path = None
    st.session_state.normal_map_path = None
    st.session_state.glb_path = None
    st.session_state.usdz_path = None
    st.session_state.error_message = None
    # Reset corners when new image is uploaded
    if 'corners' in st.session_state:
        st.session_state.corners = []


def process_carpet_with_progress(input_image_path, progress_bar, status_text):
    """
    Process carpet image with real-time progress updates.
    
    Args:
        input_image_path: Path to uploaded image
        progress_bar: Streamlit progress bar object
        status_text: Streamlit text object for status updates
    """
    try:
        # Ensure output directories exist
        Config.ensure_directories()
        
        # Step 1: Perspective Correction
        status_text.text("🔄 Step 1/5: Applying perspective correction...")
        progress_bar.progress(0.1)
        
        # Debug: Check input image
        if not os.path.exists(input_image_path):
            raise ValueError(f"Input image not found: {input_image_path}")
        
        from carpet_generation.image_processing import correct_perspective
        # Use manual corners if available, otherwise None (will use full image)
        manual_corners = st.session_state.corners[:4] if st.session_state.corners else None
        corrected_image, corrected_path = correct_perspective(input_image_path, manual_corners=manual_corners)
        
        # Debug: Check if correction worked
        if corrected_image is None or corrected_image.size == 0:
            raise ValueError("Perspective correction failed - no image returned")
        
        st.session_state.corrected_image_path = corrected_path
        progress_bar.progress(0.25)
        time.sleep(0.1)  # Brief pause for UI update
        
        # Step 2: Generate Basecolor
        status_text.text("🎨 Step 2/5: Generating basecolor texture...")
        progress_bar.progress(0.3)
        
        from carpet_generation.image_processing import generate_basecolor
        output_name = Path(input_image_path).stem
        basecolor_path = generate_basecolor(corrected_image, output_name=output_name)
        
        # Debug: Check if basecolor was generated
        if not os.path.exists(basecolor_path):
            raise ValueError(f"Basecolor generation failed - file not created: {basecolor_path}")
        
        st.session_state.basecolor_path = basecolor_path
        progress_bar.progress(0.5)
        time.sleep(0.1)
        
        # Step 3: Generate Normal Map
        status_text.text("🗺️ Step 3/5: Generating normal map...")
        progress_bar.progress(0.55)
        
        from carpet_generation.image_processing import generate_normal_map
        normal_map_path = generate_normal_map(basecolor_path, output_name=output_name)
        st.session_state.normal_map_path = normal_map_path
        progress_bar.progress(0.7)
        time.sleep(0.1)
        
        # Step 4 & 5: Create 3D Model and Export
        status_text.text("🔨 Step 4/5: Creating 3D mesh with displaced geometry...")
        progress_bar.progress(0.75)
        
        from carpet_generation.model_generation import generate_carpet_model
        
        status_text.text("📦 Step 5/5: Exporting to GLB format...")
        progress_bar.progress(0.85)
        
        output_name = Path(input_image_path).stem
        glb_path, usdz_path = generate_carpet_model(
            basecolor_path,
            normal_map_path,
            output_name
        )
        st.session_state.glb_path = glb_path
        st.session_state.usdz_path = usdz_path
        progress_bar.progress(1.0)
        
        status_text.text("✅ Processing complete!")
        return True
        
    except Exception as e:
        st.session_state.error_message = str(e)
        status_text.text("❌ Processing failed!")
        return False


def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>🏠 Carpet 3D Model Generator</h1>
            <p>Upload a carpet image to generate AR-ready 3D models</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Instructions
    with st.expander("ℹ️ How to use", expanded=False):
        st.markdown("""
        ### Instructions:
        1. **Upload** a carpet image (JPG, PNG, JPEG)
        2. Click **Generate 3D Model** button
        3. Wait for processing (typically 10-20 seconds)
        4. **Download** the GLB file for AR viewing
        
        ### Tips for best results:
        - Use good lighting with minimal shadows
        - Capture the entire carpet in the frame
        - Take photo from above for better perspective correction
        - Higher resolution images produce better quality models
        """)
    
    # Debug section
    with st.expander("🔧 Debug Info", expanded=False):
        st.markdown("""
        ### Debug Information:
        - **Input Image**: Check if uploaded file is saved correctly
        - **Processing Steps**: Each step validates its output
        - **File Paths**: Verify all intermediate files are created
        - **Error Messages**: Detailed error reporting
        """)
    
    st.markdown("---")
    
    # File uploader
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        uploaded_file = st.file_uploader(
            "Upload Carpet Image",
            type=['jpg', 'jpeg', 'png'],
            help="Select a clear image of your carpet",
            on_change=reset_results
        )
    
    if uploaded_file is not None:
        # Initialize corner selection state
        if 'corners' not in st.session_state:
            st.session_state.corners = []
        
        # Load image for processing
        image = Image.open(uploaded_file)
        
        # Interactive corner selection
        st.markdown("### 🎯 Corner Selection (Optional)")
        st.markdown("""
        **Select carpet corners for perspective correction:**
        - Use the coordinate inputs below to add corners
        - Order: Top-left → Top-right → Bottom-right → Bottom-left
        - Leave empty to use the entire image as carpet texture
        """)
        
        # Create interactive image with corner markers
        def draw_corners_on_image(img, corners):
            """Draw corner markers on the image."""
            import cv2
            img_array = np.array(img)
            img_with_corners = img_array.copy()
            
            # Draw corner markers
            for i, (x, y) in enumerate(corners):
                if i < 4:
                    # Valid corners - green with number
                    cv2.circle(img_with_corners, (x, y), 12, (0, 255, 0), -1)
                    cv2.circle(img_with_corners, (x, y), 12, (255, 255, 255), 2)
                    cv2.putText(img_with_corners, str(i+1), (x-8, y+4), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                else:
                    # Extra corners - red
                    cv2.circle(img_with_corners, (x, y), 12, (0, 0, 255), -1)
                    cv2.circle(img_with_corners, (x, y), 12, (255, 255, 255), 2)
            
            return img_with_corners
        
        # Layout: Image viewer (2/3 width) + Corner form (1/3 width)
        col_image, col_form = st.columns([2, 1])
        
        with col_image:
            # Display image with corner markers (centered in 2/3 column)
            if st.session_state.corners:
                img_with_corners = draw_corners_on_image(image, st.session_state.corners)
                st.image(img_with_corners, caption=f"Selected corners: {len(st.session_state.corners)}/4", width='stretch')
            else:
                st.image(image, caption="Click on the image to select carpet corners", width='stretch')
        
        with col_form:
            # Corner management form (1/3 width)
            st.markdown("**Add Corner:**")
            
            # Corner input with better UX
            corner_col1, corner_col2 = st.columns(2)
            with corner_col1:
                corner_x = st.number_input("X coordinate", min_value=0, max_value=image.width-1, 
                                         value=0, step=10, key="corner_x")
            with corner_col2:
                corner_y = st.number_input("Y coordinate", min_value=0, max_value=image.height-1, 
                                         value=0, step=10, key="corner_y")
            
            # Show current mouse position hint
            st.caption(f"Image size: {image.width} × {image.height}")
            
            if st.button("➕ Add Corner", disabled=len(st.session_state.corners) >= 4, type="primary"):
                st.session_state.corners.append((corner_x, corner_y))
                st.rerun()
            
            st.markdown("**Manage Corners:**")
            col_remove, col_clear = st.columns(2)
            with col_remove:
                if st.button("🗑️ Remove Last", disabled=len(st.session_state.corners) == 0):
                    st.session_state.corners.pop()
                    st.rerun()
            with col_clear:
                if st.button("🗑️ Clear All", disabled=len(st.session_state.corners) == 0):
                    st.session_state.corners = []
                    st.rerun()
        
        # Show current corners and suggestions
        if st.session_state.corners:
            st.markdown("**Current Corners:**")
            for i, (x, y) in enumerate(st.session_state.corners):
                status = "✅" if i < 4 else "⚠️"
                corner_names = ["Top-left", "Top-right", "Bottom-right", "Bottom-left"]
                corner_name = corner_names[i] if i < 4 else "Extra"
                st.write(f"{status} {i+1}. {corner_name}: ({x}, {y})")
            
            if len(st.session_state.corners) == 4:
                st.success("✅ 4 corners selected! Ready to generate 3D model.")
            elif len(st.session_state.corners) > 4:
                st.warning(f"⚠️ {len(st.session_state.corners)} corners selected (only first 4 will be used)")
        else:
            st.info("No corners selected - will use entire image as carpet texture")
            
            # Show corner suggestions
            with st.expander("💡 Corner Selection Tips", expanded=False):
                st.markdown("""
                **Suggested corner positions for a rectangular carpet:**
                - **Top-left**: Upper-left corner of the carpet
                - **Top-right**: Upper-right corner of the carpet  
                - **Bottom-right**: Lower-right corner of the carpet
                - **Bottom-left**: Lower-left corner of the carpet
                
                **Tips:**
                - Look at the image above to estimate coordinates
                - Start with corners that are clearly visible
                - You can adjust coordinates after adding them
                """)
        
        st.markdown("---")
        
        # Generate button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            generate_button = st.button(
                "🚀 Generate 3D Model",
                type="primary",
                disabled=st.session_state.processing,
                width='stretch'
            )
        
        # Process image when button is clicked
        if generate_button and not st.session_state.processing:
            st.session_state.processing = True
            reset_results()
            
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # Debug: Check if file was saved correctly
            if not os.path.exists(tmp_path):
                st.error("Failed to save uploaded file")
                st.session_state.processing = False
                return
            
            # Processing section
            st.markdown("### ⚙️ Processing")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Process the carpet
            success = process_carpet_with_progress(tmp_path, progress_bar, status_text)
            
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass
            
            st.session_state.processing = False
            
            # Show error if processing failed
            if not success:
                st.markdown(f"""
                    <div class="error-box">
                        <h4>❌ Error</h4>
                        <p>{st.session_state.error_message}</p>
                        <p><small>Please try again with a different image or check the error details above.</small></p>
                    </div>
                """, unsafe_allow_html=True)
        
        # Display results if processing was successful
        if st.session_state.glb_path and not st.session_state.error_message:
            st.markdown("---")
            
            # Success message
            st.markdown("""
                <div class="success-box">
                    <h4>✅ Success!</h4>
                    <p>Your 3D carpet model has been generated successfully in both GLB and USDZ formats.</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Display intermediate results
            st.markdown("### 🖼️ Processing Results")
            
            # Debug info
            with st.expander("🔍 Debug Information", expanded=False):
                st.write(f"**Corrected Image**: {st.session_state.corrected_image_path}")
                st.write(f"**Basecolor Path**: {st.session_state.basecolor_path}")
                st.write(f"**Normal Map Path**: {st.session_state.normal_map_path}")
                st.write(f"**GLB Path**: {st.session_state.glb_path}")
                st.write(f"**USDZ Path**: {st.session_state.usdz_path}")
                
                # Check file sizes
                if st.session_state.corrected_image_path and os.path.exists(st.session_state.corrected_image_path):
                    size = os.path.getsize(st.session_state.corrected_image_path) / 1024
                    st.write(f"**Corrected Image Size**: {size:.1f} KB")
                
                if st.session_state.basecolor_path and os.path.exists(st.session_state.basecolor_path):
                    size = os.path.getsize(st.session_state.basecolor_path) / 1024
                    st.write(f"**Basecolor Size**: {size:.1f} KB")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.session_state.corrected_image_path and os.path.exists(st.session_state.corrected_image_path):
                    # Load image with OpenCV and convert BGR to RGB
                    import cv2
                    img_bgr = cv2.imread(st.session_state.corrected_image_path)
                    if img_bgr is not None:
                        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                        # Debug info
                        unique_colors = len(np.unique(img_rgb.reshape(-1, img_rgb.shape[2]), axis=0))
                        st.write(f"Debug: {unique_colors} unique colors, shape: {img_rgb.shape}")
                        st.image(
                            img_rgb,
                            caption="Perspective Corrected",
                            width='stretch'
                        )
                    else:
                        st.error("Could not load corrected image")
                else:
                    st.error("Corrected image not found")
            
            with col2:
                if st.session_state.basecolor_path and os.path.exists(st.session_state.basecolor_path):
                    # Load image with OpenCV and convert BGR to RGB
                    img_bgr = cv2.imread(st.session_state.basecolor_path)
                    if img_bgr is not None:
                        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                        # Debug info
                        unique_colors = len(np.unique(img_rgb.reshape(-1, img_rgb.shape[2]), axis=0))
                        st.write(f"Debug: {unique_colors} unique colors, shape: {img_rgb.shape}")
                        st.image(
                            img_rgb,
                            caption="Basecolor Texture",
                            width='stretch'
                        )
                    else:
                        st.error("Could not load basecolor texture")
                else:
                    st.error("Basecolor texture not found")
            
            with col3:
                if st.session_state.normal_map_path and os.path.exists(st.session_state.normal_map_path):
                    # Load image with OpenCV and convert BGR to RGB
                    img_bgr = cv2.imread(st.session_state.normal_map_path)
                    if img_bgr is not None:
                        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                        # Debug info
                        unique_colors = len(np.unique(img_rgb.reshape(-1, img_rgb.shape[2]), axis=0))
                        st.write(f"Debug: {unique_colors} unique colors, shape: {img_rgb.shape}")
                        st.image(
                            img_rgb,
                            caption="Normal Map",
                            width='stretch'
                        )
                    else:
                        st.error("Could not load normal map")
                else:
                    st.error("Normal map not found")
            
            st.markdown("---")
            
            # Download section
            st.markdown("### 📥 Download 3D Model")
            
            # Create two columns for download buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.session_state.glb_path and os.path.exists(st.session_state.glb_path):
                    with open(st.session_state.glb_path, 'rb') as f:
                        glb_data = f.read()
                    
                    file_size = len(glb_data) / (1024 * 1024)  # Size in MB
                    
                    st.download_button(
                        label=f"⬇️ Download GLB Model ({file_size:.2f} MB)",
                        data=glb_data,
                        file_name=Path(st.session_state.glb_path).name,
                        mime="model/gltf-binary",
                        type="primary",
                        use_container_width=True
                    )
                    
                    st.caption("💡 Compatible with Android ARCore, iOS ARKit, web viewers, and most 3D applications")
                else:
                    st.error("GLB file not found")
            
            with col2:
                if st.session_state.usdz_path and os.path.exists(st.session_state.usdz_path):
                    with open(st.session_state.usdz_path, 'rb') as f:
                        usdz_data = f.read()
                    
                    file_size = len(usdz_data) / (1024 * 1024)  # Size in MB
                    
                    st.download_button(
                        label=f"⬇️ Download USDZ Model ({file_size:.2f} MB)",
                        data=usdz_data,
                        file_name=Path(st.session_state.usdz_path).name,
                        mime="model/vnd.usdz+zip",
                        type="secondary",
                        use_container_width=True
                    )
                    
                    st.caption("💡 Optimized for iOS ARKit and Apple AR experiences")
                else:
                    st.error("USDZ file not found")
    
    else:
        # Show placeholder when no file is uploaded
        st.info("👆 Please upload a carpet image to get started")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; padding: 1rem;">
            <small>Carpet 3D Model Generator v0.1.0 | Prototype</small>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

