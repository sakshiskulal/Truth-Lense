# DeepCheck AI 🛡️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

DeepCheck AI is a comprehensive Python-based service for detecting manipulated media including **images, videos, and audio files**. Built with a modular architecture, it integrates state-of-the-art deepfake detection models and provides easy-to-use REST API endpoints that can be seamlessly connected to web frontends.

---

## ✨ Key Features

- 🖼️ **Multi-Modal Detection**: Analyze images, videos, and audio files
- 📊 **Confidence Scoring**: Get detailed confidence metrics for all results
- 📁 **Bulk Processing**: Upload and process multiple files simultaneously
- 🔧 **Modular Architecture**: Easy integration of new detection models
- 🌐 **REST API**: Ready-to-use Flask/FastAPI endpoints
- ⚙️ **Configurable**: Flexible configuration via environment variables
- 🚀 **Production Ready**: Optimized for deployment and scaling

---

## 📂 Project Structure

```
deepfake-ai-service/
├── app/
│   ├── main.py                 # Application entry point
│   ├── models/                 # AI detection models
│   │   ├── image_detector.py   # Image deepfake detection
│   │   ├── video_detector.py   # Video deepfake detection
│   │   └── audio_detector.py   # Audio deepfake detection
│   ├── utils/                  # Utility functions
│   │   ├── preprocessing.py    # Media preprocessing
│   │   ├── validation.py       # Input validation
│   │   └── helpers.py          # Common helper functions
│   └── routes/                 # API route definitions
│       ├── api.py              # Main API routes
│       └── health.py           # Health check endpoints
├── config/
│   ├── settings.py             # Application settings
│   └── logging.conf            # Logging configuration
├── tests/                      # Test suite
│   ├── test_models.py          # Model tests
│   ├── test_api.py             # API endpoint tests
│   └── fixtures/               # Test media files
├── temp/                       # Temporary file storage
├── logs/                       # Application logs
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Development dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── run.py                      # Application runner
├── README.md                   # This file
└── CONTRIBUTING.md             # Contribution guidelines
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/deepcheck-ai.git
   cd deepcheck-ai
   ```

2. **Create and activate virtual environment**

   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

The service will be available at `http://localhost:5000`

---

## 🖥️ Usage

### API Endpoints

#### Authentication

Base path: both `/auth/*` and `/api/auth/*` are available for convenience.

- POST `/auth/signup` — Body: `{ "email": string, "password": string }` — returns `{ access_token, token_type }`
- POST `/auth/login` — Body: `{ "email": string, "password": string }` — returns `{ access_token, token_type }`
- GET `/auth/me` — Header: `Authorization: Bearer <token>` — returns user profile `{ email, ... }`

Notes:
- Passwords are hashed (Werkzeug) before storage.
- Tokens are JWT (HS256). Configure with `JWT_SECRET` and `JWT_EXPIRES_IN_MINUTES`.
- Backing store: MongoDB (Atlas recommended). Configure `MONGODB_URI` and `MONGODB_DB_NAME` in `.env`.

#### Health Check

```bash
GET /health
```

#### Upload and Analyze Media

```bash
POST /api/analyze
Content-Type: multipart/form-data

# Parameters:
# - file: Media file (image/video/audio)
# - threshold: Confidence threshold (optional, default: 0.5)
```

#### Example Response

```json
{
  "status": "success",
  "file_type": "image",
  "is_deepfake": false,
  "confidence": 0.85,
  "processing_time": 2.34,
  "metadata": {
    "model_version": "v2.1.0",
    "timestamp": "2024-03-15T10:30:00Z"
  }
}
```

### Python Client Example

```python
import requests

url = "http://localhost:5000/api/analyze"
files = {"file": open("suspicious_image.jpg", "rb")}
data = {"threshold": 0.7}

response = requests.post(url, files=files, data=data)
result = response.json()

print(f"Is deepfake: {result['is_deepfake']}")
print(f"Confidence: {result['confidence']}")
```

### Frontend Integration

The API is designed to work seamlessly with web frontends. For a complete example with Next.js, check out our [frontend repository](https://github.com/YOUR_USERNAME/deepcheck-frontend).

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory (see `.env.example`):

```env
# General
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development

# MongoDB Atlas (example URI format)
# MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority
MONGODB_URI=
MONGODB_DB_NAME=truthlens

# JWT
JWT_SECRET=your-jwt-secret-here
JWT_EXPIRES_IN_MINUTES=60
```

### Advanced Configuration

For advanced settings, modify `config/settings.py`:

```python
class Config:
    # Model configurations
    IMAGE_MODEL_PATH = "models/image_detector.pth"
    VIDEO_MODEL_PATH = "models/video_detector.pth"
    AUDIO_MODEL_PATH = "models/audio_detector.pth"

    # Processing limits
    MAX_VIDEO_DURATION = 300  # seconds
    MAX_BATCH_SIZE = 10

    # Performance tuning
    WORKER_THREADS = 4
    ENABLE_CACHING = True

   # Database / Auth
   MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
   MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME', 'truthlens')
   JWT_SECRET = os.environ.get('JWT_SECRET', SECRET_KEY)
   JWT_EXPIRES_IN_MINUTES = int(os.environ.get('JWT_EXPIRES_IN_MINUTES', '60'))
```

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

### Manual Docker Build

```bash
# Build image
docker build -t deepcheck-ai .

# Run container
docker run -p 5000:5000 -v $(pwd)/temp:/app/temp deepcheck-ai
```

---

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

---

## 📈 Performance

### Benchmarks

| Media Type | Average Processing Time     | GPU Acceleration |
| ---------- | --------------------------- | ---------------- |
| Images     | 0.5s                        | 3x faster        |
| Videos     | 2-10s (depending on length) | 5x faster        |
| Audio      | 1-3s                        | 2x faster        |

### Optimization Tips

- Enable GPU acceleration for significant performance gains
- Use batch processing for multiple files
- Configure appropriate worker threads based on your hardware
- Enable caching for repeated analyses

---

## 🛣️ Roadmap

### Version 2.0

- [ ] Advanced transformer-based models (BERT, Vision Transformer)
- [ ] Real-time streaming detection
- [ ] Enhanced GPU optimization (TensorRT integration)
- [ ] Multi-language support for API documentation

### Version 2.1

- [ ] Kubernetes deployment templates
- [ ] Advanced analytics dashboard
- [ ] Model fine-tuning capabilities
- [ ] Integration with cloud storage providers (AWS S3, Google Cloud)

### Version 3.0

- [ ] Federated learning support
- [ ] Custom model training interface
- [ ] Advanced forensic analysis features
- [ ] Mobile SDK for iOS/Android

---

## 🤝 Contributing

We welcome contributions from developers of all skill levels! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on how to contribute to DeepCheck AI.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

We thank the following projects and research communities:

- **[DeepFace](https://github.com/serengil/deepface)** - Face recognition and analysis framework
- **[OpenCV](https://opencv.org/)** - Computer vision library
- **[PyTorch](https://pytorch.org/)** - Deep learning framework
- **[Librosa](https://librosa.org/)** - Audio analysis library
- **Academic Research Community** - For groundbreaking work in deepfake detection

### Research Papers

- "FaceForensics++: Learning to Detect Manipulated Facial Images" (Rössler et al., 2019)
- "The DeepFake Detection Challenge (DFDC) Dataset" (Dolhansky et al., 2020)
- "DeeperForensics-1.0: A Large-Scale Dataset for Real-World Face Forgery Detection" (Jiang et al., 2020)

---

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/YOUR_USERNAME/deepcheck-ai/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/YOUR_USERNAME/deepcheck-ai/discussions)
- 📧 **Email**: support@deepcheck-ai.com
- 💬 **Discord**: [Join our community](https://discord.gg/deepcheck-ai)

---

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/deepcheck-ai?style=social)
![GitHub forks](https://img.shields.io/github/forks/YOUR_USERNAME/deepcheck-ai?style=social)
![GitHub issues](https://img.shields.io/github/issues/YOUR_USERNAME/deepcheck-ai)
![GitHub pull requests](https://img.shields.io/github/issues-pr/YOUR_USERNAME/deepcheck-ai)

---

<p align="center">
  <strong>Built with ❤️ for a safer digital world</strong>
</p>
