print("=" * 80)
print("ORATORIQ - WEBCAM RECORDER WITH FER INTEGRATION")
print("=" * 80)

import os

client_src = "oratoriq/client/src"
components_dir = os.path.join(client_src, "components")

# Create recorder directory
recorder_dir = os.path.join(components_dir, "recorder")
os.makedirs(recorder_dir, exist_ok=True)

# ============================================================================
# WebcamAudioRecorder Component with FER Integration
# ============================================================================
recorder_component = """import { useEffect, useRef, useState, useCallback } from 'react';
import { useAppStore } from '../../store';
import { useFaceAPI } from '../../hooks/useFaceAPI';
import { ExpressionBadges } from '../ExpressionBadges';
import { FaceDetectionResult, FacialEvent } from '../../../shared/types';

interface AudioChunk {
  blob: Blob;
  timestamp: number;
}

export const WebcamAudioRecorder = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const dataArrayRef = useRef<Uint8Array | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const audioChunksRef = useRef<AudioChunk[]>([]);
  
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [hasPermissions, setHasPermissions] = useState(false);
  const [permissionError, setPermissionError] = useState<string | null>(null);
  const [audioLevel, setAudioLevel] = useState(0);
  const [recordingTime, setRecordingTime] = useState(0);
  
  const { 
    session,
    startRecording: startSession, 
    stopRecording: stopSession,
    addFacialEvent,
    updateCurrentExpression 
  } = useAppStore();

  // Face detection callbacks
  const handleFaceDetection = useCallback((result: FaceDetectionResult) => {
    updateCurrentExpression(result);
  }, [updateCurrentExpression]);

  const handleFacialEvent = useCallback((event: FacialEvent) => {
    if (isRecording) {
      addFacialEvent(event);
      console.log(`🎭 Expression: ${event.eventType} (${Math.round(event.confidence * 100)}%)`);
    }
  }, [isRecording, addFacialEvent]);

  // FER Hook integration
  const {
    isModelsLoaded,
    isDetecting,
    currentExpression,
    error: ferError
  } = useFaceAPI({
    videoElement: videoRef.current,
    enabled: hasPermissions && isRecording,
    targetFPS: 7,
    onDetection: handleFaceDetection,
    onEvent: handleFacialEvent,
  });

  // Initialize getUserMedia for webcam and audio
  const initializeMedia = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720 },
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });

      mediaStreamRef.current = stream;

      // Set video preview
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      // Setup Web Audio API for audio level meter
      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      const source = audioContext.createMediaStreamSource(stream);
      
      analyser.fftSize = 256;
      source.connect(analyser);
      
      audioContextRef.current = audioContext;
      analyserRef.current = analyser;
      dataArrayRef.current = new Uint8Array(analyser.frequencyBinCount);

      setHasPermissions(true);
      setPermissionError(null);
      console.log('✓ Media permissions granted');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setPermissionError(`Failed to access camera/microphone: ${errorMessage}`);
      setHasPermissions(false);
      console.error('✗ Media permission error:', error);
    }
  }, []);

  // Draw waveform visualization
  const drawWaveform = useCallback(() => {
    if (!canvasRef.current || !analyserRef.current || !dataArrayRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const analyser = analyserRef.current;
    const dataArray = dataArrayRef.current;
    const bufferLength = dataArray.length;

    analyser.getByteTimeDomainData(dataArray);

    // Clear canvas with dark background
    ctx.fillStyle = '#1D1D20';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw waveform
    ctx.lineWidth = 2;
    ctx.strokeStyle = '#A1C9F4';
    ctx.beginPath();

    const sliceWidth = canvas.width / bufferLength;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
      const v = dataArray[i] / 128.0;
      const y = (v * canvas.height) / 2;

      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }

      x += sliceWidth;
    }

    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.stroke();

    // Calculate audio level for meter
    const sum = dataArray.reduce((acc, val) => acc + Math.abs(val - 128), 0);
    const avgLevel = sum / bufferLength;
    const normalizedLevel = Math.min((avgLevel / 128) * 100, 100);
    setAudioLevel(normalizedLevel);

    animationFrameRef.current = requestAnimationFrame(drawWaveform);
  }, []);

  // Start recording with MediaRecorder
  const startRecording = useCallback(() => {
    if (!mediaStreamRef.current) {
      console.error('No media stream available');
      return;
    }

    // Create MediaRecorder with webm/opus format
    const mediaRecorder = new MediaRecorder(mediaStreamRef.current, {
      mimeType: 'audio/webm;codecs=opus',
      audioBitsPerSecond: 128000
    });

    audioChunksRef.current = [];

    // Handle data available every 1-2 seconds
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        const chunk: AudioChunk = {
          blob: event.data,
          timestamp: Date.now()
        };
        audioChunksRef.current.push(chunk);
        console.log(`✓ Audio chunk recorded: ${(event.data.size / 1024).toFixed(2)} KB`);
      }
    };

    mediaRecorder.onstop = () => {
      console.log(`✓ Recording stopped. Total chunks: ${audioChunksRef.current.length}`);
    };

    // Start recording with 1.5 second intervals
    mediaRecorder.start(1500);
    mediaRecorderRef.current = mediaRecorder;

    setIsRecording(true);
    setIsPaused(false);
    setRecordingTime(0);
    
    // Start waveform visualization
    drawWaveform();

    // Update store
    startSession();

    console.log('✓ Recording started with FER enabled');
  }, [drawWaveform, startSession]);

  // Pause recording
  const pauseRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
      console.log('⏸ Recording paused');
    }
  }, []);

  // Resume recording
  const resumeRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'paused') {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
      console.log('▶ Recording resumed');
    }
  }, []);

  // Stop recording
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);
      
      // Stop waveform animation
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }

      // Update store
      stopSession();

      console.log('⏹ Recording stopped');
      console.log(`📊 FER events collected: ${session.facialEvents.length}`);
    }
  }, [stopSession, session.facialEvents.length]);

  // Recording timer
  useEffect(() => {
    let interval: number | null = null;
    
    if (isRecording && !isPaused) {
      interval = window.setInterval(() => {
        setRecordingTime(prev => prev + 1000);
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isRecording, isPaused]);

  // Initialize on mount
  useEffect(() => {
    initializeMedia();

    return () => {
      // Cleanup
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(track => track.stop());
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [initializeMedia]);

  const formatTime = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 space-y-4">
      <h2 className="text-2xl font-bold mb-4">Webcam & Audio Recorder with FER</h2>

      {/* Permission Error */}
      {permissionError && (
        <div className="bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-200 px-4 py-3 rounded">
          <p className="font-medium">Permission Error</p>
          <p className="text-sm">{permissionError}</p>
          <button
            onClick={initializeMedia}
            className="mt-2 px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      )}

      {/* FER Error */}
      {ferError && (
        <div className="bg-yellow-100 dark:bg-yellow-900 border border-yellow-400 text-yellow-700 dark:text-yellow-200 px-4 py-3 rounded">
          <p className="font-medium">FER Warning</p>
          <p className="text-sm">{ferError}</p>
        </div>
      )}

      {/* Video Preview with Expression Badges Overlay */}
      <div className="relative bg-black rounded-lg overflow-hidden" style={{ aspectRatio: '16/9' }}>
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-full object-cover"
        />
        
        {/* Expression Badges Overlay */}
        {isRecording && (
          <div className="absolute top-4 left-4 right-4">
            <ExpressionBadges detection={currentExpression} />
          </div>
        )}
        
        {/* FER Status Indicator */}
        {isRecording && (
          <div className="absolute top-4 right-4 flex items-center gap-2 bg-black bg-opacity-60 px-3 py-2 rounded-lg">
            {isDetecting ? (
              <>
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="text-white text-xs font-medium">FER Active</span>
              </>
            ) : (
              <>
                <div className="w-2 h-2 bg-yellow-500 rounded-full" />
                <span className="text-white text-xs font-medium">Loading models...</span>
              </>
            )}
          </div>
        )}
        
        {!hasPermissions && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75">
            <p className="text-white text-lg">Waiting for camera permissions...</p>
          </div>
        )}
      </div>

      {/* Waveform Visualization */}
      <div className="space-y-2">
        <h3 className="text-lg font-semibold">Audio Waveform</h3>
        <canvas
          ref={canvasRef}
          width={800}
          height={100}
          className="w-full bg-gray-900 rounded-lg"
        />
      </div>

      {/* Audio Level Meter */}
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-semibold">Audio Level</h3>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {audioLevel.toFixed(0)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 overflow-hidden">
          <div
            className="h-full transition-all duration-100 rounded-full"
            style={{
              width: `${audioLevel}%`,
              backgroundColor: audioLevel > 75 ? '#f04438' : audioLevel > 50 ? '#ffd400' : '#17b26a'
            }}
          />
        </div>
      </div>

      {/* Recording Controls */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <div className="text-sm text-gray-600 dark:text-gray-400">Recording Time</div>
          <div className="text-2xl font-mono font-bold">{formatTime(recordingTime)}</div>
          {isRecording && (
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${isPaused ? 'bg-yellow-500' : 'bg-red-500 animate-pulse'}`} />
              <span className="text-sm font-medium">{isPaused ? 'Paused' : 'Recording'}</span>
            </div>
          )}
        </div>

        <div className="flex gap-3">
          {!isRecording ? (
            <button
              onClick={startRecording}
              disabled={!hasPermissions}
              className="px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <circle cx="10" cy="10" r="8" />
              </svg>
              Start
            </button>
          ) : (
            <>
              {!isPaused ? (
                <button
                  onClick={pauseRecording}
                  className="px-6 py-3 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <rect x="5" y="4" width="4" height="12" />
                    <rect x="11" y="4" width="4" height="12" />
                  </svg>
                  Pause
                </button>
              ) : (
                <button
                  onClick={resumeRecording}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M6 4l10 6-10 6V4z" />
                  </svg>
                  Resume
                </button>
              )}
              <button
                onClick={stopRecording}
                className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <rect x="5" y="5" width="10" height="10" />
                </svg>
                Stop
              </button>
            </>
          )}
        </div>
      </div>

      {/* Recording Stats with FER Data */}
      {(audioChunksRef.current.length > 0 || session.facialEvents.length > 0) && (
        <div className="mt-4 p-4 bg-gray-100 dark:bg-gray-900 rounded-lg">
          <h4 className="font-semibold mb-2">Recording Stats</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600 dark:text-gray-400">Audio Chunks:</span>
              <span className="ml-2 font-medium">{audioChunksRef.current.length}</span>
            </div>
            <div>
              <span className="text-gray-600 dark:text-gray-400">Format:</span>
              <span className="ml-2 font-medium">webm/opus</span>
            </div>
            <div>
              <span className="text-gray-600 dark:text-gray-400">FER Events:</span>
              <span className="ml-2 font-medium">{session.facialEvents.length}</span>
            </div>
            <div>
              <span className="text-gray-600 dark:text-gray-400">FER Status:</span>
              <span className="ml-2 font-medium">
                {isModelsLoaded ? 'Ready' : 'Loading...'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
"""

recorder_path = os.path.join(recorder_dir, "WebcamAudioRecorder.tsx")
with open(recorder_path, 'w') as f:
    f.write(recorder_component)
print(f"✓ Created {recorder_path}")

print("\n" + "=" * 80)
print("WEBCAM RECORDER WITH FER INTEGRATION COMPLETE")
print("=" * 80)
print("\n✅ Features implemented:")
print("  • getUserMedia for webcam (1280x720) and audio access")
print("  • MediaRecorder with audio/webm;codecs=opus format")
print("  • Audio chunks recorded at 1.5 second intervals")
print("  • Web Audio API for real-time audio level meter")
print("  • Waveform visualization using Canvas API")
print("  • Start/Pause/Resume/Stop recording controls")
print("  • Video preview with live webcam feed")
print("  • Real-time audio level display with color coding")
print("  • Recording time tracker")
print("  • Graceful permission error handling")
print("  • Automatic cleanup on component unmount")
print("\n🎭 FER Integration:")
print("  • useFaceAPI hook integration at 7 FPS")
print("  • Real-time expression badges overlay on video")
print("  • Facial events stored in Zustand session store")
print("  • FER status indicator (active/loading)")
print("  • Expression change event tracking")
print("  • FER events count in recording stats")
print("\n✅ Ticket requirements fulfilled:")
print("  ✓ face-api.js integrated with lazy loading")
print("  ✓ 5-10 FPS detection (7 FPS)")
print("  ✓ 7 expressions detected (neutral, happy, sad, angry, fearful, disgusted, surprised)")
print("  ✓ Attention proxy from face presence and landmarks")
print("  ✓ FacialEvents with timestamps stored in session")
print("  ✓ Real-time expression badges overlay video")
print("  ✓ FER data collected in session store")
print("  ✓ CPU usage kept low with TinyFaceDetector")

webcam_recorder_fer_complete = True
print(f"\n📄 Component saved: {recorder_path}")
