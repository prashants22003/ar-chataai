/**
 * Main Application Logic
 * Handles form validation, state management, and user interactions
 */

class App {
    constructor() {
        this.state = {
            dimensions: { length: 2, width: 3, thickness: 5 },
            uploadedImage: null,
            imagePreview: null,
            generatedModel: null,
            isGenerating: false
        };

        this.elements = {
            // Form elements
            lengthInput: document.getElementById('length'),
            widthInput: document.getElementById('width'),
            thicknessInput: document.getElementById('thickness'),
            imageInput: document.getElementById('imageInput'),
            uploadArea: document.getElementById('uploadArea'),
            uploadContent: document.getElementById('uploadContent'),
            imagePreview: document.getElementById('imagePreview'),
            previewImage: document.getElementById('previewImage'),
            removeImage: document.getElementById('removeImage'),
            generateBtn: document.getElementById('generateBtn'),
            
            // Preview elements
            previewContainer: document.getElementById('previewContainer'),
            
            // Progress elements
            progressOverlay: document.getElementById('progressOverlay'),
            progressFill: document.getElementById('progressFill'),
            progressPercent: document.getElementById('progressPercent'),
            progressStatus: document.getElementById('progressStatus'),
            
            // AR elements
            arBtn: document.getElementById('arBtn')
        };

        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        this.setupEventListeners();
        this.validateForm();
        this.checkServerHealth();
        
        console.log('App initialized');
    }

    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Dimension inputs
        this.elements.lengthInput.addEventListener('input', () => this.handleDimensionChange('length'));
        this.elements.widthInput.addEventListener('input', () => this.handleDimensionChange('width'));
        this.elements.thicknessInput.addEventListener('input', () => this.handleDimensionChange('thickness'));

        // Image upload
        this.elements.uploadArea.addEventListener('click', () => this.elements.imageInput.click());
        this.elements.imageInput.addEventListener('change', (e) => this.handleImageUpload(e));
        this.elements.removeImage.addEventListener('click', () => this.removeImage());

        // Drag and drop
        this.elements.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.elements.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.elements.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));

        // Generate button
        this.elements.generateBtn.addEventListener('click', () => this.generateModel());

        // AR button
        this.elements.arBtn.addEventListener('click', () => this.openARViewer());
    }

    /**
     * Handle dimension input changes
     * @param {string} dimension - The dimension that changed
     */
    handleDimensionChange(dimension) {
        const value = parseFloat(this.elements[`${dimension}Input`].value);
        
        if (!isNaN(value)) {
            this.state.dimensions[dimension] = value;
        }
        
        this.validateForm();
    }

    /**
     * Handle image file upload
     * @param {Event} event - File input change event
     */
    handleImageUpload(event) {
        const file = event.target.files[0];
        if (file) {
            this.processImageFile(file);
        }
    }

    /**
     * Handle drag over event
     * @param {Event} event - Drag over event
     */
    handleDragOver(event) {
        event.preventDefault();
        this.elements.uploadArea.classList.add('dragover');
    }

    /**
     * Handle drag leave event
     * @param {Event} event - Drag leave event
     */
    handleDragLeave(event) {
        event.preventDefault();
        this.elements.uploadArea.classList.remove('dragover');
    }

    /**
     * Handle drop event
     * @param {Event} event - Drop event
     */
    handleDrop(event) {
        event.preventDefault();
        this.elements.uploadArea.classList.remove('dragover');
        
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            this.processImageFile(files[0]);
        }
    }

    /**
     * Process uploaded image file
     * @param {File} file - The uploaded file
     */
    processImageFile(file) {
        // Validate file
        if (!this.validateImageFile(file)) {
            return;
        }

        this.state.uploadedImage = file;
        
        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
            this.state.imagePreview = e.target.result;
            this.showImagePreview();
            this.validateForm();
        };
        reader.readAsDataURL(file);
    }

    /**
     * Validate image file
     * @param {File} file - The file to validate
     * @returns {boolean} - True if valid
     */
    validateImageFile(file) {
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        const maxSize = 20 * 1024 * 1024; // 20MB

        if (!validTypes.includes(file.type)) {
            alert('Please upload a JPG, PNG, or JPEG image.');
            return false;
        }

        if (file.size > maxSize) {
            alert('Image size must be less than 20MB.');
            return false;
        }

        return true;
    }

    /**
     * Show image preview
     */
    showImagePreview() {
        this.elements.previewImage.src = this.state.imagePreview;
        this.elements.uploadContent.style.display = 'none';
        this.elements.imagePreview.style.display = 'block';
    }

    /**
     * Remove uploaded image
     */
    removeImage() {
        this.state.uploadedImage = null;
        this.state.imagePreview = null;
        this.elements.imageInput.value = '';
        this.elements.uploadContent.style.display = 'block';
        this.elements.imagePreview.style.display = 'none';
        this.validateForm();
    }

    /**
     * Validate form and enable/disable generate button
     */
    validateForm() {
        const { length, width, thickness } = this.state.dimensions;
        const hasValidDimensions = length >= 0.5 && length <= 10 &&
                                  width >= 0.5 && width <= 10 &&
                                  thickness >= 1 && thickness <= 20;
        const hasImage = this.state.uploadedImage !== null;

        const isValid = hasValidDimensions && hasImage;
        this.elements.generateBtn.disabled = !isValid;
    }

    /**
     * Generate 3D model
     */
    async generateModel() {
        if (this.state.isGenerating) {
            return;
        }

        try {
            this.state.isGenerating = true;
            this.showProgressOverlay();
            this.updateProgress(0, 'Uploading image...');

            // Generate model via API
            const result = await window.apiClient.generateModel(
                this.state.uploadedImage,
                this.state.dimensions
            );

            this.state.generatedModel = result;
            this.updateProgress(100, 'Complete!');
            
            // Show model preview
            setTimeout(() => {
                this.hideProgressOverlay();
                this.showModelPreview(result.publicUrl);
            }, 1000);

        } catch (error) {
            console.error('Model generation failed:', error);
            this.hideProgressOverlay();
            alert(`Model generation failed: ${error.message}`);
        } finally {
            this.state.isGenerating = false;
        }
    }

    /**
     * Show model preview
     * @param {string} modelUrl - URL of the generated model
     */
    showModelPreview(modelUrl) {
        // Show preview container
        this.elements.previewContainer.style.display = 'block';
        
        // Load model in viewer
        window.modelViewer.loadModel(modelUrl);
        
        // Store AR viewer link
        this.state.arViewerLink = window.apiClient.getARViewerLink(modelUrl);
    }

    /**
     * Open AR viewer
     */
    openARViewer() {
        if (this.state.arViewerLink) {
            window.open(this.state.arViewerLink, '_blank');
        } else {
            console.error('AR viewer link not available');
        }
    }

    /**
     * Show progress overlay
     */
    showProgressOverlay() {
        this.elements.progressOverlay.style.display = 'flex';
    }

    /**
     * Hide progress overlay
     */
    hideProgressOverlay() {
        this.elements.progressOverlay.style.display = 'none';
    }

    /**
     * Update progress
     * @param {number} percent - Progress percentage (0-100)
     * @param {string} status - Status message
     */
    updateProgress(percent, status) {
        this.elements.progressFill.style.width = `${percent}%`;
        this.elements.progressPercent.textContent = `${Math.round(percent)}%`;
        this.elements.progressStatus.textContent = status;
    }

    /**
     * Check server health
     */
    async checkServerHealth() {
        try {
            const isHealthy = await window.apiClient.checkHealth();
            if (!isHealthy) {
                console.warn('API server is not responding');
                // Could show a warning to the user
            }
        } catch (error) {
            console.error('Failed to check server health:', error);
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize model viewer first
    window.modelViewer.init();
    
    // Then initialize main app
    window.app = new App();
});
