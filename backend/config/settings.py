import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-deepfake-ai'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../temp')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'mov', 'avi', 'mkv', 'wav', 'mp3'}
    MODEL_PATH = os.environ.get('MODEL_PATH', './models')
    PYTHON_SERVICE_API_KEY = os.environ.get('PYTHON_SERVICE_API_KEY', '')
    
    # MongoDB (Atlas) configuration
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
    MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME', 'truthlens')
    
    # JWT configuration
    JWT_SECRET = os.environ.get('JWT_SECRET', SECRET_KEY)
    JWT_EXPIRES_IN_MINUTES = int(os.environ.get('JWT_EXPIRES_IN_MINUTES', '60'))
    
    # Create upload folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)