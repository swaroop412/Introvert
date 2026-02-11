print("=" * 80)
print("ENHANCED FACEAPI HOOK - ERROR HANDLING & CLEANUP")
print("=" * 80)

import os

client_src = "oratoriq/client/src"
hooks_dir = os.path.join(client_src, "hooks")
os.makedirs(hooks_dir, exist_ok=True)

enhanced_faceapi_hook = """import { useEffect, useRef, useState, useCallback } from 'react';
import * as faceapi from 'face-api.js';
import { FaceDetectionResult, FacialEvent, FacialExpression, FacialEventType } from '../../../shared/types';
import { toast } from '../utils/toast';

interface UseFaceAPIOptions {
  videoElement: HTMLVideoElement | null;
  enabled: boolean;
  targetFPS?: number;
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

const MODEL_URL = '/models';

export const useFaceAPI = ({
  videoElement,
  enabled,
  targetFPS = 7,
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
  const cleanupCallbackRef = useRef<(() => void) | null>(null);
  const loadingRetryCount = useRef(0);
  const maxRetries = 3;

  // Cleanup function
  const cleanup = useCallback(() => {
    console.log('🧹 Cleaning up FER resources...');
    
    if (detectionIntervalRef.current) {
      clearInterval(detectionIntervalRef.current);
      detectionIntervalRef.current = null;
    }
    
    setIsDetecting(false);
    setCurrentExpression(null);
    previousExpressionRef.current = null;
    
    console.log('✓ FER cleanup complete');
  }, []);

  // Register cleanup
  useEffect(() => {
    cleanupCallbackRef.current = cleanup;
  }, [cleanup]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanupCallbackRef.current?.();
    };
  }, []);

  // Lazy load face-api.js models with retry logic
  useEffect(() => {
    const loadModels = async () => {
      if (modelsLoadedRef.current || !enabled) return;

      try {
        console.log('🔄 Loading face-api.js models...');
        
        await Promise.all([
          faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
          faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL),
          faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
        ]);

        modelsLoadedRef.current = true;
        setIsModelsLoaded(true);
        setError(null);
        loadingRetryCount.current = 0;
        console.log('✓ face-api.js models loaded successfully');
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error loading models';
        console.error('✗ Failed to load face-api.js models:', errorMessage);
        
        // Retry loading with exponential backoff
        if (loadingRetryCount.current < maxRetries) {
          loadingRetryCount.current++;
          const delay = 1000 * Math.pow(2, loadingRetryCount.current - 1);
          
          toast.warning(
            'FER Loading',
            `Retrying model loading (${loadingRetryCount.current}/${maxRetries})...`,
            3000
          );
          
          setTimeout(() => {
            modelsLoadedRef.current = false;
            loadModels();
          }, delay);
        } else {
          const userFriendlyError = errorMessage.includes('404') || errorMessage.includes('NetworkError')
            ? 'Failed to load FER models. Please check your internet connection and ensure model files are available.'
            : `Model loading failed: ${errorMessage}`;
          
          setError(userFriendlyError);
          toast.error(
            'FER Unavailable',
            'Facial expression recognition cannot be loaded. Recording will continue without FER.',
            0 // Don't auto-dismiss
          );
        }
      }
    };

    if (enabled) {
      loadModels();
    }
  }, [enabled]);

  // Calculate attention score from landmarks and face presence
  const calculateAttentionScore = useCallback((
    detected: boolean,
    landmarks?: faceapi.FaceLandmarks68
  ): number => {
    if (!detected) return 0;
    
    if (!landmarks) return 0.5;
    
    try {
      const leftEye = landmarks.getLeftEye();
      const rightEye = landmarks.getRightEye();
      const nose = landmarks.getNose();
      
      const eyesVisible = leftEye.length > 0 && rightEye.length > 0;
      const noseCentered = nose.length > 0;
      
      if (eyesVisible && noseCentered) {
        const leftEyeCenter = leftEye[0];
        const rightEyeCenter = rightEye[0];
        const eyeDistance = Math.abs(rightEyeCenter.x - leftEyeCenter.x);
        
        const attentionScore = Math.min(eyeDistance / 100, 1.0);
        return Math.max(0.6, attentionScore);
      }
      
      return 0.5;
    } catch (err) {
      console.warn('Error calculating attention score:', err);
      return 0.5;
    }
  }, []);

  // Determine dominant expression
  const getDominantExpression = useCallback((expressions: FacialExpression): FacialEventType => {
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
  }, []);

  // Perform face detection and expression recognition with error handling
  const detectFace = useCallback(async () => {
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

        if (previousExpressionRef.current !== null) {
          previousExpressionRef.current = null;
        }
      }
    } catch (err) {
      // Silent fail for individual detection errors to prevent flooding
      console.warn('Face detection error:', err);
    }
  }, [videoElement, onDetection, onEvent, calculateAttentionScore, getDominantExpression]);

  // Start detection loop
  const startDetection = useCallback(() => {
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
  }, [isModelsLoaded, videoElement, targetFPS, detectFace]);

  // Stop detection loop
  const stopDetection = useCallback(() => {
    cleanup();
  }, [cleanup]);

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
  }, [enabled, isModelsLoaded, videoElement, startDetection, stopDetection]);

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
    f.write(enhanced_faceapi_hook)
print(f"✓ Created {hook_path}")

print("\n" + "=" * 80)
print("ENHANCED FACEAPI HOOK COMPLETE")
print("=" * 80)
print("\n✅ Error Handling:")
print("  • Model loading retry with exponential backoff (3 attempts)")
print("  • User-friendly error messages for network/404 errors")
print("  • Silent fail for individual detection errors")
print("  • Toast notifications for loading failures")
print("  • Graceful cleanup on stop/unmount")
print("\n✅ Reliability:")
print("  • Prevents infinite retry loops")
print("  • Non-critical errors don't block recording")
print("  • Cleanup prevents memory leaks")
print("  • Proper state management")
print("\n✅ UX:")
print("  • Clear error messages")
print("  • Loading retry feedback")
print("  • Non-blocking FER failures")

enhanced_faceapi_complete = True
