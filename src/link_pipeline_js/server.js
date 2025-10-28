/**
 * Node.js Service for Uploading 3D Models to Supabase
 * Generates public access links for GLB files
 */

require('dotenv').config();
const express = require('express');
const multer = require('multer');
const { createClient } = require('@supabase/supabase-js');
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const fs = require('fs');

const app = express();
const port = process.env.PORT || 3000;

// Initialize Supabase client
const supabaseUrl = process.env.PROJECT_URL || process.env.SUPABASE_URL;
const supabaseKey = process.env.API_KEY || process.env.SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('ERROR: PROJECT_URL and API_KEY must be set in .env file');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

// Configure multer for file uploads
const upload = multer({ 
  dest: 'uploads/',
  limits: { fileSize: 100 * 1024 * 1024 } // 100MB limit
});

app.use(express.json());
app.use(express.static('public'));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    supabase: !!supabaseUrl,
    bucket: '3d-models' 
  });
});

// Upload GLB file and return public URL
app.post('/upload', upload.single('glb'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const { originalname, path: filePath, size } = req.file;
    
    // Read file
    const fileData = fs.readFileSync(filePath);
    
    // Generate unique filename
    const fileExt = path.extname(originalname);
    const uniqueId = uuidv4().substring(0, 8);
    const filename = `${path.parse(originalname).name}_${uniqueId}${fileExt}`;
    
    console.log(`Uploading ${filename} to Supabase...`);
    
    // Upload to Supabase storage
    const { data, error } = await supabase.storage
      .from('3d-models')
      .upload(filename, fileData, {
        contentType: 'model/gltf-binary',
        upsert: false
      });
    
    // Clean up local file
    fs.unlinkSync(filePath);
    
    if (error) {
      console.error('Upload error:', error);
      return res.status(500).json({ error: error.message });
    }
    
    // Get public URL
    const { data: publicUrlData } = supabase.storage
      .from('3d-models')
      .getPublicUrl(filename);
    
    const publicUrl = publicUrlData.publicUrl;
    
    console.log(`Upload successful: ${filename}`);
    console.log(`Public URL: ${publicUrl}`);
    console.log(`Size: ${(size / (1024 * 1024)).toFixed(2)} MB`);
    
    res.json({
      success: true,
      filename: filename,
      public_url: publicUrl,
      size: size,
      message: 'Model uploaded successfully!'
    });
    
  } catch (error) {
    console.error('Upload failed:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get bucket info
app.get('/bucket-info', async (req, res) => {
  try {
    const { data: buckets, error } = await supabase.storage.listBuckets();
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    const modelsBucket = buckets.find(b => b.name === '3d-models');
    
    res.json({
      bucket_exists: !!modelsBucket,
      bucket_info: modelsBucket || null,
      all_buckets: buckets.map(b => b.name)
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(port, () => {
  console.log('='.repeat(70));
  console.log('Carpet Model Link Generator Service');
  console.log('='.repeat(70));
  console.log(`Server running on http://localhost:${port}`);
  console.log(`Supabase URL: ${supabaseUrl}`);
  console.log('Endpoints:');
  console.log('  POST /upload - Upload GLB file');
  console.log('  GET  /health - Health check');
  console.log('  GET  /bucket-info - Check bucket status');
  console.log('='.repeat(70));
});

