"""
OratorIQ Speech Mode - Core Analysis Engine
Real-time speech metrics: WPM, filler words/min, pause detection
"""

import time
from collections import deque
import re

class SpeechAnalysisEngine:
    """Real-time speech analysis with live metrics tracking"""
    
    def __init__(self, target_wpm_min=120, target_wpm_max=160, wpm_window_s=10.0):
        # WPM tracking
        self.target_wpm_min = target_wpm_min
        self.target_wpm_max = target_wpm_max
        self.wpm_window_s = wpm_window_s
        self.word_timestamps = deque()
        
        # Filler word detection
        self.filler_words = {
            'um', 'uh', 'uhm', 'umm', 'er', 'ah', 'like', 
            'you know', 'i mean', 'sort of', 'kind of', 
            'basically', 'actually', 'literally', 'right',
            'so', 'well', 'okay', 'ok', 'yeah'
        }
        self.filler_events = []
        
        # Pause detection
        self.pause_threshold_ms = 500
        self.last_speech_time = None
        self.pause_events = []
        
        # Session tracking
        self.session_start = None
        self.total_words = 0
        self.total_fillers = 0
        
    def start_session(self):
        """Initialize a new speech session"""
        self.session_start = time.time()
        self.word_timestamps.clear()
        self.filler_events.clear()
        self.pause_events.clear()
        self.total_words = 0
        self.total_fillers = 0
        self.last_speech_time = self.session_start
        
    def process_transcript_segment(self, text, timestamp=None):
        """Process incoming transcript and extract metrics"""
        if timestamp is None:
            timestamp = time.time()
            
        if self.session_start is None:
            self.start_session()
        
        # Extract words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Track word timestamps for WPM
        for word in words:
            self.word_timestamps.append(timestamp)
            self.total_words += 1
            
            # Check for filler words
            if word in self.filler_words:
                self.filler_events.append({
                    'timestamp': timestamp,
                    'word': word,
                    'text': text
                })
                self.total_fillers += 1
        
        # Detect pause
        if self.last_speech_time is not None:
            pause_duration_ms = (timestamp - self.last_speech_time) * 1000
            if pause_duration_ms > self.pause_threshold_ms:
                self.pause_events.append({
                    'timestamp': self.last_speech_time,
                    'duration_ms': round(pause_duration_ms, 0),
                    'end_timestamp': timestamp
                })
        
        self.last_speech_time = timestamp
        
        return self.get_current_metrics()
    
    def get_current_metrics(self):
        """Get current real-time metrics"""
        now = time.time()
        
        # Calculate WPM (sliding window)
        cutoff_time = now - self.wpm_window_s
        while self.word_timestamps and self.word_timestamps[0] < cutoff_time:
            self.word_timestamps.popleft()
        
        recent_words = len(self.word_timestamps)
        window_duration_s = min(self.wpm_window_s, now - self.session_start if self.session_start else 0)
        
        if window_duration_s > 0:
            current_wpm = (recent_words / window_duration_s) * 60
        else:
            current_wpm = 0
        
        wpm_status = 'optimal'
        if current_wpm < self.target_wpm_min:
            wpm_status = 'too_slow'
        elif current_wpm > self.target_wpm_max:
            wpm_status = 'too_fast'
        
        # Calculate fillers per minute
        session_duration_min = (now - self.session_start) / 60 if self.session_start else 0
        fillers_per_min = self.total_fillers / session_duration_min if session_duration_min > 0 else 0
        
        # Count recent fillers (last 60s)
        recent_filler_cutoff = now - 60
        recent_fillers = sum(1 for f in self.filler_events if f['timestamp'] > recent_filler_cutoff)
        
        # Count recent pauses (last 60s)
        recent_pause_cutoff = now - 60
        recent_pauses = sum(1 for p in self.pause_events if p['timestamp'] > recent_pause_cutoff)
        
        return {
            'wpm': round(current_wpm, 1),
            'wpm_status': wpm_status,
            'wpm_target_range': f"{self.target_wpm_min}-{self.target_wpm_max}",
            'fillers_per_min': round(fillers_per_min, 2),
            'recent_fillers_60s': recent_fillers,
            'total_fillers': self.total_fillers,
            'recent_pauses_60s': recent_pauses,
            'total_pauses': len(self.pause_events),
            'total_words': self.total_words,
            'session_duration_s': round(now - self.session_start, 1) if self.session_start else 0
        }
    
    def get_key_moments(self):
        """Identify key moments in the session for timeline visualization"""
        moments = []
        
        # Peak filler moment (highest concentration in 30s window)
        if len(self.filler_events) >= 3:
            max_fillers = 0
            peak_time = None
            for i, event in enumerate(self.filler_events):
                window_start = event['timestamp']
                window_fillers = sum(1 for f in self.filler_events 
                                   if window_start <= f['timestamp'] <= window_start + 30)
                if window_fillers > max_fillers:
                    max_fillers = window_fillers
                    peak_time = event['timestamp']
            
            if peak_time:
                moments.append({
                    'type': 'peak_confusion',
                    'timestamp': peak_time,
                    'description': f"{max_fillers} filler words in 30s window",
                    'severity': 'high' if max_fillers >= 5 else 'medium'
                })
        
        # Longest pause
        if self.pause_events:
            longest_pause = max(self.pause_events, key=lambda p: p['duration_ms'])
            if longest_pause['duration_ms'] > 1000:  # Over 1 second
                moments.append({
                    'type': 'long_pause',
                    'timestamp': longest_pause['timestamp'],
                    'description': f"Pause: {longest_pause['duration_ms']:.0f}ms",
                    'severity': 'high' if longest_pause['duration_ms'] > 2000 else 'medium'
                })
        
        # Sort by timestamp
        moments.sort(key=lambda m: m['timestamp'])
        
        return moments


# Demo the engine
print("=" * 70)
print("SPEECH MODE - CORE ANALYSIS ENGINE")
print("=" * 70)

engine = SpeechAnalysisEngine()
engine.start_session()

# Simulate transcript segments
test_transcripts = [
    ("Hello everyone, welcome to my presentation", 0.0),
    ("Um, today I want to talk about", 3.5),
    ("The key metrics we need to focus on", 6.0),
    ("You know, like, the main thing is", 8.5),
    ("Actually, let me explain this better", 15.0),  # Long pause
    ("The data shows clear trends", 17.5),
    ("Um, uh, well, basically we should", 20.0),
    ("Focus on customer satisfaction", 23.0),
]

print("\n📊 PROCESSING SPEECH SEGMENTS")
print("-" * 70)

for text, relative_time in test_transcripts:
    timestamp = engine.session_start + relative_time
    metrics = engine.process_transcript_segment(text, timestamp)
    
    print(f"\n⏰ T+{relative_time}s: \"{text}\"")
    print(f"   WPM: {metrics['wpm']} ({metrics['wpm_status']})")
    print(f"   Fillers/min: {metrics['fillers_per_min']:.2f} | Recent: {metrics['recent_fillers_60s']}")
    print(f"   Pauses: {metrics['recent_pauses_60s']} recent | {metrics['total_pauses']} total")

# Get final metrics
print("\n" + "=" * 70)
print("FINAL SESSION METRICS")
print("=" * 70)

final_metrics = engine.get_current_metrics()
print(f"\n📈 Words Per Minute: {final_metrics['wpm']} ({final_metrics['wpm_status']})")
print(f"   Target Range: {final_metrics['wpm_target_range']}")
print(f"📊 Total Words: {final_metrics['total_words']}")
print(f"⚠️  Total Fillers: {final_metrics['total_fillers']} ({final_metrics['fillers_per_min']:.2f}/min)")
print(f"⏸️  Total Pauses: {final_metrics['total_pauses']}")
print(f"⏱️  Session Duration: {final_metrics['session_duration_s']}s")

# Get key moments
print("\n" + "=" * 70)
print("KEY MOMENTS TIMELINE")
print("=" * 70)

key_moments = engine.get_key_moments()
if key_moments:
    for moment in key_moments:
        relative_time = moment['timestamp'] - engine.session_start
        print(f"\n🔴 {moment['type'].upper()} (T+{relative_time:.1f}s)")
        print(f"   {moment['description']}")
        print(f"   Severity: {moment['severity']}")
else:
    print("\n✅ No significant moments detected")

print("\n" + "=" * 70)
print("✅ SPEECH ANALYSIS ENGINE READY")
print("=" * 70)

# Export for downstream blocks
speech_engine = engine
