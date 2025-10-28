/**
 * API Communication Layer
 * Handles all backend API calls
 */

class APIClient {
    constructor(baseURL = 'http://localhost:3000') {
        this.baseURL = baseURL;
        this.endpoints = {
            upload: `${baseURL}/api/upload`,
            arViewer: `${baseURL}/api/ar-viewer`,
            health: `${baseURL}/api/health`
        };
    }

    /**
     * Check if the API server is healthy
     * @returns {Promise<boolean>} - True if server is healthy
     */
    async checkHealth() {
        try {
            const response = await fetch(this.endpoints.health, {
                method: 'GET',
                timeout: 5000
            });
            return response.ok;
        } catch (error) {
            console.error('Health check failed:', error);
            return false;
        }
    }

    /**
     * Generate 3D model from image and dimensions
     * @param {File} imageFile - The uploaded image file
     * @param {Object} dimensions - Model dimensions
     * @param {number} dimensions.length - Length in meters
     * @param {number} dimensions.width - Width in meters
     * @param {number} dimensions.thickness - Thickness in millimeters
     * @returns {Promise<Object>} - Response with model URLs
     */
    async generateModel(imageFile, dimensions) {
        try {
            // Create FormData for file upload
            const formData = new FormData();
            formData.append('image', imageFile); // Field name matches API server expectation
            
            // Add dimensions as metadata (for future backend support)
            formData.append('dimensions', JSON.stringify(dimensions));
            formData.append('length', dimensions.length.toString());
            formData.append('width', dimensions.width.toString());
            formData.append('thickness', dimensions.thickness.toString());

            const response = await fetch(`${this.endpoints.upload}/generate-ar-link`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Upload failed');
            }

            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.error || 'Model generation failed');
            }

            return {
                success: true,
                filename: result.filename,
                publicUrl: result.public_url,
                arViewerLink: result.ar_viewer_link,
                size: result.size
            };

        } catch (error) {
            console.error('Model generation failed:', error);
            throw error;
        }
    }

    /**
     * Get AR viewer link for a model URL
     * @param {string} modelUrl - URL of the model
     * @returns {string} - AR viewer link
     */
    getARViewerLink(modelUrl) {
        return `${this.endpoints.arViewer}?model_url=${encodeURIComponent(modelUrl)}`;
    }

    /**
     * Get server information
     * @returns {Promise<Object>} - Server info
     */
    async getServerInfo() {
        try {
            const response = await fetch(this.baseURL, {
                method: 'GET'
            });

            if (!response.ok) {
                throw new Error('Failed to get server info');
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to get server info:', error);
            throw error;
        }
    }

    /**
     * Get upload statistics
     * @returns {Promise<Object>} - Upload stats
     */
    async getUploadStats() {
        try {
            const response = await fetch(`${this.endpoints.upload}/stats`, {
                method: 'GET'
            });

            if (!response.ok) {
                throw new Error('Failed to get upload stats');
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to get upload stats:', error);
            throw error;
        }
    }
}

// Export singleton instance
window.apiClient = new APIClient();
