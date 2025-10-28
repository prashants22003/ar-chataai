#!/usr/bin/env python3
"""
AR-Chataai Unified Backend Startup Script
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the unified AR-Chataai backend."""
    
    # Get the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("🚀 Starting AR-Chataai Unified Backend...")
    print("=" * 60)
    
    # Check if .env file exists
    env_file = script_dir / ".env"
    if not env_file.exists():
        print("⚠️  No .env file found!")
        print("📝 Please create a .env file with your Supabase credentials:")
        print("   PROJECT_URL=https://your-project-id.supabase.co")
        print("   API_KEY=your_supabase_anon_key_here")
        print("   PORT=3000")
        return
    
    # Check if requirements are installed
    try:
        import fastapi
        import uvicorn
        import supabase
        print("✅ Dependencies are installed")
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("📦 Installing dependencies...")
        
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return
    
    # Start the unified backend
    print("🌐 Starting unified backend...")
    print("📍 Backend will be available at: http://localhost:3000")
    print("📚 API Documentation: http://localhost:3000/docs")
    print("🔍 Health Check: http://localhost:3000/api/health")
    print("🎯 Model Generation: Integrated")
    print("=" * 60)
    
    try:
        # Import and run the FastAPI app
        from main import app
        import uvicorn
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=3000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Backend stopped by user")
    except Exception as e:
        print(f"❌ Backend failed to start: {e}")

if __name__ == "__main__":
    main()
