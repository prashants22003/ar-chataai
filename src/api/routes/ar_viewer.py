"""
AR Viewer routes for serving the AR viewer interface
"""

import logging
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def serve_ar_viewer(model_url: str = Query(..., description="URL of the 3D model")):
    """
    Serve the AR viewer page with embedded model.
    """
    if not model_url:
        return HTMLResponse(content="""
            <html>
                <head>
                    <title>AR Viewer - Error</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .error { color: #e74c3c; }
                        .code { background: #f5f5f5; padding: 10px; border-radius: 4px; font-family: monospace; }
                    </style>
                </head>
                <body>
                    <h1>AR Viewer</h1>
                    <p class="error">Error: No model URL provided</p>
                    <p>Please provide a model URL as a query parameter:</p>
                    <div class="code">?model_url=YOUR_MODEL_URL</div>
                </body>
            </html>
        """, status_code=400)
    
    # Return AR viewer HTML with embedded model URL
    ar_viewer_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AR Model Viewer</title>
            <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: #333;
                    overflow-x: hidden;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 40px;
                    padding: 40px 20px;
                }}
                
                .title {{
                    font-size: 3rem;
                    font-weight: 700;
                    color: white;
                    margin-bottom: 10px;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
                }}
                
                .subtitle {{
                    font-size: 1.2rem;
                    color: rgba(255,255,255,0.9);
                    font-weight: 300;
                }}
                
                .model-container {{
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    margin-bottom: 60px;
                }}
                
                .model-wrapper {{
                    width: 100%;
                    max-width: 600px;
                    height: 500px;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    overflow: hidden;
                    margin-bottom: 30px;
                    position: relative;
                }}
                
                model-viewer {{
                    width: 100%;
                    height: 100%;
                    background: #f8f9fa;
                }}
                
                .ar-section {{
                    text-align: center;
                    margin-bottom: 40px;
                }}
                
                .ar-button {{
                    background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                    border: none;
                    padding: 30px 50px;
                    border-radius: 20px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 20px;
                    margin: 0 auto 20px;
                    transition: all 0.3s ease;
                    box-shadow: 0 10px 30px rgba(255,107,107,0.3);
                    min-width: 300px;
                    justify-content: center;
                }}
                
                .ar-button:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 15px 40px rgba(255,107,107,0.4);
                }}
                
                .ar-icon {{
                    font-size: 3rem;
                    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
                }}
                
                .ar-content h3 {{
                    color: white;
                    font-size: 1.8rem;
                    font-weight: 700;
                    margin-bottom: 5px;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }}
                
                .ar-content p {{
                    color: rgba(255,255,255,0.9);
                    font-size: 1.1rem;
                    font-weight: 300;
                }}
                
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: rgba(255,255,255,0.7);
                    font-size: 0.9rem;
                }}
                
                @media (max-width: 768px) {{
                    .title {{ font-size: 2.2rem; }}
                    .model-wrapper {{ height: 400px; }}
                    .ar-button {{ padding: 25px 30px; min-width: 280px; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <header class="header">
                    <h1 class="title">3D Model Viewer</h1>
                    <p class="subtitle">Experience your model in Augmented Reality</p>
                </header>

                <div class="model-container">
                    <div class="model-wrapper">
                        <model-viewer 
                            id="model-viewer"
                            src="{model_url}"
                            alt="3D Model"
                            auto-rotate
                            camera-controls
                            touch-action="pan-y"
                            camera-orbit="45deg 75deg 2.5m"
                            min-camera-orbit="auto auto 1.5m"
                            max-camera-orbit="auto auto 4m"
                            field-of-view="30deg"
                            camera-target="0m 0m 0m"
                            loading="eager"
                            reveal="auto"
                            ar
                            ar-modes="webxr scene-viewer quick-look">
                        </model-viewer>
                    </div>
                </div>

                <div class="ar-section">
                    <button class="ar-button" id="ar-button" onclick="launchAR()">
                        <div class="ar-icon">📱</div>
                        <div class="ar-content">
                            <h3>View in Room</h3>
                            <p>Open in AR</p>
                        </div>
                    </button>
                </div>

                <footer class="footer">
                    <p>Powered by Web AR Technology</p>
                </footer>
            </div>

            <script>
                function launchAR() {{
                    const modelViewer = document.getElementById('model-viewer');
                    if (modelViewer) {{
                        modelViewer.activateAR();
                    }}
                }}
            </script>
        </body>
        </html>
    """
    
    return HTMLResponse(content=ar_viewer_html)
