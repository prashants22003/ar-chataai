# AR Carpet Model Generator - Frontend

A modern, interactive frontend for generating 3D carpet models with AR viewing capabilities.

## Features

- **Dimension Input**: Configure carpet length, width, and thickness
- **Image Upload**: Drag & drop or click to upload carpet images
- **3D Model Generation**: Generate interactive 3D models from images
- **AR Viewing**: View models in augmented reality
- **Progress Tracking**: Real-time progress updates during generation
- **Responsive Design**: Works on desktop, tablet, and mobile

## Technology Stack

- **HTML5**: Semantic markup with accessibility features
- **CSS3**: Modern styling with CSS Grid, Flexbox, and custom properties
- **Vanilla JavaScript**: No frameworks, pure ES6+ JavaScript
- **Model Viewer**: Google's model-viewer component for 3D display
- **Fetch API**: Modern HTTP client for API communication

## File Structure

```
client/
├── index.html          # Main application page
├── css/
│   └── style.css      # Complete styling with bluish-green theme
├── js/
│   ├── app.js         # Main application logic and state management
│   ├── api.js         # API communication layer
│   └── modelViewer.js # 3D model viewer component
└── assets/
    └── placeholder.svg # Upload area placeholder icon
```

## Design System

### Color Palette
- **Primary**: `#2DD4BF` (Teal/Cyan)
- **Secondary**: `#1E40AF` (Deep Blue)
- **Background**: `#0F172A` (Dark Blue-Gray)
- **Surface**: `#1E293B` (Lighter Blue-Gray)
- **Text**: `#F8FAFC` (Off-White)
- **Accent**: `#10B981` (Green)

### Typography
- **Font Family**: System fonts (SF Pro, Segoe UI, Roboto, etc.)
- **Headings**: Bold weights with gradient text effects
- **Body**: Regular weight with good contrast

### Components
- **Cards**: Glass morphism effect with backdrop blur
- **Buttons**: Gradient backgrounds with hover animations
- **Inputs**: Rounded corners with focus states
- **Progress**: Animated gradient progress bars

## Usage

1. **Open** `index.html` in a web browser
2. **Configure** carpet dimensions (default: 2m × 3m × 5mm)
3. **Upload** a carpet image (JPG, PNG, JPEG up to 20MB)
4. **Click** "Generate 3D Model" to start processing
5. **View** the generated model in the preview area
6. **Click** "View in Room" to open AR viewer

## API Integration

The frontend communicates with the backend API server:

- **Base URL**: `http://localhost:3000`
- **Upload Endpoint**: `POST /api/upload/generate-ar-link`
- **AR Viewer**: `GET /api/ar-viewer?model_url=<url>`
- **Health Check**: `GET /api/health`

## Browser Support

- **Chrome**: 80+ (recommended)
- **Firefox**: 75+
- **Safari**: 13+
- **Edge**: 80+

## Responsive Breakpoints

- **Desktop**: >1024px (Two-column layout)
- **Tablet**: 768-1024px (Stacked layout)
- **Mobile**: <768px (Single column)

## Development

To modify the frontend:

1. **Styling**: Edit `css/style.css`
2. **Logic**: Modify `js/app.js`
3. **API**: Update `js/api.js`
4. **3D Viewer**: Adjust `js/modelViewer.js`

## Future Enhancements

- Advanced model controls (rotation, zoom limits)
- Multiple model formats support
- Batch processing capabilities
- User account system
- Model sharing features
