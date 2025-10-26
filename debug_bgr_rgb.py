"""
Quick test to verify BGR to RGB conversion works correctly.
"""

import streamlit as st
import cv2
import numpy as np
from pathlib import Path

st.title("BGR to RGB Conversion Test")

# Test with the latest generated files
texture_dir = Path("static/textures")
latest_files = list(texture_dir.glob("tmpf2tq53ay_*.png"))

if latest_files:
    st.write("Testing latest generated files:")
    
    for file_path in latest_files:
        st.write(f"**{file_path.name}**")
        
        # Load with OpenCV (BGR)
        img_bgr = cv2.imread(str(file_path))
        if img_bgr is not None:
            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            
            # Display both versions
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**BGR (OpenCV default)**")
                st.image(img_bgr, width=300)
            
            with col2:
                st.write("**RGB (converted)**")
                st.image(img_rgb, width=300)
            
            # Show statistics
            st.write(f"Shape: {img_rgb.shape}")
            st.write(f"Unique colors: {len(np.unique(img_rgb.reshape(-1, img_rgb.shape[2]), axis=0))}")
            st.write(f"Min/Max: {img_rgb.min()}/{img_rgb.max()}")
            
            # Check if it's actually a solid color
            unique_colors = len(np.unique(img_rgb.reshape(-1, img_rgb.shape[2]), axis=0))
            if unique_colors < 10:
                st.error(f"⚠️ This looks like a solid color! Only {unique_colors} unique colors.")
            else:
                st.success(f"✅ This has texture data! {unique_colors} unique colors.")
            
            st.write("---")
        else:
            st.error(f"Could not load {file_path}")
else:
    st.error("No latest files found. Try processing an image first.")

