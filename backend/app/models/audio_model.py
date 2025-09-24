import numpy as np
from datetime import datetime
from flask_socketio import emit
import librosa
from scipy import signal
from scipy.stats import kurtosis, skew
import warnings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")

class LightweightAudioDetector:
    def __init__(self):
        self.sample_rate = 16000
        logger.info("Lightweight audio detector initialized")
    
    def _load_audio(self, file_path):
        """Load and preprocess audio file with error handling"""
        try:
            # Load audio with librosa (lightweight approach)
            audio, sr = librosa.load(file_path, sr=self.sample_rate, duration=30)  # Limit to 30 seconds
            
            # Normalize audio
            if len(audio) > 0:
                audio = librosa.util.normalize(audio)
                return audio, sr
            else:
                raise ValueError("Empty audio file")
            
        except Exception as e:
            logger.error(f"Error loading audio: {str(e)}")
            return None, None
    
    def _extract_basic_features(self, audio, sr):
        """Extract basic audio features without heavy ML"""
        try:
            features = {}
            
            # 1. Zero crossing rate (voice naturalness indicator)
            zcr = librosa.feature.zero_crossing_rate(audio)[0]
            features['zcr_mean'] = np.mean(zcr)
            features['zcr_std'] = np.std(zcr)
            
            # 2. RMS energy (volume consistency)
            rms = librosa.feature.rms(y=audio)[0]
            features['rms_mean'] = np.mean(rms)
            features['rms_std'] = np.std(rms)
            
            # 3. Spectral centroid (brightness of sound)
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            features['spectral_centroid_mean'] = np.mean(spectral_centroids)
            features['spectral_centroid_std'] = np.std(spectral_centroids)
            
            # 4. Spectral rolloff (frequency distribution)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
            features['spectral_rolloff_mean'] = np.mean(spectral_rolloff)
            features['spectral_rolloff_std'] = np.std(spectral_rolloff)
            
            # 5. Basic MFCCs (first 5 coefficients only)
            mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=5)
            for i in range(5):
                features[f'mfcc_{i}_mean'] = np.mean(mfccs[i])
                features[f'mfcc_{i}_std'] = np.std(mfccs[i])
            
            # 6. Tempo estimation
            try:
                tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
                features['tempo'] = tempo
            except:
                features['tempo'] = 120  # Default
            
            # 7. Audio statistics
            features['audio_mean'] = np.mean(audio)
            features['audio_std'] = np.std(audio)
            features['audio_skewness'] = skew(audio) if len(audio) > 1 else 0
            features['audio_kurtosis'] = kurtosis(audio) if len(audio) > 1 else 0
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting basic features: {str(e)}")
            return {}
    
    def _analyze_voice_naturalness(self, audio, sr):
        """Analyze if voice sounds natural using simple techniques"""
        try:
            issues = []
            
            # 1. Check for unnatural silence patterns
            rms = librosa.feature.rms(y=audio)[0]
            silence_threshold = np.mean(rms) * 0.1
            silence_frames = rms < silence_threshold
            
            # Count silence segments
            silence_changes = np.diff(silence_frames.astype(int))
            silence_segments = np.sum(silence_changes == 1)
            
            if silence_segments < 2:  # Too few pauses
                issues.append({
                    "type": "Unnatural silence pattern",
                    "severity": "medium",
                    "description": "Missing natural speech pauses"
                })
            
            # 2. Check pitch consistency (simplified)
            # Split audio into segments and check variance
            segment_length = sr * 2  # 2-second segments
            pitch_estimates = []
            
            for i in range(0, len(audio) - segment_length, segment_length):
                segment = audio[i:i+segment_length]
                
                # Simple pitch estimation using autocorrelation
                autocorr = np.correlate(segment, segment, mode='full')
                autocorr = autocorr[len(autocorr)//2:]
                
                # Find fundamental frequency (simplified)
                if len(autocorr) > sr//50:  # At least 50Hz
                    peak_idx = np.argmax(autocorr[sr//400:sr//50]) + sr//400  # 50-400Hz range
                    if peak_idx > 0:
                        pitch = sr / peak_idx
                        pitch_estimates.append(pitch)
            
            if len(pitch_estimates) > 1:
                pitch_var = np.var(pitch_estimates)
                if pitch_var < 100:  # Too consistent (robotic)
                    issues.append({
                        "type": "Unnatural pitch consistency",
                        "severity": "high",
                        "description": "Voice pitch appears artificially consistent"
                    })
                elif pitch_var > 10000:  # Too inconsistent
                    issues.append({
                        "type": "Pitch inconsistency",
                        "severity": "medium",
                        "description": "Unusual pitch variations detected"
                    })
            
            # 3. Check for artifacts in frequency spectrum
            D = np.abs(librosa.stft(audio))
            
            # Look for unusual frequency patterns
            freq_means = np.mean(D, axis=1)
            freq_variance = np.var(freq_means)
            
            if freq_variance > np.mean(freq_means) * 5:  # High variance in frequency content
                issues.append({
                    "type": "Frequency artifacts",
                    "severity": "high",
                    "description": "Suspicious frequency patterns suggesting synthesis"
                })
            
            return issues
            
        except Exception as e:
            logger.error(f"Error analyzing voice naturalness: {str(e)}")
            return []
    
    def _detect_synthesis_patterns(self, audio, sr):
        """Simple synthesis detection without ML models"""
        try:
            artifacts = []
            
            # 1. Check for repetitive patterns (common in AI)
            # Use autocorrelation to find repetitive segments
            autocorr = np.correlate(audio, audio, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            
            # Look for strong periodicity beyond normal speech patterns
            peaks, _ = signal.find_peaks(autocorr, height=np.max(autocorr) * 0.3)
            
            if len(peaks) > 20:  # Too many repetitive patterns
                artifacts.append({
                    "type": "Repetitive patterns",
                    "severity": "high",
                    "description": "Excessive repetitive patterns suggesting AI synthesis"
                })
            
            # 2. Check spectral consistency (AI often produces too-consistent spectra)
            stft = librosa.stft(audio)
            magnitude = np.abs(stft)
            
            # Check variance across time frames
            frame_variances = np.var(magnitude, axis=0)
            avg_variance = np.mean(frame_variances)
            
            if avg_variance < 0.01:  # Too consistent
                artifacts.append({
                    "type": "Spectral consistency",
                    "severity": "medium",
                    "description": "Spectrum too consistent, possibly AI-generated"
                })
            
            # 3. Dynamic range analysis
            dynamic_range = np.max(audio) - np.min(audio)
            
            if dynamic_range < 0.1:  # Too compressed
                artifacts.append({
                    "type": "Limited dynamic range",
                    "severity": "medium",
                    "description": "Audio dynamic range suggests artificial processing"
                })
            
            return artifacts
            
        except Exception as e:
            logger.error(f"Error detecting synthesis patterns: {str(e)}")
            return []
    
    def detect(self, file_path, session_id=None, progress_dict=None):
        """Main lightweight audio detection"""
        try:
            # Update progress
            if progress_dict is not None and session_id is not None:
                progress_dict[session_id] = 20
                emit('progress_update', {'progress': 20, 'message': 'Loading audio...'}, room=session_id)
            
            # Load audio
            audio, sr = self._load_audio(file_path)
            if audio is None:
                raise ValueError("Could not load audio file")
            
            if progress_dict is not None and session_id is not None:
                progress_dict[session_id] = 40
                emit('progress_update', {'progress': 40, 'message': 'Extracting features...'}, room=session_id)
            
            # Extract features
            features = self._extract_basic_features(audio, sr)
            
            if progress_dict is not None and session_id is not None:
                progress_dict[session_id] = 70
                emit('progress_update', {'progress': 70, 'message': 'Analyzing voice patterns...'}, room=session_id)
            
            # Analyze voice naturalness
            voice_issues = self._analyze_voice_naturalness(audio, sr)
            
            # Detect synthesis patterns
            synthesis_artifacts = self._detect_synthesis_patterns(audio, sr)
            
            # LIGHTWEIGHT DETECTION ALGORITHM
            suspicious_score = 0
            anomalies = []
            
            # Rule 1: Zero crossing rate (unnatural if too consistent)
            if features.get('zcr_std', 0.01) < 0.005:
                suspicious_score += 0.2
                anomalies.append({
                    "type": "Unnatural voice consistency",
                    "severity": "medium",
                    "description": "Voice patterns too consistent for natural speech"
                })
            
            # Rule 2: RMS energy consistency
            if features.get('rms_std', 0.1) < 0.05:
                suspicious_score += 0.15
                anomalies.append({
                    "type": "Volume consistency",
                    "severity": "medium",
                    "description": "Audio volume artificially consistent"
                })
            
            # Rule 3: Spectral centroid (brightness)
            spectral_std = features.get('spectral_centroid_std', 500)
            if spectral_std < 200:
                suspicious_score += 0.15
                anomalies.append({
                    "type": "Spectral uniformity",
                    "severity": "medium",
                    "description": "Audio brightness artificially uniform"
                })
            
            # Rule 4: MFCC consistency (first coefficient is most important)
            mfcc_0_std = features.get('mfcc_0_std', 10)
            if mfcc_0_std < 5:
                suspicious_score += 0.2
                anomalies.append({
                    "type": "MFCC uniformity",
                    "severity": "high",
                    "description": "Voice characteristics too uniform"
                })
            
            # Add voice analysis issues
            for issue in voice_issues:
                suspicious_score += 0.1
                anomalies.append(issue)
            
            # Add synthesis artifacts
            for artifact in synthesis_artifacts:
                suspicious_score += 0.15
                anomalies.append(artifact)
            
            # Determine result
            is_deepfake = suspicious_score > 0.5
            
            # Calculate confidence
            if is_deepfake:
                confidence = min(65 + suspicious_score * 30, 95)
            else:
                confidence = max(75 - suspicious_score * 25, 60)
            
            if progress_dict is not None and session_id is not None:
                progress_dict[session_id] = 100
                emit('progress_update', {'progress': 100, 'message': 'Analysis complete'}, room=session_id)
            
            # Calculate audio duration
            duration = len(audio) / sr
            
            return {
                "isDeepfake": bool(is_deepfake),
                "confidence": float(confidence),
                "processingTime": 1.0,
                "anomalies": anomalies,
                "mediaType": "audio",
                "duration": float(duration),
                "sampleRate": int(sr),
                "modelUsed": "Lightweight Signal Processing",
                "inconsistencyCount": len(voice_issues),
                "artifactCount": len(synthesis_artifacts),
                "timestamp": datetime.now().isoformat(),
                "features": {
                    "zcr_consistency": features.get('zcr_std', 0),
                    "rms_consistency": features.get('rms_std', 0),
                    "suspicious_score": suspicious_score
                }
            }
            
        except Exception as e:
            logger.error(f"Error in lightweight audio detection: {str(e)}")
            return {
                "isDeepfake": False,
                "confidence": 50.0,
                "processingTime": 0.5,
                "anomalies": [],
                "mediaType": "audio",
                "duration": 0.0,
                "sampleRate": self.sample_rate,
                "modelUsed": "Error",
                "inconsistencyCount": 0,
                "artifactCount": 0,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

# Global detector instance
detector = LightweightAudioDetector()

def analyze_audio(file_path, session_id=None, progress_dict=None):
    """Main function called by the Flask app"""
    return detector.detect(file_path, session_id, progress_dict)