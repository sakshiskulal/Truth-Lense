# Deepfake Detection Pipeline - Usage Guide

## Overview

This enhanced deepfake detection pipeline uses lightweight Hugging Face models and traditional computer vision techniques to detect manipulated media content across images, videos, and audio files.

## Features

### Enhanced Detection Capabilities
- **Image Analysis**: Uses ResNet-50 with custom feature extraction for facial inconsistencies, texture anomalies, and compression artifacts
- **Video Analysis**: Frame-by-frame analysis with temporal consistency checking and facial landmark tracking  
- **Audio Analysis**: Wav2Vec2-based feature extraction with spectral analysis and voice consistency checking
- **Real-time Progress**: WebSocket-based progress updates during analysis
- **Batch Processing**: Support for analyzing multiple files simultaneously

### Supported Formats
- **Images**: JPG, JPEG, PNG, GIF, BMP, TIFF
- **Videos**: MP4, MOV, AVI, MKV, WEBM, FLV  
- **Audio**: WAV, MP3, FLAC, AAC, OGG, M4A

## Quick Start

### 1. Setup Environment

```bash
# Clone or download the project files
cd deepfake-detection

# Run the setup script
python setup.py

# Or manually install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Edit the `.env` file:

```bash
SECRET_KEY=your-unique-secret-key-here
PYTHON_SERVICE_API_KEY=your-api-key-for-authentication
MODEL_PATH=./models
UPLOAD_FOLDER=./temp
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 3. Start the Service

```bash
# Option 1: Direct execution
python app/main.py

# Option 2: Using run script
python run.py

# The service will start on http://localhost:8000
```

## API Usage

### WebSocket Connection (Recommended)

```javascript
// Connect to the service
const socket = io('http://localhost:8000');

// Listen for connection status
socket.on('connection_status', (data) => {
    console.log('Connected:', data.models_ready);
});

// Start analysis
socket.emit('start_analysis', {
    media_url: 'https://example.com/suspicious_video.mp4',
    media_type: 'video'
});

// Listen for progress updates
socket.on('progress_update', (data) => {
    console.log('Progress:', data.progress + '%');
});

// Listen for results
socket.on('analysis_complete', (result) => {
    console.log('Is Deepfake:', result.isDeepfake);
    console.log('Confidence:', result.confidence + '%');
    console.log('Anomalies:', result.anomalies);
});
```

### REST API Endpoints

#### Single Analysis
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "media_url": "https://example.com/image.jpg",
    "media_type": "image"
  }'
```

#### Batch Analysis
```bash
curl -X POST http://localhost:8000/api/batch-analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "media_list": [
      {"media_url": "https://example.com/image1.jpg", "media_type": "image"},
      {"media_url": "https://example.com/video1.mp4", "media_type": "video"}
    ]
  }'
```

#### Health Check
```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/status
```

## Response Format

### Analysis Result Structure

```json
{
  "isDeepfake": true,
  "confidence": 87.3,
  "processingTime": 2.45,
  "mediaType": "image",
  "timestamp": "2024-01-15T10:30:00Z",
  "modelUsed": "ResNet-50",
  "anomalies": [
    {
      "type": "Facial inconsistency", 
      "severity": "high",
      "description": "Detected unnatural facial feature transitions"
    },
    {
      "type": "Compression artifacts",
      "severity": "medium", 
      "description": "Suspicious compression patterns detected"
    }
  ]
}
```

### Video-Specific Fields
```json
{
  "frameAnalysis": [
    {"frame": 0, "confidence": 85.2, "isDeepfake": true},
    {"frame": 15, "confidence": 72.1, "isDeepfake": false}
  ],
  "totalFrames": 150,
  "analyzedFrames": 30,
  "fps": 25.0,
  "deepfakeFrameRatio": 0.6
}
```

### Audio-Specific Fields
```json
{
  "duration": 15.7,
  "sampleRate": 16000,
  "inconsistencyCount": 3,
  "artifactCount": 1
}
```

## Model Details

### Image Detection
- **Primary Model**: Microsoft ResNet-50 (fine-tuned for binary classification)
- **Fallback**: Traditional computer vision techniques
- **Features Analyzed**:
  - Edge consistency and density
  - Color distribution patterns
  - Texture variance analysis
  - Frequency domain characteristics
  - Compression artifact detection

### Video Detection  
- **Frame Analysis**: ResNet-50 per frame
- **Temporal Analysis**: Optical flow and frame differencing
- **Facial Tracking**: OpenCV Haar cascades for face detection
- **Consistency Checks**: Cross-frame facial landmark analysis

### Audio Detection
- **Primary Model**: Facebook Wav2Vec2-base for feature extraction
- **Signal Processing**: Librosa-based spectral analysis
- **Features Analyzed**:
  - MFCCs (Mel-frequency cepstral coefficients)
  - Spectral centroids and rolloff
  - Zero-crossing rates
  - Chroma and spectral contrast
  - Voice consistency across segments
  - Synthesis artifact detection

## Performance Optimization

### CPU-Only Operation
All models are configured for CPU-only operation to ensure broad compatibility:

```python
# Models automatically use CPU
device = "cpu"
torch.set_num_threads(4)  # Adjust based on your CPU cores
```

### Memory Management
- **Image Processing**: Automatic resizing for large images (>1MP)
- **Video Processing**: Limited to first 100 frames or 30 key frames
- **Audio Processing**: Segment-based analysis for long files
- **Automatic Cleanup**: Temporary files are automatically removed

### Batch Processing Tips
- Process similar media types together
- Limit batch size to 5-10 files for optimal memory usage
- Use WebSocket API for real-time progress tracking

## Troubleshooting

### Common Issues

#### Model Loading Errors
```bash
# Clear Hugging Face cache and redownload
rm -rf ~/.cache/huggingface/
python setup.py
```

#### Memory Issues
```python
# Reduce batch size or frame sampling
# In video_model.py, reduce max_frames:
max_frames = 15  # Instead of 30
```

#### Audio Processing Errors
```bash
# Install additional audio codecs
sudo apt-get install ffmpeg  # Linux
brew install ffmpeg          # macOS
```

### Performance Tuning

#### For Better Accuracy
- Increase frame sampling in videos
- Use higher resolution for image analysis
- Enable more detailed spectral analysis for audio

#### For Better Speed
- Reduce max_frames in video analysis
- Lower image resolution threshold
- Disable some feature extraction steps

### Monitoring and Logging

The service provides comprehensive logging:

```bash
# View logs in real-time
tail -f logs/deepfake_detection.log

# Check model initialization
grep "Model loaded" logs/deepfake_detection.log
```

## Integration Examples

### Python Client
```python
import socketio
import time

sio = socketio.Client()

@sio.event
def analysis_complete(data):
    print(f"Result: {data['isDeepfake']} ({data['confidence']:.1f}%)")

sio.connect('http://localhost:8000')
sio.emit('start_analysis', {
    'media_url': 'path/to/media.jpg',
    'media_type': 'image'
})

sio.wait()
```

### JavaScript/Node.js
```javascript
const io = require('socket.io-client');
const socket = io('http://localhost:8000');

socket.on('connect', () => {
    socket.emit('start_analysis', {
        media_url: 'https://example.com/video.mp4',
        media_type: 'video'
    });
});

socket.on('analysis_complete', (result) => {
    console.log(`Deepfake: ${result.isDeepfake}`);
    console.log(`Confidence: ${result.confidence}%`);
    process.exit(0);
});
```

## Security Considerations

- **API Authentication**: Always use API keys in production
- **File Validation**: Service validates file types and sizes
- **Temporary Files**: All uploads are automatically cleaned up
- **Network Security**: Consider using HTTPS in production
- **Rate Limiting**: Implement rate limiting for public deployments

## Deployment

### Development
```bash
python app/main.py
# Service runs on http://localhost:8000
```

### Production
```bash
# Using Gunicorn + eventlet
pip install gunicorn
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:8000 app.main:app

# Using Docker (create Dockerfile)
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN python setup.py
CMD ["python", "app/main.py"]
```

### Environment Variables for Production
```bash
ENVIRONMENT=production
SECRET_KEY=your-production-secret-key
PYTHON_SERVICE_API_KEY=your-production-api-key
LOG_LEVEL=WARNING
```

## Contributing

To improve the detection models:

1. **Training Data**: Use the Kaggle datasets mentioned:
   - [Fake Audio Dataset](https://www.kaggle.com/datasets/walimuhammadahmad/fakeaudio/data)
   - [Video Deepfake Detection](https://www.kaggle.com/code/adham7elmy/video-deepfake-detection)
   - [Deepfake Image Detection](https://www.kaggle.com/datasets/anjummehnazakumalla/deepfake-image-detection)

2. **Model Fine-tuning**: Replace the generic models with fine-tuned versions
3. **Feature Engineering**: Add new detection features based on latest research
4. **Performance**: Optimize for specific hardware configurations

## License and Disclaimer

This tool is for research and educational purposes. Always verify results with human expertise for critical applications. The accuracy of detection depends on the quality and type of deepfakes being analyzed.