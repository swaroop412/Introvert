print("=" * 80)
print("ORATORIQ - FER HOOK WITH FACE-API.JS INTEGRATION")
print("=" * 80)

import os

hooks_dir = "oratoriq/client/src/hooks"
os.makedirs(hooks_dir, exist_ok=True)

# ============================================================================
# useFaceAPI Hook - Lazy loading, 5-10 FPS detection, attention tracking
# ============================================================================
faceapi_hook = """import { useEffect, useRef, useState } from 'react';
import * as faceapi from 'face-api.js';
import { FaceDetectionResult, FacialEvent, FacialExpression, FacialEventType } from '../../../shared/types';

interface UseFaceAPIOptions {
  videoElement: HTMLVideoElement | null;
  enabled: boolean;
  targetFPS?: number; // 5-10 FPS for CPU efficiency
  onDetection?: (result: FaceDetectionResult) => void;
  onEvent?: (event: FacialEvent) => void;
}

interface UseFaceAPIReturn {
  isModelsLoaded: boolean;
  isDetecting: boolean;
  currentExpression: FaceDetectionResult | null;
  error: string | null;
  startDetection: () => void;
  stopDetection: () => void;
}

const MODEL_URL = '/models'; // Models will be served from public/models

export const useFaceAPI = ({
  videoElement,
  enabled,
  targetFPS = 7, // Default 7 FPS for balance
  onDetection,
  onEvent,
}: UseFaceAPIOptions): UseFaceAPIReturn => {
  const [isModelsLoaded, setIsModelsLoaded] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [currentExpression, setCurrentExpression] = useState<FaceDetectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const detectionIntervalRef = useRef<number | null>(null);
  const modelsLoadedRef = useRef(false);
  const previousExpressionRef = useRef<FacialEventType | null>(null);

  // Lazy load face-api.js models on first use
  useEffect(() => {
    const loadModels = async () => {
      if (modelsLoadedRef.current) return;

      try {
        console.log('🔄 Loading face-api.js models...');
        
        // Load only necessary models for expression detection
        await Promise.all([
          faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
          faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL),
          faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
        ]);

        modelsLoadedRef.current = true;
        setIsModelsLoaded(true);
        console.log('✓ face-api.js models loaded successfully');
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error loading models';
        console.error('✗ Failed to load face-api.js models:', errorMessage);
        setError(`Model loading failed: ${errorMessage}`);
      }
    };

    if (enabled) {
      loadModels();
    }
  }, [enabled]);

  // Calculate attention score from landmarks and face presence
  const calculateAttentionScore = (
    detected: boolean,
    landmarks?: faceapi.FaceLandmarks68
  ): number => {
    if (!detected) return 0;
    
    if (!landmarks) return 0.5; // Face detected but no landmarks
    
    // Analyze eye regions and face orientation
    const leftEye = landmarks.getLeftEye();
    const rightEye = landmarks.getRightEye();
    const nose = landmarks.getNose();
    
    // Simple attention heuristic: eyes visible and nose centered
    const eyesVisible = leftEye.length > 0 && rightEye.length > 0;
    const noseCentered = nose.length > 0;
    
    // Calculate face angle (simplified)
    if (eyesVisible && noseCentered) {
      const leftEyeCenter = leftEye[0];
      const rightEyeCenter = rightEye[0];
      const eyeDistance = Math.abs(rightEyeCenter.x - leftEyeCenter.x);
      
      // Normalized attention score based on eye distance (frontal face = higher score)
      const attentionScore = Math.min(eyeDistance / 100, 1.0);
      return Math.max(0.6, attentionScore); // Minimum 0.6 if face detected
    }
    
    return 0.5; // Default moderate attention
  };

  // Determine dominant expression
  const getDominantExpression = (expressions: FacialExpression): FacialEventType => {
    const expressionMap: [keyof FacialExpression, FacialEventType][] = [
      ['neutral', 'neutral'],
      ['happy', 'happy'],
      ['sad', 'sad'],
      ['angry', 'angry'],
      ['fearful', 'fearful'],
      ['disgusted', 'disgusted'],
      ['surprised', 'surprised'],
    ];

    let maxScore = 0;
    let dominant: FacialEventType = 'neutral';

    for (const [expr, eventType] of expressionMap) {
      if (expressions[expr] > maxScore) {
        maxScore = expressions[expr];
        dominant = eventType;
      }
    }

    return dominant;
  };

  // Perform face detection and expression recognition
  const detectFace = async () => {
    if (!videoElement || !modelsLoadedRef.current) return;

    try {
      const detection = await faceapi
        .detectSingleFace(videoElement, new faceapi.TinyFaceDetectorOptions())
        .withFaceExpressions()
        .withFaceLandmarks();

      const timestamp = Date.now();

      if (detection) {
        const expressions: FacialExpression = {
          neutral: detection.expressions.neutral,
          happy: detection.expressions.happy,
          sad: detection.expressions.sad,
          angry: detection.expressions.angry,
          fearful: detection.expressions.fearful,
          disgusted: detection.expressions.disgusted,
          surprised: detection.expressions.surprised,
        };

        const attentionScore = calculateAttentionScore(true, detection.landmarks);

        const result: FaceDetectionResult = {
          timestamp,
          detected: true,
          expressions,
          landmarks: {
            positions: detection.landmarks.positions.map((p) => ({ x: p.x, y: p.y })),
          },
          attentionScore,
        };

        setCurrentExpression(result);
        onDetection?.(result);

        // Emit event on expression change
        const dominantExpression = getDominantExpression(expressions);
        if (dominantExpression !== previousExpressionRef.current) {
          const event: FacialEvent = {
            timestamp,
            eventType: dominantExpression,
            confidence: expressions[dominantExpression],
            expressions,
            attentionScore,
          };
          
          onEvent?.(event);
          previousExpressionRef.current = dominantExpression;
        }
      } else {
        // No face detected
        const result: FaceDetectionResult = {
          timestamp,
          detected: false,
          expressions: {
            neutral: 0,
            happy: 0,
            sad: 0,
            angry: 0,
            fearful: 0,
            disgusted: 0,
            surprised: 0,
          },
          attentionScore: 0,
        };

        setCurrentExpression(result);
        onDetection?.(result);

        // Reset previous expression
        if (previousExpressionRef.current !== null) {
          previousExpressionRef.current = null;
        }
      }
    } catch (err) {
      console.error('Face detection error:', err);
    }
  };

  // Start detection loop
  const startDetection = () => {
    if (!isModelsLoaded || !videoElement) {
      console.warn('Cannot start detection: models not loaded or video element missing');
      return;
    }

    if (detectionIntervalRef.current) {
      return; // Already detecting
    }

    const intervalMs = 1000 / targetFPS;
    detectionIntervalRef.current = window.setInterval(() => {
      detectFace();
    }, intervalMs);

    setIsDetecting(true);
    console.log(`✓ Face detection started at ${targetFPS} FPS`);
  };

  // Stop detection loop
  const stopDetection = () => {
    if (detectionIntervalRef.current) {
      clearInterval(detectionIntervalRef.current);
      detectionIntervalRef.current = null;
    }

    setIsDetecting(false);
    setCurrentExpression(null);
    previousExpressionRef.current = null;
    console.log('⏹ Face detection stopped');
  };

  // Auto-start/stop based on enabled prop
  useEffect(() => {
    if (enabled && isModelsLoaded && videoElement) {
      startDetection();
    } else {
      stopDetection();
    }

    return () => {
      stopDetection();
    };
  }, [enabled, isModelsLoaded, videoElement]);

  return {
    isModelsLoaded,
    isDetecting,
    currentExpression,
    error,
    startDetection,
    stopDetection,
  };
};
"""

hook_path = os.path.join(hooks_dir, "useFaceAPI.ts")
with open(hook_path, 'w') as f:
    f.write(faceapi_hook)

print(f"\n✓ Created {hook_path}")

print("\n" + "=" * 80)
print("FACE-API.JS HOOK CREATED")
print("=" * 80)
print("\n✅ Features implemented:")
print("  • Lazy model loading (TinyFaceDetector + Expression + Landmarks)")
print("  • 5-10 FPS detection (configurable, default 7 FPS)")
print("  • 7 expression detection: neutral, happy, sad, angry, fearful, disgusted, surprised")
print("  • Attention score from face presence and landmarks")
print("  • Event emission on expression changes")
print("  • Auto-start/stop based on enabled flag")
print("  • CPU-efficient with TinyFaceDetector")
print("  • Real-time expression tracking")
print("\n🎯 Ticket requirements:")
print("  ✓ Lazy model loading")
print("  ✓ 5-10 FPS detection")
print("  ✓ 7 expressions detected")
print("  ✓ Attention proxy from face + landmarks")
print("  ✓ Timestamped events")
print("  ✓ Low CPU usage (TinyFaceDetector)")

fer_hook_created = True
print(f"\n📄 Hook saved: {hook_path}")
