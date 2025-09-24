from flask import Blueprint, request, jsonify
from app.utils.helpers import validate_api_key
from app.utils.file_processing import download_file, cleanup_file
from app.models.image_model import analyze_image
from app.models.video_model import analyze_video
from app.models.audio_model import analyze_audio

bp = Blueprint('analysis', __name__)

@bp.route('/analyze', methods=['POST'])
@validate_api_key
def analyze_media():
    data = request.json
    media_url = data.get('media_url')
    media_type = data.get('media_type')
    
    if not media_url or not media_type:
        return jsonify({'error': 'Missing media_url or media_type'}), 400
    
    try:
        # Download file
        file_path = download_file(media_url)
        
        if not file_path:
            return jsonify({'error': 'Failed to download file'}), 400
        
        # Analyze based on media type
        if media_type in ['image', 'jpg', 'jpeg', 'png']:
            result = analyze_image(file_path)
        elif media_type in ['video', 'mp4', 'mov', 'avi', 'mkv']:
            result = analyze_video(file_path)
        elif media_type in ['audio', 'wav', 'mp3']:
            result = analyze_audio(file_path)
        else:
            return jsonify({'error': f'Unsupported media type: {media_type}'}), 400
        
        # Cleanup
        cleanup_file(file_path)
        
        return jsonify(result)
        
    except Exception as e:
        # Cleanup on error
        if 'file_path' in locals() and file_path:
            cleanup_file(file_path)
            
        return jsonify({'error': str(e)}), 500

@bp.route('/batch-analyze', methods=['POST'])
@validate_api_key
def batch_analyze():
    data = request.json
    media_list = data.get('media_list', [])
    
    if not media_list:
        return jsonify({'error': 'Missing media_list'}), 400
    
    results = []
    for media in media_list:
        media_url = media.get('media_url')
        media_type = media.get('media_type')
        
        if not media_url or not media_type:
            results.append({'error': 'Missing media_url or media_type', 'media_url': media_url})
            continue
        
        try:
            # Download file
            file_path = download_file(media_url)
            
            if not file_path:
                results.append({'error': 'Failed to download file', 'media_url': media_url})
                continue
            
            # Analyze based on media type
            if media_type in ['image', 'jpg', 'jpeg', 'png']:
                result = analyze_image(file_path)
            elif media_type in ['video', 'mp4', 'mov', 'avi', 'mkv']:
                result = analyze_video(file_path)
            elif media_type in ['audio', 'wav', 'mp3']:
                result = analyze_audio(file_path)
            else:
                results.append({'error': f'Unsupported media type: {media_type}', 'media_url': media_url})
                continue
            
            # Add media URL to result
            result['media_url'] = media_url
            results.append(result)
            
            # Cleanup
            cleanup_file(file_path)
            
        except Exception as e:
            # Cleanup on error
            if 'file_path' in locals() and file_path:
                cleanup_file(file_path)
                
            results.append({'error': str(e), 'media_url': media_url})
    
    return jsonify({'results': results})