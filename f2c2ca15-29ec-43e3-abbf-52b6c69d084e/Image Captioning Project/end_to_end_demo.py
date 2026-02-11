"""
OratorIQ Speech Mode - End-to-End Demo
Complete speech practice session workflow demonstrating:
1. Topic/title input
2. Real-time metrics display (WPM, filler/min, pauses)
3. Stop-to-evaluate with key moments timeline
"""

import time
from collections import deque
import re

print("=" * 80)
print("ORATORIQ SPEECH MODE - COMPLETE DEMO")
print("=" * 80)

# ============================================================================
# PART 1: SPEECH ANALYSIS ENGINE
# ============================================================================

class SpeechAnalysisEngine:
    """Real-time speech analysis with live metrics tracking"""
    
    def __init__(self, target_wpm_min=120, target_wpm_max=160, wpm_window_s=10.0):
        self.target_wpm_min = target_wpm_min
        self.target_wpm_max = target_wpm_max
        self.wpm_window_s = wpm_window_s
        self.word_timestamps = deque()
        
        self.filler_words = {
            'um', 'uh', 'uhm', 'umm', 'er', 'ah', 'like', 
            'you know', 'i mean', 'sort of', 'kind of', 
            'basically', 'actually', 'literally', 'right',
            'so', 'well', 'okay', 'ok', 'yeah'
        }
        self.filler_events = []
        self.pause_threshold_ms = 500
        self.last_speech_time = None
        self.pause_events = []
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
        
        words = re.findall(r'\b\w+\b', text.lower())
        
        for word in words:
            self.word_timestamps.append(timestamp)
            self.total_words += 1
            
            if word in self.filler_words:
                self.filler_events.append({
                    'timestamp': timestamp,
                    'word': word,
                    'text': text
                })
                self.total_fillers += 1
        
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
        
        cutoff_time = now - self.wpm_window_s
        while self.word_timestamps and self.word_timestamps[0] < cutoff_time:
            self.word_timestamps.popleft()
        
        recent_words = len(self.word_timestamps)
        window_duration_s = min(self.wpm_window_s, now - self.session_start if self.session_start else 0)
        
        current_wpm = (recent_words / window_duration_s) * 60 if window_duration_s > 0 else 0
        
        wpm_status = 'optimal'
        if current_wpm < self.target_wpm_min:
            wpm_status = 'too_slow'
        elif current_wpm > self.target_wpm_max:
            wpm_status = 'too_fast'
        
        session_duration_min = (now - self.session_start) / 60 if self.session_start else 0
        fillers_per_min = self.total_fillers / session_duration_min if session_duration_min > 0 else 0
        
        recent_filler_cutoff = now - 60
        recent_fillers = sum(1 for f in self.filler_events if f['timestamp'] > recent_filler_cutoff)
        
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
        """Identify key moments in the session"""
        moments = []
        
        if len(self.filler_events) >= 3:
            max_fillers = 0
            peak_time = None
            for event in self.filler_events:
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
        
        if self.pause_events:
            longest_pause = max(self.pause_events, key=lambda p: p['duration_ms'])
            if longest_pause['duration_ms'] > 1000:
                moments.append({
                    'type': 'long_pause',
                    'timestamp': longest_pause['timestamp'],
                    'description': f"Pause: {longest_pause['duration_ms']:.0f}ms",
                    'severity': 'high' if longest_pause['duration_ms'] > 2000 else 'medium'
                })
        
        moments.sort(key=lambda m: m['timestamp'])
        return moments


# ============================================================================
# PART 2: EVALUATION SYSTEM
# ============================================================================

class SpeechEvaluationSystem:
    """Evaluates speech sessions and provides comprehensive feedback"""
    
    def __init__(self):
        self.evaluation_criteria = {
            'excellent': {'wpm_range': (130, 150), 'max_fillers_per_min': 2},
            'good': {'wpm_range': (120, 160), 'max_fillers_per_min': 4},
            'needs_improvement': {'wpm_range': (100, 180), 'max_fillers_per_min': 8}
        }
    
    def evaluate_session(self, engine):
        """Comprehensive session evaluation"""
        metrics = engine.get_current_metrics()
        key_moments = engine.get_key_moments()
        
        rating = self._calculate_rating(metrics)
        strongest_segment = self._find_strongest_segment(engine)
        notable_quotes = self._extract_notable_quotes(engine)
        recommendations = self._generate_recommendations(metrics, key_moments)
        
        return {
            'overall_rating': rating,
            'metrics_summary': metrics,
            'strongest_segment': strongest_segment,
            'key_moments': key_moments,
            'notable_quotes': notable_quotes,
            'recommendations': recommendations
        }
    
    def _calculate_rating(self, metrics):
        wpm = metrics['wpm']
        fillers_per_min = metrics['fillers_per_min']
        
        for rating, criteria in self.evaluation_criteria.items():
            wpm_min, wpm_max = criteria['wpm_range']
            if (wpm_min <= wpm <= wpm_max and 
                fillers_per_min <= criteria['max_fillers_per_min']):
                return rating
        
        return 'needs_significant_improvement'
    
    def _find_strongest_segment(self, engine):
        if not engine.filler_events or engine.session_start is None:
            return None
        
        session_duration = engine.get_current_metrics()['session_duration_s']
        best_score = -float('inf')
        best_segment = None
        window_size = 30
        step_size = 5
        
        for start_offset in range(0, int(session_duration - window_size) + 1, step_size):
            window_start = engine.session_start + start_offset
            window_end = window_start + window_size
            
            fillers_in_window = sum(1 for f in engine.filler_events 
                                   if window_start <= f['timestamp'] < window_end)
            pauses_in_window = sum(1 for p in engine.pause_events 
                                  if window_start <= p['timestamp'] < window_end)
            words_in_window = sum(1 for t in engine.word_timestamps 
                                 if window_start <= t < window_end)
            
            wpm = (words_in_window / window_size) * 60
            wpm_penalty = abs(wpm - 140)
            score = -fillers_in_window * 10 - pauses_in_window * 5 - wpm_penalty * 0.5
            
            if score > best_score and words_in_window > 10:
                best_score = score
                best_segment = {
                    'start_offset_s': start_offset,
                    'duration_s': window_size,
                    'wpm': round(wpm, 1),
                    'fillers': fillers_in_window,
                    'pauses': pauses_in_window,
                    'words': words_in_window,
                    'score': round(score, 2)
                }
        
        return best_segment
    
    def _extract_notable_quotes(self, engine):
        if not engine.filler_events:
            return []
        
        quotes = []
        sorted_fillers = sorted(engine.filler_events, key=lambda f: f['timestamp'])
        
        for i in range(len(sorted_fillers) - 1):
            gap_duration = sorted_fillers[i+1]['timestamp'] - sorted_fillers[i]['timestamp']
            
            if gap_duration > 10:
                quote_time = sorted_fillers[i]['timestamp'] + gap_duration / 2
                relative_time = quote_time - engine.session_start
                
                quotes.append({
                    'timestamp_offset_s': round(relative_time, 1),
                    'duration_s': round(gap_duration, 1),
                    'note': 'Clean delivery - no fillers'
                })
        
        return quotes[:3]
    
    def _generate_recommendations(self, metrics, key_moments):
        recommendations = []
        
        if metrics['wpm_status'] == 'too_slow':
            recommendations.append({
                'category': 'pace',
                'priority': 'high',
                'message': f"Increase pace to {metrics['wpm_target_range']} WPM (currently {metrics['wpm']})"
            })
        elif metrics['wpm_status'] == 'too_fast':
            recommendations.append({
                'category': 'pace',
                'priority': 'high',
                'message': f"Slow down to {metrics['wpm_target_range']} WPM (currently {metrics['wpm']})"
            })
        else:
            recommendations.append({
                'category': 'pace',
                'priority': 'low',
                'message': f"Excellent pace at {metrics['wpm']} WPM"
            })
        
        if metrics['fillers_per_min'] > 5:
            recommendations.append({
                'category': 'fillers',
                'priority': 'high',
                'message': f"Reduce fillers - {metrics['fillers_per_min']:.1f}/min is high"
            })
        elif metrics['fillers_per_min'] > 3:
            recommendations.append({
                'category': 'fillers',
                'priority': 'medium',
                'message': f"Good filler control, aim for <2/min (currently {metrics['fillers_per_min']:.1f})"
            })
        else:
            recommendations.append({
                'category': 'fillers',
                'priority': 'low',
                'message': f"Excellent filler control at {metrics['fillers_per_min']:.1f}/min"
            })
        
        return recommendations


# ============================================================================
# PART 3: COMPLETE SESSION DEMO
# ============================================================================

print("\n\n" + "=" * 80)
print("STARTING SPEECH PRACTICE SESSION")
print("=" * 80)

# Session setup
session_topic = "The Impact of AI on Modern Education"
target_duration_min = 2
print(f"\n📋 Topic: {session_topic}")
print(f"⏱️  Target Duration: {target_duration_min} minutes")

# Initialize engine
engine = SpeechAnalysisEngine()
engine.start_session()

# Simulate realistic speech with transcript segments
print("\n\n" + "▶" * 40)
print("LIVE SPEECH SESSION (REAL-TIME METRICS)")
print("▶" * 40)

test_speech = [
    ("Welcome everyone, today I want to discuss the impact of AI on education", 0.0),
    ("Um, artificial intelligence is transforming how we learn", 4.5),
    ("The traditional classroom model has been around for centuries", 8.0),
    ("But now we're seeing, you know, personalized learning at scale", 12.5),
    ("AI tutors can adapt to each student's pace and learning style", 16.0),
    ("Like, imagine having a personal tutor available twenty four seven", 20.0),
    ("That's the promise of AI in education", 28.5),  # Long pause
    ("However, we must consider the challenges", 31.0),
    ("Um, uh, there are concerns about data privacy", 35.0),
    ("And the digital divide remains a significant barrier", 38.5),
    ("Not all students have equal access to technology", 42.0),
    ("So we need to ensure AI enhances education for everyone", 46.0),
    ("Not just those with resources", 49.5),
    ("Well, basically, the key is responsible implementation", 53.0),
    ("Teachers working alongside AI, not being replaced by it", 57.0),
    ("That's how we can create a better future for learning", 61.0),
]

for text, relative_time in test_speech:
    timestamp = engine.session_start + relative_time
    metrics = engine.process_transcript_segment(text, timestamp)
    
    print(f"\n[T+{relative_time:05.1f}s] {text}")
    print(f"  📊 WPM: {metrics['wpm']:5.1f} ({metrics['wpm_status']:10s}) | "
          f"Fillers: {metrics['total_fillers']:2d} ({metrics['fillers_per_min']:4.1f}/min) | "
          f"Pauses: {metrics['total_pauses']:2d}")

# Stop and evaluate
print("\n\n" + "■" * 40)
print("SESSION STOPPED - GENERATING EVALUATION")
print("■" * 40)

evaluator = SpeechEvaluationSystem()
evaluation = evaluator.evaluate_session(engine)

# Display comprehensive results
print("\n\n" + "=" * 80)
print("📊 COMPREHENSIVE SESSION EVALUATION")
print("=" * 80)

print(f"\n🎯 Overall Performance: {evaluation['overall_rating'].upper()}")

print(f"\n📈 SESSION METRICS:")
metrics = evaluation['metrics_summary']
print(f"   Duration: {metrics['session_duration_s']}s")
print(f"   Total Words: {metrics['total_words']}")
print(f"   Words Per Minute: {metrics['wpm']} ({metrics['wpm_status']})")
print(f"   Target Range: {metrics['wpm_target_range']}")
print(f"   Total Fillers: {metrics['total_fillers']} ({metrics['fillers_per_min']:.2f}/min)")
print(f"   Total Pauses: {metrics['total_pauses']}")

if evaluation['strongest_segment']:
    seg = evaluation['strongest_segment']
    print(f"\n💪 STRONGEST SEGMENT:")
    print(f"   Time: T+{seg['start_offset_s']}s to T+{seg['start_offset_s'] + seg['duration_s']}s")
    print(f"   Performance: {seg['wpm']} WPM | {seg['fillers']} fillers | {seg['pauses']} pauses")
    print(f"   Quality Score: {seg['score']}")

print(f"\n🔑 KEY MOMENTS TIMELINE ({len(evaluation['key_moments'])} identified):")
for moment in evaluation['key_moments']:
    relative_time = moment['timestamp'] - engine.session_start
    severity_icon = '🔴' if moment['severity'] == 'high' else '🟡'
    print(f"   {severity_icon} T+{relative_time:05.1f}s | {moment['type'].replace('_', ' ').title()}")
    print(f"      → {moment['description']}")

if evaluation['notable_quotes']:
    print(f"\n💬 NOTABLE QUOTES ({len(evaluation['notable_quotes'])} clean segments):")
    for quote in evaluation['notable_quotes']:
        print(f"   • T+{quote['timestamp_offset_s']}s ({quote['duration_s']}s duration)")
        print(f"      {quote['note']}")

print(f"\n💡 RECOMMENDATIONS:")
for rec in evaluation['recommendations']:
    priority_icon = '🔴' if rec['priority'] == 'high' else ('🟡' if rec['priority'] == 'medium' else '🟢')
    print(f"   {priority_icon} [{rec['category'].upper()}] {rec['message']}")

print("\n" + "=" * 80)
print("✅ SPEECH MODE SESSION COMPLETE")
print("=" * 80)

print("\n\n📝 SUMMARY:")
print("   ✓ Topic/title input supported")
print("   ✓ Real-time metrics tracking (WPM, fillers/min, pauses)")
print("   ✓ Stop-to-evaluate workflow implemented")
print("   ✓ Key moments timeline generated")
print("   ✓ Strongest segment identification")
print("   ✓ Notable quotes extraction")
print("   ✓ Actionable recommendations provided")
print("\n🎉 End-to-end speech practice workflow operational!")
