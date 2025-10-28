# AR-Chataai Unified Backend

A complete Python-based backend for 3D carpet model generation and AR viewing, unified in a single `src/` directory.

## 🏗 **Unified Structure**

```
src/
├── main.py                    # Main backend entry point
├── config.py                  # Unified configuration
├── requirements.txt           # All Python dependencies
├── start_backend.py          # Easy startup script
├── api/                      # API server components
│   ├── routes/
│   │   ├── upload.py         # File upload & model generation
│   │   ├── ar_viewer.py     # AR viewer serving
│   │   └── health.py         # Health monitoring
│   ├── models/               # Pydantic models
│   └── services/             # Business logic services
│       ├── supabase_client.py
│       ├── file_manager.py
│       └── model_generator.py
├── model_generation/          # 3D model generation pipeline
│   ├── main.py
│   ├── utils/
│   ├── model_generation/
│   └── ...
├── static/                   # AR viewer static files
└── uploads/                  # Temporary uploads
```

## 🚀 **Quick Start**

1. **Navigate to src directory**:
   ```bash
   cd src
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   # Create .env file with your Supabase credentials
   echo "PROJECT_URL=https://your-project-id.supabase.co" > .env
   echo "API_KEY=your_supabase_anon_key_here" >> .env
   echo "PORT=3000" >> .env
   ```

4. **Start the backend**:
   ```bash
   python main.py
   # OR
   python start_backend.py
   ```

## 🎯 **Key Features**

### **Unified Backend**
- **Single entry point**: `python main.py` starts everything
- **Integrated components**: API server + model generation
- **Unified configuration**: Single config for all components
- **Direct Python integration**: No subprocess overhead

### **API Server (FastAPI)**
- **Modern web framework** with automatic documentation
- **File upload handling** with validation
- **Supabase integration** for file storage
- **AR viewer serving** with embedded model-viewer
- **Health monitoring** with system information

### **Model Generation**
- **Direct Python calls** to model generation pipeline
- **Async processing** with background tasks
- **Custom dimensions** support
- **Perspective correction** toggle
- **Automatic cleanup** of temporary files

### **AR Viewer**
- **Web-based AR experience** using model-viewer
- **Responsive design** with modern UI
- **"View in Room" functionality** for AR
- **Interactive 3D preview**

## 📡 **API Endpoints**

### **Upload & Model Generation**
- `POST /api/upload/generate-ar-link` - Upload image + dimensions → AR link
- `GET /api/upload/stats` - Upload statistics

### **AR Viewer**
- `GET /api/ar-viewer` - Serve AR viewer page

### **Health & Monitoring**
- `GET /api/health` - Basic health check
- `GET /api/health/detailed` - Detailed system health
- `GET /api/health/supabase` - Supabase connection check
- `GET /api/health/system` - System information

### **Documentation**
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## 🔧 **Configuration**

Create a `.env` file with:

```env
# Supabase Configuration
PROJECT_URL=https://your-project-id.supabase.co
API_KEY=your_supabase_anon_key_here

# Server Configuration
PORT=3000
HOST=0.0.0.0
DEBUG=false

# Model Generation Settings
TEXTURE_RESOLUTION=1024
MESH_SUBDIVISION=20
DISPLACEMENT_SCALE=0.02
CARPET_WIDTH=2.0
CARPET_HEIGHT=3.0
CARPET_THICKNESS=0.005
```

## 🔄 **API Usage Example**

### **Upload Image and Generate AR Link**

```bash
curl -X POST "http://localhost:3000/api/upload/generate-ar-link" \
  -F "image=@carpet.jpg" \
  -F "length=2.0" \
  -F "width=3.0" \
  -F "thickness=5.0" \
  -F "skip_perspective=true"
```

**Response**:
```json
{
  "success": true,
  "filename": "carpet_abc12345.glb",
  "public_url": "https://supabase.co/storage/v1/object/public/3d-models/carpet_abc12345.glb",
  "ar_viewer_link": "/api/ar-viewer?model_url=https://...",
  "size": 2048576,
  "dimensions": {
    "length": 2.0,
    "width": 3.0,
    "thickness": 5.0
  },
  "message": "3D model generated and AR link created successfully!"
}
```

## 🎯 **Benefits of Unified Structure**

✅ **Single Backend Directory**: Everything in `src/`  
✅ **One Entry Point**: `python main.py` starts everything  
✅ **Unified Configuration**: Single config for all components  
✅ **Direct Integration**: No subprocess spawning overhead  
✅ **Easier Deployment**: Single directory to deploy  
✅ **Better Organization**: API and model generation as integrated components  
✅ **Simplified Maintenance**: One codebase to maintain  

## 🧪 **Testing**

```bash
# Health check
curl http://localhost:3000/api/health

# Detailed health check
curl http://localhost:3000/api/health/detailed

# Upload test
curl -X POST "http://localhost:3000/api/upload/generate-ar-link" \
  -F "image=@test_image.jpg" \
  -F "length=2.0" \
  -F "width=3.0" \
  -F "thickness=5.0"
```

## 🚀 **Deployment**

### **Local Development**
```bash
cd src
python main.py
```

### **Production**
```bash
cd src
uvicorn main:app --host 0.0.0.0 --port 3000 --workers 4
```

### **Docker (Optional)**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY src/ .
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
```

## 📝 **Logs & Monitoring**

The unified backend provides comprehensive logging:
- **Startup logs**: Service initialization and health checks
- **Request logs**: API endpoint access and processing
- **Model generation logs**: 3D model creation progress
- **Error tracking**: Detailed error information
- **System monitoring**: Resource usage and health status

## 🔗 **Integration**

The unified backend seamlessly integrates with:
- **Frontend**: HTML/CSS/JavaScript client in `client/` directory
- **Model Generation**: Direct Python model generation pipeline
- **Supabase**: File storage and public URLs
- **AR Viewer**: Web-based AR experience

## 🎉 **Ready to Use!**

The unified backend is now complete and ready for production use! 

**Start the backend**:
```bash
cd src
python main.py
```

**Access the API**:
- Backend: http://localhost:3000
- API Docs: http://localhost:3000/docs
- Health Check: http://localhost:3000/api/health

The unified structure makes the backend much cleaner, easier to maintain, and simpler to deploy! 🚀