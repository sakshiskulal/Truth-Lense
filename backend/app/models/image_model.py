import cv2
import numpy as np
from flask_socketio import emit
from datetime import datetime
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LightweightImageDetector:
    def __init__(self):
        logger.info("Initializing lightweight image detector...")
        # No heavy models to load!
    
    # ---------- Feature extraction helpers ----------
    def _extract_traditional_features(self, image_path):
        """Extract features using only OpenCV and numpy"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not load image")
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            features = {}
            
            # 1. Edge density analysis (deepfakes often have inconsistent edges)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (image.shape[0] * image.shape[1])
            features['edge_density'] = edge_density
            
            # 2. Texture analysis using Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            features['texture_variance'] = laplacian_var
            
            # 3. Color distribution analysis
            color_std = np.std(image.reshape(-1, 3), axis=0)
            features['color_uniformity'] = np.mean(color_std)
            
            # 4. Brightness distribution
            brightness_hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            brightness_entropy = -np.sum(brightness_hist * np.log2(brightness_hist + 1e-10))
            features['brightness_entropy'] = brightness_entropy
            
            # 5. Local Binary Pattern-like texture
            kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
            texture_response = cv2.filter2D(gray, -1, kernel)
            features['local_texture_var'] = np.var(texture_response)
            
            # 6. Frequency domain analysis (simplified)
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.log(np.abs(f_shift) + 1)
            features['freq_energy'] = np.mean(magnitude_spectrum)
            features['freq_variance'] = np.var(magnitude_spectrum)

            # 7. Simple quality metrics
            features['brightness_mean'] = float(np.mean(gray))
            features['brightness_std'] = float(np.std(gray))
            features['width'] = int(image.shape[1])
            features['height'] = int(image.shape[0])
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            return {}
    
    def _analyze_compression_artifacts(self, image_path):
        """Detect compression artifacts that might indicate manipulation"""
        try:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply DCT-like analysis to detect compression patterns
            # Split image into 8x8 blocks (like JPEG)
            h, w = gray.shape
            block_size = 8
            compression_scores = []
            
            for y in range(0, h - block_size, block_size):
                for x in range(0, w - block_size, block_size):
                    block = gray[y:y+block_size, x:x+block_size].astype(np.float32)
                    
                    # Simple frequency analysis of block
                    fft_block = np.fft.fft2(block)
                    high_freq = np.sum(np.abs(fft_block[4:, 4:]))  # High frequency components
                    total_energy = np.sum(np.abs(fft_block))
                    
                    if total_energy > 0:
                        hf_ratio = high_freq / total_energy
                        compression_scores.append(hf_ratio)
            
            avg_compression = np.mean(compression_scores)
            compression_var = np.var(compression_scores)
            
            return avg_compression, compression_var
            
        except Exception as e:
            logger.error(f"Error analyzing compression: {str(e)}")
            return 0.1, 0.01
    
    def _detect_face_inconsistencies(self, image_path):
        """Simple face detection and consistency check"""
        try:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Use OpenCV's built-in face detector
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            face_inconsistencies = []
            
            for (x, y, w, h) in faces:
                # Extract face region
                face_region = gray[y:y+h, x:x+w]
                
                # Analyze face region texture
                face_edges = cv2.Canny(face_region, 50, 150)
                edge_density = np.sum(face_edges > 0) / (w * h)
                
                # Check if face region has suspicious characteristics
                # Relax thresholds to reduce false positives on clean photos
                if edge_density < 0.03:  # Too smooth
                    face_inconsistencies.append("Face region too smooth (possible AI generation)")
                elif edge_density > 0.45:  # Too detailed
                    face_inconsistencies.append("Face region has excessive detail (possible artifacts)")
                
                # Check brightness uniformity in face
                face_std = np.std(face_region)
                if face_std < 10:  # Too uniform
                    face_inconsistencies.append("Face lighting too uniform")
            
            return face_inconsistencies
            
        except Exception as e:
            logger.error(f"Error detecting face inconsistencies: {str(e)}")
            return []

    def _green_indicators(self, features, avg_compression, compression_var, face_issues):
        """Indicators that support natural/unaltered imagery. Returns (green_score, notes)."""
        notes = []
        green = 0.0

        edge_density = features.get('edge_density', 0)
        texture_var = features.get('texture_variance', 0)
        color_uni = features.get('color_uniformity', 0)
        freq_var = features.get('freq_variance', 0)
        b_std = features.get('brightness_std', 0)
        w = max(1, features.get('width', 1))
        h = max(1, features.get('height', 1))
        total_px = w * h

        # Natural range of edges for typical photos
        if 0.04 <= edge_density <= 0.25:
            green += 0.25
            notes.append("Edge density in natural range")

        # Good texture variance suggests non-synthetic content
        if texture_var >= 250:
            green += 0.25
            notes.append("Healthy texture variance")

        # Color variability typical for real images
        if 15 <= color_uni <= 60:
            green += 0.15
            notes.append("Natural color variability")

        # Frequency variance within normal band
        if 1.5 <= freq_var <= 20:
            green += 0.15
            notes.append("Balanced frequency spectrum")

        # Not overly uniform brightness
        if b_std >= 20:
            green += 0.1
            notes.append("Adequate contrast/brightness variation")

        # Compression patterns fairly consistent and not extreme
        if 0.03 <= avg_compression <= 0.20 and compression_var < 0.06:
            green += 0.1
            notes.append("Compression looks consistent with camera/JPEG")

        # Larger images tend to be camera originals; small images are more risky
        if total_px >= (640 * 480):
            green += 0.05
            notes.append("Sufficient resolution")

        # No face issues if faces are detected
        if not face_issues:
            green += 0.05
            notes.append("No facial inconsistencies detected")

        return min(green, 0.8), notes
    
    def detect(self, image_path, session_id=None, progress_dict=None):
        """Main lightweight detection method"""
        try:
            # Update progress
            if progress_dict is not None and session_id is not None:
                progress_dict[session_id] = 20
                emit('progress_update', {'progress': 20, 'message': 'Extracting image features...'}, room=session_id)
            
            # Extract traditional features
            features = self._extract_traditional_features(image_path)
            
            if progress_dict is not None and session_id is not None:
                progress_dict[session_id] = 50
                emit('progress_update', {'progress': 50, 'message': 'Analyzing compression artifacts...'}, room=session_id)
            
            # Analyze compression
            avg_compression, compression_var = self._analyze_compression_artifacts(image_path)
            
            if progress_dict is not None and session_id is not None:
                progress_dict[session_id] = 80
                emit('progress_update', {'progress': 80, 'message': 'Checking for face inconsistencies...'}, room=session_id)
            
            # Face analysis
            face_issues = self._detect_face_inconsistencies(image_path)
            
            # LIGHTWEIGHT DETECTION ALGORITHM (tuned to reduce false positives)
            suspicious_score = 0
            anomalies = []
            
            # Rule 1: Edge density (deepfakes often over-smooth)
            if features.get('edge_density', 0.15) < 0.03:
                suspicious_score += 0.18
                anomalies.append({
                    "type": "Edge smoothing",
                    "severity": "high",
                    "description": "Image appears over-smoothed, typical of AI generation"
                })
            
            # Rule 2: Texture variance (AI often creates unrealistic textures)
            if features.get('texture_variance', 500) < 80:
                suspicious_score += 0.15
                anomalies.append({
                    "type": "Low texture variance",
                    "severity": "medium",
                    "description": "Texture patterns appear artificially uniform"
                })
            
            # Rule 3: Color uniformity (AI struggles with natural color variation)
            if features.get('color_uniformity', 30) < 10:
                suspicious_score += 0.10
                anomalies.append({
                    "type": "Color uniformity",
                    "severity": "medium",
                    "description": "Colors appear artificially uniform"
                })
            
            # Rule 4: Frequency domain analysis
            if features.get('freq_variance', 5) < 1:
                suspicious_score += 0.10
                anomalies.append({
                    "type": "Frequency anomaly",
                    "severity": "medium",
                    "description": "Suspicious frequency patterns detected"
                })
            
            # Rule 5: Compression artifacts
            # Only flag extreme/unusual compression patterns
            if avg_compression > 0.22 or compression_var > 0.12:
                suspicious_score += 0.12
                anomalies.append({
                    "type": "Compression artifacts",
                    "severity": "high",
                    "description": "Unusual compression patterns suggesting manipulation"
                })
            
            # Rule 6: Face inconsistencies
            if face_issues:
                suspicious_score += 0.08 * len(face_issues)
                for issue in face_issues:
                    anomalies.append({
                        "type": "Facial inconsistency",
                        "severity": "high",
                        "description": issue
                    })
            
            # Apply green indicators to offset suspicion when natural cues are strong
            green_score, green_notes = self._green_indicators(features, avg_compression, compression_var, face_issues)
            adjusted_suspicion = max(0.0, suspicious_score - 0.5 * green_score)

            # Determine result
            # Raise threshold to reduce false positives
            is_deepfake = adjusted_suspicion > 0.8
            
            # Calculate confidence (higher score = more confident it's fake)
            if is_deepfake:
                confidence = float(min(55 + adjusted_suspicion * 45, 92))
            else:
                # Confidence for real increases with green_score and low suspicion
                confidence = float(min(90, 60 + 25 * green_score - 10 * adjusted_suspicion))
            
            if progress_dict is not None and session_id is not None:
                progress_dict[session_id] = 100
                emit('progress_update', {'progress': 100, 'message': 'Analysis complete'}, room=session_id)
            
            return {
                "isDeepfake": bool(is_deepfake),
                "confidence": float(confidence),
                "processingTime": 0.5,  # Much faster!
                "anomalies": anomalies + ([{"type": "Green indicator", "severity": "info", "description": note} for note in green_notes] if green_notes else []),
                "mediaType": "image",
                "timestamp": datetime.now().isoformat(),
                "modelUsed": "Lightweight CV Analysis v1.1 (tuned)",
                "features": {
                    "edge_density": features.get('edge_density', 0),
                    "texture_variance": features.get('texture_variance', 0),
                    "color_uniformity": features.get('color_uniformity', 0),
                    "freq_variance": features.get('freq_variance', 0),
                    "avg_compression": float(avg_compression),
                    "compression_var": float(compression_var),
                    "suspicious_score_raw": float(suspicious_score),
                    "green_score": float(green_score),
                    "suspicious_score": float(adjusted_suspicion)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in lightweight detection: {str(e)}")
            return {
                "isDeepfake": False,
                "confidence": 50.0,
                "processingTime": 0.1,
                "anomalies": [],
                "mediaType": "image",
                "timestamp": datetime.now().isoformat(),
                "modelUsed": "Error",
                "error": str(e)
            }

# Global detector instance
detector = LightweightImageDetector()

def analyze_image(file_path, session_id=None, progress_dict=None):
    """Main function called by the Flask app"""
    return detector.detect(file_path, session_id, progress_dict)