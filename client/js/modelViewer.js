/**
 * Model Viewer Component
 * Handles 3D model display and AR functionality
 */

class ModelViewer {
    constructor() {
        this.modelViewer = null;
        this.arButton = null;
        this.isInitialized = false;
    }

    /**
     * Initialize the model viewer
     */
    init() {
        this.modelViewer = document.getElementById('modelViewer');
        this.arButton = document.getElementById('arBtn');
        
        if (!this.modelViewer) {
            console.error('Model viewer element not found');
            return;
        }

        this.setupEventListeners();
        this.isInitialized = true;
        console.log('Model viewer initialized');
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        if (this.arButton) {
            this.arButton.addEventListener('click', () => this.launchAR());
        }

        if (this.modelViewer) {
            this.modelViewer.addEventListener('load', () => {
                console.log('Model loaded successfully');
                this.hideLoading();
            });

            this.modelViewer.addEventListener('error', (e) => {
                console.error('Model load error:', e);
                this.showError('Failed to load 3D model');
            });
        }
    }

    /**
     * Load a model into the viewer
     * @param {string} modelUrl - URL of the GLB model
     */
    loadModel(modelUrl) {
        if (!this.isInitialized) {
            console.error('Model viewer not initialized');
            return;
        }

        console.log('Loading model:', modelUrl);
        this.showLoading();
        
        // Set model source
        this.modelViewer.src = modelUrl;
        
        // Configure AR
        this.modelViewer.ar = true;
        this.modelViewer.arModes = 'webxr scene-viewer quick-look';
    }

    /**
     * Launch AR viewer
     */
    launchAR() {
        if (!this.modelViewer) {
            console.error('Model viewer not available');
            return;
        }

        console.log('Launching AR...');
        
        try {
            // Try to activate AR
            this.modelViewer.activateAR();
        } catch (error) {
            console.error('Failed to launch AR:', error);
            this.showARError();
        }
    }

    /**
     * Show loading state
     */
    showLoading() {
        const loadingElement = this.modelViewer.querySelector('.model-loading');
        if (loadingElement) {
            loadingElement.style.display = 'block';
        }
    }

    /**
     * Hide loading state
     */
    hideLoading() {
        const loadingElement = this.modelViewer.querySelector('.model-loading');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }

    /**
     * Show error state
     * @param {string} message - Error message
     */
    showError(message) {
        console.error('Model viewer error:', message);
        
        // Create error overlay
        const errorOverlay = document.createElement('div');
        errorOverlay.className = 'model-error';
        errorOverlay.innerHTML = `
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; color: var(--error);">
                <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
                <p>${message}</p>
                <button onclick="this.parentElement.parentElement.remove()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: var(--error); color: white; border: none; border-radius: var(--radius-md); cursor: pointer;">Retry</button>
            </div>
        `;
        
        this.modelViewer.appendChild(errorOverlay);
    }

    /**
     * Show AR error
     */
    showARError() {
        // Simple alert for now - could be improved with a modal
        alert('AR is not available on this device or browser. Please try on a mobile device with AR support.');
    }

    /**
     * Reset the viewer
     */
    reset() {
        if (this.modelViewer) {
            this.modelViewer.src = '';
            this.hideLoading();
        }
    }

    /**
     * Get current model URL
     * @returns {string|null} - Current model URL
     */
    getCurrentModelUrl() {
        return this.modelViewer ? this.modelViewer.src : null;
    }

    /**
     * Check if AR is supported
     * @returns {boolean} - True if AR is supported
     */
    isARSupported() {
        // Check for WebXR support or mobile AR
        return 'xr' in navigator || 
               /iPhone|iPad|iPod/.test(navigator.userAgent) ||
               /Android/.test(navigator.userAgent);
    }
}

// Export singleton instance
window.modelViewer = new ModelViewer();
