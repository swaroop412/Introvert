import cv2
import numpy as np
import base64
from fer import FER

class VideoAnalyzer:
    def __init__(self):
        # Initialize FER with MTCNN=False for faster OpenCV Haar Cascade detection
        self.detector = FER(mtcnn=False)

    def analyze_frame(self, base64_data):
        try:
            # Remove header if present
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            # Decode
            nparr = np.frombuffer(base64.b64decode(base64_data), np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return {"face_detected": False, "error": "Decode failed"}

            # Detect emotions
            # Returns list of dicts: [{'box': (x, y, w, h), 'emotions': {'angry': 0.1, ...}}]
            result = self.detector.detect_emotions(frame)
            
            if not result:
                return {"face_detected": False}
            
            # Get dominant emotion of the first face
            emotions = result[0]["emotions"]
            dominant_emotion = max(emotions, key=emotions.get)
            
            return {
                "face_detected": True,
                "dominant_emotion": dominant_emotion,
                "emotions": emotions
            }
        except Exception as e:
            print(f"CV Error: {e}")
            return {"face_detected": False, "error": str(e)}