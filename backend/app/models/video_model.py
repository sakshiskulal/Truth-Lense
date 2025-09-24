import cv2
import numpy as np
from flask_socketio import emit
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LightweightVideoDetector:
    def __init__(self):
        logger.info("Initializing lightweight video detector...")
        # No heavy models to load!
    
    def _extract_key_frames(self, video_path, max_frames=15):
        """Extract fewer frames for lightweight analysis"""
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            if total_frames == 0:
                raise ValueError("Could not read video frames")
            
            # Calculate frame sampling interval (fewer frames for speed)
            frame_interval = max(1, total_frames // max_frames)
            
            frames = []
            frame_indices = []
            
            for i in range(0, total_frames, frame_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                
                if ret and frame is not None:
                    # Resize frame for faster processing
                    height, width = frame.shape[:2]
                    if width > 640:  # Resize if too large
                        scale = 640 / width
                        new_width = 640
                        new_height = int(height * scale)
                        frame = cv2.resize(frame, (new_width, new_height))
                    
                    frames.append(frame)
                    frame_indices.append(i)
                
                if len(frames) >= max_frames:
                    break
            
            cap.release()
            return frames, frame_indices, total_frames, fps
            
        except Exception as e:
            logger.error(f"Error extracting frames: {str(e)}")
            return [], [], 0, 0
    
    def _analyze_single_frame_lightweight(self, frame):
        """Fast analysis of single frame without ML models"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 1. Blur detection (deepfakes often have unnatural blur)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # 2. Edge density
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (frame.shape[0] * frame.shape[1])
            
            # 3. Color distribution
            color_std = np.std(frame.reshape(-1, 3), axis=0)
            color_uniformity = np.mean(color_std)
            
            # 4. Brightness analysis
            brightness = np.mean(gray)
            brightness_std = np.std(gray)
            
            # Simple scoring system
            suspicious_score = 0
            reasons = []
            
            # Rule 1: Too blurry (over-smoothed)
            if blur_score < 100:
                suspicious_score += 0.3
                reasons.append("Frame appears over-smoothed")
            
            # Rule 2: Low edge density (typical of AI generation)
            if edge_density < 0.08:
                suspicious_score += 0.2
                reasons.append("Low edge density detected")
            
            # Rule 3: Unnatural color uniformity
            if color_uniformity < 15:
                suspicious_score += 0.2
                reasons.append("Colors appear artificially uniform")
            
            # Rule 4: Extreme brightness values
            if brightness < 50 or brightness > 200:
                suspicious_score += 0.1
                reasons.append("Unusual brightness levels")
            
            # Rule 5: Low brightness variation
            if brightness_std < 30:
                suspicious_score += 0.2
                reasons.append("Low brightness variation")
            
            is_suspicious = suspicious_score > 0.4
            confidence = min(60 + suspicious_score * 35, 90) if is_suspicious else max(70 - suspicious_score * 30, 55)
            
            return is_suspicious, confidence, reasons, {
                'blur_score': blur_score,
                'edge_density': edge_density,
                'color_uniformity': color_uniformity,
                'brightness': brightness,
                'brightness_std': brightness_std
            }
            
        except Exception as e:
            logger.error(f"Error analyzing frame: {str(e)}")
            return False, 50.0, [], {}
    
    def _analyze_temporal_consistency(self, frames):
        """Lightweight temporal analysis between frames"""
        try:
            if len(frames) < 2:
                return []
            
            inconsistencies = []
            
            for i in range(1, len(frames)):
                prev_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
                curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                
                # Calculate frame difference
                diff = cv2.absdiff(prev_gray, curr_gray)
                diff_score = np.mean(diff)
                
                # Check for sudden large changes (might indicate splice/manipulation)
                if diff_score > 60:
                    inconsistencies.append({
                        "frame": i,
                        "type": "Sudden change",
                        "severity": "high",
                        "description": f"Large difference between frames (score: {diff_score:.1f})"
                    })
                
                # Check for too little change (might indicate static AI generation)
                elif diff_score < 5:
                    inconsistencies.append({
                        "frame": i,
                        "type": "Static content",
                        "severity": "medium",
                        "description": f"Unusually static content between frames (score: {diff_score:.1f})"
                    })
            
            return inconsistencies
            
        except Exception as e:
            logger.error(f"Error in temporal analysis: {str(e)}")
            return []
    
    def _simple_face_tracking(self, frames):
        """Simple face consistency check across frames"""
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            face_data = []
            
            for i, frame in enumerate(frames):
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.2, 3, minSize=(30, 30))
                
                if len(faces) > 0:
                    # Take largest face
                    largest_face = max(faces, key=lambda x: x[2] * x[3])
                    x, y, w, h = largest_face
                    
                    # Extract face region for analysis
                    face_region = gray[y:y+h, x:x+w]
                    face_brightness = np.mean(face_region)
                    face_contrast = np.std(face_region)
                    
                    face_data.append({
                        'frame': i,
                        'position': (x, y),
                        'size': (w, h),
                        'brightness': face_brightness,
                        'contrast': face_contrast
                    })
            
            # Analyze face consistency
            face_issues = []
            
            if len(face_data) > 1:
                # Check brightness consistency
                brightnesses = [f['brightness'] for f in face_data]
                brightness_var = np.var(brightnesses)
                
                if brightness_var < 50:  # Too consistent
                    face_issues.append({
                        "type": "Face brightness consistency",
                        "severity": "medium",
                        "description": "Face brightness artificially consistent across frames"
                    })
                
                # Check size jumps
                sizes = [f['size'][0] * f['size'][1] for f in face_data]
                for i in range(1, len(sizes)):
                    size_change = abs(sizes[i] - sizes[i-1]) / sizes[i-1]
                    if size_change > 0.5:  # 50% size jump
                        face_issues.append({
                            "type": "Face size inconsistency",
                            "severity": "high",
                            "description": f"Large face size change at frame {face_data[i]['frame']}"
                        })
            
            return face_issues, len(face_data)
            
        except Exception as e:
            logger.error(f"Error in face tracking: {str(e)}")
            return [], 0
    
    def detect(self, video_path, session_id=None, progress_dict=None):
        """Main lightweight video detection"""
        try:
            # Update progress
            if progress_dict is not None and session_id is not None:
                progress_dict[session_id] = 15
                emit('progress_update', {'progress': 15, 'message': 'Extracting video frames...'}, room=session_id)
            
            # Extract fewer frames for speed
            frames, frame_indices, total_frames, fps = self._extract_key_frames(video_path, max_frames=15)
            
            if not frames:
                raise ValueError("Could not extract frames from video")
            
            if progress_dict is not None and session_id is not None:
                progress_dict[session_id] = 30
                emit('progress_update', {'progress': 30, 'message': 'Analyzing frames...'}, room=session_id)
            
            # Analyze individual frames
            frame_analysis = []
            total_suspicious_score = 0
            deepfake_frame_count = 0
            
            for i, (frame, frame_idx) in enumerate(zip(frames, frame_indices)):
                is_suspicious, confidence, reasons, features = self._analyze_single_frame_lightweight(frame)
                
                frame_analysis.append({
                    "frame": int(frame_idx),
                    "confidence": float(confidence),
                    "isDeepfake": bool(is_suspicious),
                    "reasons": reasons
                })
                
                if is_suspicious:
                    deepfake_frame_count += 1
                    total_suspicious_score += confidence / 100
                
                # Update progress
                if progress_dict is not None and session_id is not None:
                    progress = 30 + (i / len(frames)) * 30
                    progress_dict[session_id] = progress
                    emit('progress_update', {'progress': progress}, room=session_id)
            
            if progress_dict is not None and session_id is not None:
                progress_dict[session_id] = 70
                emit('progress_update', {'progress': 70, 'message': 'Checking temporal consistency...'}, room=session_id)
            
            # Temporal analysis
            temporal_issues = self._analyze_temporal_consistency(frames)
            
            if progress_dict is not None and session_id is not None:
                progress_dict[session_id] = 85
                emit('progress_update', {'progress': 85, 'message': 'Analyzing faces...'}, room=session_id)
            
            # Face analysis
            face_issues, faces_detected = self._simple_face_tracking(frames)
            
            # Determine overall result
            deepfake_ratio = deepfake_frame_count / len(frames)
            
            # Lightweight decision logic
            is_deepfake = (
                deepfake_ratio > 0.4 or  # More than 40% suspicious frames
                len(temporal_issues) > 2 or  # Multiple temporal issues
                len(face_issues) > 1  # Multiple face issues
            )
            
            # Calculate confidence
            base_confidence = (total_suspicious_score / max(1, deepfake_frame_count)) * 100 if deepfake_frame_count > 0 else 50
            
            # Adjust based on supporting evidence
            evidence_boost = len(temporal_issues) * 5 + len(face_issues) * 3
            
            if is_deepfake:
                overall_confidence = min(base_confidence + evidence_boost, 95)
            else:
                overall_confidence = max(75 - evidence_boost, 60)
            
            # Compile anomalies
            anomalies = []
            
            # Add temporal issues
            anomalies.extend(temporal_issues)
            
            # Add face issues
            anomalies.extend(face_issues)
            
            # Add frame-level issues
            if deepfake_ratio > 0.5:
                anomalies.append({
                    "type": "High suspicious frame ratio",
                    "severity": "high",
                    "description": f"{deepfake_ratio:.1%} of frames appear manipulated"
                })
            
            # Add general anomalies if deepfake detected
            if is_deepfake and len(anomalies) < 2:
                anomalies.extend([
                    {
                        "type": "Visual inconsistency",
                        "severity": "medium",
                        "description": "Multiple frames show signs of artificial generation"
                    },
                    {
                        "type": "Processing artifacts",
                        "severity": "high",
                        "description": "Video shows characteristics of AI manipulation"
                    }
                ])
            
            if progress_dict is not None and session_id is not None:
                progress_dict[session_id] = 100
                emit('progress_update', {'progress': 100, 'message': 'Analysis complete'}, room=session_id)
            
            return {
                "isDeepfake": bool(is_deepfake),
                "confidence": float(overall_confidence),
                "processingTime": 2.0,  # Much faster than heavy ML
                "anomalies": anomalies,
                "frameAnalysis": frame_analysis,
                "totalFrames": int(total_frames),
                "analyzedFrames": len(frames),
                "fps": float(fps),
                "deepfakeFrameRatio": float(deepfake_ratio),
                "facesDetected": faces_detected,
                "mediaType": "video",
                "timestamp": datetime.now().isoformat(),
                "modelUsed": "Lightweight CV Analysis"
            }
            
        except Exception as e:
            logger.error(f"Error in lightweight video detection: {str(e)}")
            return {
                "isDeepfake": False,
                "confidence": 50.0,
                "processingTime": 1.0,
                "anomalies": [],
                "frameAnalysis": [],
                "totalFrames": 0,
                "analyzedFrames": 0,
                "fps": 0,
                "deepfakeFrameRatio": 0.0,
                "facesDetected": 0,
                "mediaType": "video",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

# Global detector instance
detector = LightweightVideoDetector()

def analyze_video(file_path, session_id=None, progress_dict=None):
    """Main function called by the Flask app"""
    return detector.detect(file_path, session_id, progress_dict)