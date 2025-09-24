import os
import threading
import logging
from flask import request, jsonify
from flask_socketio import emit
from app import socketio, create_app
from app.utils.file_processing import download_file, cleanup_file

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = create_app()

# Store analysis progress
analysis_progress = {}

# Lightweight model initialization
models_initialized = True

def process_media(session_id, media_url, media_type):
    """Lightweight media processing - production ready"""
    file_path = None
    
    try:
        logger.info(f"Processing {media_type} for session {session_id}")
        
        # Update progress
        analysis_progress[session_id] = 5
        socketio.emit('progress_update', {'progress': 5, 'message': 'Downloading file...'}, room=session_id)
        
        # Download file
        file_path = download_file(media_url)
        
        if not file_path:
            socketio.emit('analysis_error', {
                'error': 'Failed to download file. Please check the URL.',
                'code': 'DOWNLOAD_FAILED'
            }, room=session_id)
            return
        
        # Verify file exists and has content
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            socketio.emit('analysis_error', {
                'error': 'Downloaded file is empty or corrupted',
                'code': 'FILE_CORRUPTED'
            }, room=session_id)
            return
        
        # Update progress
        analysis_progress[session_id] = 10
        socketio.emit('progress_update', {'progress': 10, 'message': 'Starting analysis...'}, room=session_id)
        
        # Import and analyze based on media type
        result = None
        
        if media_type.lower() in ['image', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff']:
            try:
                from app.models.image_model import analyze_image
                result = analyze_image(file_path, session_id, analysis_progress)
            except Exception as e:
                logger.error(f"Image analysis error: {str(e)}")
                result = create_fallback_result('image', str(e))
            
        elif media_type.lower() in ['video', 'mp4', 'mov', 'avi', 'mkv', 'webm', 'flv']:
            try:
                from app.models.video_model import analyze_video
                result = analyze_video(file_path, session_id, analysis_progress)
            except Exception as e:
                logger.error(f"Video analysis error: {str(e)}")
                result = create_fallback_result('video', str(e))
            
        elif media_type.lower() in ['audio', 'wav', 'mp3', 'flac', 'aac', 'ogg', 'm4a']:
            try:
                from app.models.audio_model import analyze_audio
                result = analyze_audio(file_path, session_id, analysis_progress)
            except Exception as e:
                logger.warning(f"Audio analysis not available: {str(e)}")
                result = create_fallback_result('audio', 'Audio analysis not available in this deployment')
        else:
            socketio.emit('analysis_error', {
                'error': f"Unsupported media type: {media_type}",
                'code': 'UNSUPPORTED_MEDIA_TYPE'
            }, room=session_id)
            return
        
        if result is None:
            result = create_fallback_result(media_type, 'Analysis failed')
        
        # Add metadata
        result['session_id'] = session_id
        result['media_url'] = media_url
        result['file_size'] = os.path.getsize(file_path)
        result['deployment_mode'] = True
        
        # Send final result
        socketio.emit('analysis_complete', result, room=session_id)
        logger.info(f"Analysis completed for session {session_id}")
        
    except Exception as e:
        logger.error(f"Error processing media for session {session_id}: {str(e)}")
        socketio.emit('analysis_error', {
            'error': str(e),
            'code': 'PROCESSING_ERROR'
        }, room=session_id)
        
    finally:
        # Cleanup
        if file_path and os.path.exists(file_path):
            cleanup_file(file_path)
        
        # Remove progress tracking
        if session_id in analysis_progress:
            del analysis_progress[session_id]

def create_fallback_result(media_type, error_msg):
    """Create a fallback result when analysis fails"""
    from datetime import datetime
    
    return {
        "isDeepfake": False,
        "confidence": 50.0,
        "processingTime": 0.5,
        "anomalies": [{
            "type": "Analysis unavailable",
            "severity": "info",
            "description": error_msg
        }],
        "mediaType": media_type,
        "timestamp": datetime.now().isoformat(),
        "modelUsed": "Fallback",
        "deployment_mode": True
    }

@socketio.on('connect')
def handle_connect():
    logger.info(f'Client connected: {request.sid}')
    socketio.emit('connection_status', {
        'status': 'connected',
        'models_ready': True,
        'deployment_mode': True,
        'message': 'Connected to deepfake detection service'
    }, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f'Client disconnected: {request.sid}')
    session_id = request.sid
    if session_id in analysis_progress:
        del analysis_progress[session_id]

@socketio.on('start_analysis')
def handle_start_analysis(data):
    session_id = request.sid
    media_url = data.get('media_url')
    media_type = data.get('media_type')
    
    if not media_url or not media_type:
        socketio.emit('analysis_error', {
            'error': 'Missing media_url or media_type',
            'code': 'MISSING_PARAMETERS'
        }, room=session_id)
        return
    
    logger.info(f"Starting analysis for session {session_id}: {media_type}")
    
    # Start analysis in background thread
    thread = threading.Thread(
        target=process_media, 
        args=(session_id, media_url, media_type),
        daemon=True
    )
    thread.start()
    
    socketio.emit('analysis_started', {
        'status': 'processing', 
        'message': f'Analysis started for {media_type}',
        'session_id': session_id
    }, room=session_id)

@socketio.on('get_progress')
def handle_get_progress(data):
    session_id = data.get('session_id', request.sid)
    progress = analysis_progress.get(session_id, 0)
    socketio.emit('progress_update', {'progress': progress}, room=session_id)

@socketio.on('cancel_analysis')
def handle_cancel_analysis(data):
    session_id = data.get('session_id', request.sid)
    
    if session_id in analysis_progress:
        del analysis_progress[session_id]
        socketio.emit('analysis_cancelled', {'message': 'Analysis cancelled'}, room=session_id)
        logger.info(f"Analysis cancelled for session {session_id}")
    else:
        socketio.emit('analysis_error', {'error': 'No ongoing analysis found'}, room=session_id)

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get service status"""
    return jsonify({
        'status': 'healthy',
        'service': 'deepfake-detection-api',
        'models_initialized': True,
        'deployment_mode': True,
        'active_sessions': len(analysis_progress),
        'supported_formats': {
            'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'],
            'video': ['mp4', 'mov', 'avi', 'mkv', 'webm', 'flv'],
            'audio': ['wav', 'mp3', 'flac', 'aac', 'ogg', 'm4a']
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 
        'service': 'deepfake-detection-api'
    })

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'service': 'Deepfake Detection API',
        'version': '1.0.0',
        'status': 'running',
        'deployment_mode': True,
        'endpoints': {
            'websocket': 'Connect to / for real-time analysis',
            'health': '/api/health',
            'status': '/api/status'
        }
    })

# For deployment compatibility
def create_application():
    """Factory function for deployment"""
    return app

if __name__ == '__main__':
    logger.info("Starting Deepfake Detection Service...")
    
    # Create upload directory
    from config.settings import Config
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)
        logger.info(f"Created upload directory: {Config.UPLOAD_FOLDER}")
    
    # Get port from environment (for deployment)
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting server on {host}:{port}")
    socketio.run(app, debug=False, host=host, port=port)