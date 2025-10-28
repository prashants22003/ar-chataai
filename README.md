# Carpet 3D Model Generator

An automated pipeline that converts carpet images into 3D models with AR support for iOS and Android devices.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch Streamlit UI
streamlit run ui/app.py

# Open browser to http://localhost:8501
# Upload carpet image → Generate → Download GLB/USDZ files
```

## Project Structure

```
AR-Chataai/
├── src/
│   ├── model_pipeline/          # 3D Model Generation
│   │   ├── image_processing/
│   │   ├── model_generation/
│   │   └── utils/
│   └── link_pipeline/           # Shareable Link Generation
│       └── supabase_upload.py
│
├── ui/                          # Streamlit Interface
│   └── app.py
│
├── tests/                       # Test Scripts
│   └── ...
│
├── output/                      # Generated Files
│   └── static/
│       ├── basecolor/
│       ├── corrected/
│       ├── normal/
│       ├── glb_exports/
│       └── usdz_exports/
│
└── Testing Images/               # Sample Images
```

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Supabase** (optional, for shareable links):
   - Create `.env` file in project root with:
     ```bash
     PROJECT_URL=https://your-project-id.supabase.co
     API_KEY=your-anon-key-here
     AR_VIEWER_URL=http://your-viewer-url.com  # Optional: For AR viewer links
     ```
   - Set up storage bucket named `3d-models` (make it public)
   - Run `fix_permissions.sql` in Supabase SQL Editor

## Usage

### Streamlit Web UI (Recommended)

```bash
streamlit run ui/app.py
```

Then in your browser:
1. Upload a carpet image (JPG, PNG)
2. Click "Generate 3D Model"
3. Watch real-time progress (5 steps)
4. Preview intermediate results
5. Download GLB/USDZ files
6. (Optional) Upload to cloud for shareable AR link

**Processing time**: ~10-20 seconds per image

### Command Line

```bash
# Run from project root
python src/model_pipeline/main.py --input Testing\ Images/carpet.jpg
```

## Features

- **Automatic Perspective Correction** - Detects carpet corners
- **Texture Generation** - Creates optimized basecolor textures
- **Normal Map Creation** - Generates surface detail maps
- **Displaced Geometry** - Creates realistic 3D meshes
- **Shareable AR Links** - Upload to Supabase for cloud sharing
- **Streamlit Web UI** - Simple interface with progress tracking
- **GLB/USDZ Export** - Android/iOS AR-ready models

## Configuration

Edit `src/model_pipeline/utils/config.py` to customize:
- Texture Resolution (default 2048x2048)
- Mesh Subdivisions (default 200x200)
- Displacement Scale
- Material Properties

## Output Files

Each processed image generates:
- Corrected Image (perspective-corrected)
- Basecolor Texture (enhanced colors)
- Normal Map (surface detail)
- GLB Model (Android/Web AR, ~10-20 MB)
- USDZ Model (iOS AR, ~10-20 MB)

Files are saved in `output/static/` subdirectories.

## Shareable AR Links

1. Generate 3D model in Streamlit
2. Click "Upload to Cloud & Generate Shareable Link"
3. Copy the generated link
4. Share with others to view in AR

Requires Supabase setup (see requirements above).

## Troubleshooting

**App won't start**:
```bash
pip install streamlit
streamlit run ui/app.py
```

**Slow processing**: Normal for high-res images (10-20s typical)

**Shareable links not working**: Check Supabase configuration in `.env` file

## Dependencies

See `requirements.txt` for complete list.

## Current Status

v0.2.0 - Restructured with separate pipelines for model generation and link sharing