# Link Generation Service (Node.js)

Simple Node.js service for uploading GLB files to Supabase and getting public URLs.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure `.env` file:
```
PROJECT_URL=https://your-project-id.supabase.co
API_KEY=your-anon-key
PORT=3000
```

3. Start the service:
```bash
npm start
```

## API Endpoints

- `POST /upload` - Upload a GLB file
- `GET /health` - Health check
- `GET /bucket-info` - Check if bucket exists

## Usage from Python

```python
import requests

# Upload file
with open('model.glb', 'rb') as f:
    response = requests.post(
        'http://localhost:3000/upload',
        files={'glb': f}
    )
    result = response.json()
    print(f"Public URL: {result['public_url']}")
```

