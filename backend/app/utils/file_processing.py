import os
import requests
from urllib.parse import urlparse
from config.settings import Config

def download_file(url):
    """Download file from URL to temporary location"""
    try:
        # Extract filename from URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        # Generate unique filename
        unique_filename = f"{os.path.splitext(filename)[0]}_{os.urandom(8).hex()}{os.path.splitext(filename)[1]}"
        file_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        
        # Download file
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return file_path
        
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        return None

def cleanup_file(file_path):
    """Remove temporary file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error cleaning up file: {str(e)}")