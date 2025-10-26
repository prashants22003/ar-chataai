# Carpet 3D Model Generator

An automated pipeline that converts carpet images into 3D models with AR support for iOS and Android devices.

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch Streamlit UI
streamlit run app.py

# Open browser to http://localhost:8501
# Upload carpet image → Generate → Download GLB/USDZ files
```

---

## Features

- **Automatic Perspective Correction** - Detects carpet corners and applies perspective transform
- **Texture Generation** - Creates optimized basecolor textures with enhancement and denoising
- **Normal Map Creation** - Generates normal maps using computer vision techniques
- **Displaced Geometry** - Creates realistic 3D meshes with surface detail
- **Streamlit Web UI** - Simple interface with real-time progress tracking
- **GLB Export** - Android/Web-ready AR models with embedded textures
- **USDZ Export** - iOS-ready AR models (requires converter - see USDZ_SETUP_GUIDE.md)

---

## Project Structure

```
carpet_generation/
├── image_processing/
│   ├── perspective.py      # Perspective correction
│   ├── texture_gen.py      # Basecolor generation
│   └── normal_map.py       # Normal map generation
├── model_generation/
│   └── generate_model.py   # 3D mesh creation and export
└── utils/
    └── config.py           # Configuration settings

static/
├── uploads/                # Input images
├── textures/               # Generated textures
├── glb_exports/            # GLB output files (Android/Web)
└── usdz_exports/           # USDZ output files (iOS)
```

---

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify installation** (optional):
   ```bash
   python verify_installation.py
   ```

---

## Usage

### Streamlit Web UI (Recommended)

```bash
streamlit run app.py
```

Then in your browser:
1. Upload a carpet image (JPG, PNG)
2. Click "Generate 3D Model"
3. Watch real-time progress (5 steps)
4. Preview intermediate results (corrected image, basecolor, normal map)
5. Download GLB (Android/Web) and USDZ (iOS) files

**Processing time**: ~10-20 seconds per image

**USDZ Support**: To enable iOS USDZ export, install a converter (see below)

### Command Line

```bash
# Basic usage
python main.py --input path/to/carpet.jpg

# With custom settings
python main.py --input carpet.jpg --resolution 2048 --subdivisions 200 --displacement 0.02
```

### Python API

```python
from main import process_carpet

glb_path, usdz_path = process_carpet("carpet.jpg")
print(f"Model saved to: {glb_path}")
```

---

## Configuration

Edit `carpet_generation/utils/config.py` to customize:

- **Texture Resolution**: Default 2048x2048
- **Mesh Subdivisions**: Default 200x200 vertices
- **Displacement Scale**: Default 0.02 meters
- **Material Properties**: Roughness (0.8), Metallic (0.0)

---

## Tips for Best Results

**Photography**:
- Use even, natural lighting
- Shoot from directly above when possible
- Ensure entire carpet is visible
- Clear background with good contrast
- Higher resolution images = better quality

**Good Candidates**:
- Carpets with clear edges
- Distinct patterns
- Good lighting without harsh shadows

**Challenging**:
- Very dark carpets
- Busy/cluttered backgrounds
- Extreme angles or heavy shadows

---

## Output Files

Each processed image generates:
- **Corrected Image** - Perspective-corrected view
- **Basecolor Texture** - Enhanced color texture (PNG, ~3-8 MB)
- **Normal Map** - Surface detail texture (PNG, ~3-8 MB)
- **GLB Model** - 3D model for Android/Web AR (~10-20 MB)
- **USDZ Model** - 3D model for iOS AR (~10-20 MB, if converter installed)

Files are saved in `static/` subdirectories.

---

## USDZ Export Setup (iOS Support)

The pipeline supports automatic USDZ conversion for iOS AR. Choose one method:

### Quick Setup (Easiest):
```bash
# Install Aspose.3D (free trial, commercial license for production)
pip install aspose-3d
```

### Free Setup:
1. Install Blender from https://www.blender.org/download/
2. Add Blender to your system PATH
3. Restart your application

### Without Converter:
- GLB files will still generate successfully
- USDZ download will show installation instructions
- Manual conversion available via online tools

**For detailed instructions, see:** `QUICK_USDZ_SETUP.md` and `USDZ_SETUP_GUIDE.md`

---

## AR Viewing

### Android (GLB)
1. Transfer GLB file to your phone
2. Open with AR viewer app (Google Scene Viewer, AR Viewer, etc.)
3. Point at floor and place model

### iOS (USDZ)
1. Install a USDZ converter (see USDZ Export Setup above)
2. Transfer USDZ file to your iPhone/iPad via AirDrop
3. Tap to open in AR Quick Look
4. Point at floor and place model

**Without converter:**
- Use manual conversion tools (Reality Converter, Blender, or online)
- Or transfer GLB and convert on device using compatible apps

---

## Troubleshooting

### App won't start
```bash
pip install streamlit
python -m streamlit run app.py
```

### Processing fails
- Check image quality and lighting
- Ensure carpet is clearly visible
- Try different image
- Check error message in UI

### Slow processing
- Normal for high-resolution images
- Denoising step takes 3-5 seconds
- Total time: 10-20 seconds typical
- Reduce `--resolution` for faster processing

### Corner detection fails
- App will use entire image as fallback
- For better results, use manual corner specification (coming in future update)

---

## Performance

| Component | Time | Notes |
|-----------|------|-------|
| Perspective Correction | ~1-2s | Auto corner detection |
| Basecolor Generation | ~3-5s | Denoising is slowest |
| Normal Map Generation | ~1-2s | Sobel filter based |
| 3D Mesh Creation | ~2-4s | 200x200 vertices |
| GLB Export | ~1-2s | Embedded textures |
| **Total** | **10-20s** | Per image |

**Memory**: ~500MB - 1GB peak usage  
**File Sizes**: GLB models 10-20 MB with embedded textures

---

## Current Limitations

- USDZ export requires manual conversion (iOS)
- Single image processing only (no batch mode)
- Traditional CV normal maps (not AI-powered)
- Corner detection may fail with low-contrast images

These are acceptable for prototyping and will be addressed in future updates.

---

## Future Enhancements

- AI-powered normal map generation (MiDaS, DPT)
- Automatic USDZ conversion for iOS
- Batch processing support
- Manual corner specification in UI
- 3D model preview in browser
- Parameter controls in UI
- REST API for mobile integration

---

## Dependencies

- Python 3.8+
- opencv-python (image processing)
- numpy (numerical operations)
- Pillow (image handling)
- trimesh (3D mesh manipulation)
- streamlit (web UI)
- scipy (scientific computing)

See `requirements.txt` for complete list.

---

## License

This project is provided as-is for educational and commercial use.

---

## Support

For issues or questions, check the terminal output for detailed error messages and stack traces.

**Current Status**: v0.1.0 - Prototype ready for testing
