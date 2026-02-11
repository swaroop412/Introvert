import re
from collections import deque

# Disfluency Detector Class
class DisfluencyDetector:
    def __init__(self):
        self.filler_words = {
            'um', 'uh', 'uhm', 'umm', 'er', 'ah', 'like', 
            'you know', 'i mean', 'sort of', 'kind of', 
            'basically', 'actually', 'literally', 'right',
            'so', 'well', 'okay', 'ok'
        }
        self.pause_threshold_ms = 400
        self.repetition_window_s = 2.0
        self.target_wpm_min = 120
        self.target_wpm_max = 160
        self.word_history = deque()
        self.last_word_time = None
        
    def detect_filler_words(self, text, timestamp):
        events = []
        text_lower = text.lower().strip()
        words = text_lower.split()
        
        for word in words:
            word_clean = re.sub(r'[^\w\s]', '', word)
            if word_clean in self.filler_words:
                events.append({
                    'type': 'filler_word',
                    'timestamp': timestamp,
                    'detail': {'word': word_clean, 'text': text}
                })
        
        for filler in self.filler_words:
            if ' ' in filler and filler in text_lower:
                events.append({
                    'type': 'filler_word',
                    'timestamp': timestamp,
                    'detail': {'word': filler, 'text': text}
                })
        
        return events
    
    def detect_pause(self, current_timestamp):
        if self.last_word_time is None:
            self.last_word_time = current_timestamp
            return None
        
        pause_duration_ms = (current_timestamp - self.last_word_time) * 1000
        
        if pause_duration_ms > self.pause_threshold_ms:
            event = {
                'type': 'pause',
                'timestamp': self.last_word_time,
                'detail': {
                    'duration_ms': round(pause_duration_ms, 1),
                    'end_timestamp': current_timestamp
                }
            }
            self.last_word_time = current_timestamp
            return event
        
        self.last_word_time = current_timestamp
        return None
    
    def detect_repetition(self, text, timestamp):
        events = []
        words = re.findall(r'\b\w+\b', text.lower())
        
        for word in words:
            self.word_history.append((word, timestamp))
        
        cutoff_time = timestamp - self.repetition_window_s
        while self.word_history and self.word_history[0][1] < cutoff_time:
            self.word_history.popleft()
        
        word_counts = {}
        for word, ts in self.word_history:
            if len(word) > 2:
                word_counts[word] = word_counts.get(word, 0) + 1
        
        for word, count in word_counts.items():
            if count >= 2:
                events.append({
                    'type': 'repetition',
                    'timestamp': timestamp,
                    'detail': {
                        'word': word,
                        'count': count,
                        'window_s': self.repetition_window_s
                    }
                })
        
        return events
    
    def calculate_wpm(self, word_count, duration_s):
        if duration_s == 0:
            return None
        
        wpm = (word_count / duration_s) * 60
        is_in_range = self.target_wpm_min <= wpm <= self.target_wpm_max
        status = 'optimal' if is_in_range else ('too_slow' if wpm < self.target_wpm_min else 'too_fast')
        
        return {
            'wpm': round(wpm, 1),
            'word_count': word_count,
            'duration_s': round(duration_s, 1),
            'target_range': str(self.target_wpm_min) + '-' + str(self.target_wpm_max),
            'status': status,
            'in_target_range': is_in_range
        }
    
    def process_transcript_segment(self, text, timestamp):
        disfluency_events = []
        disfluency_events.extend(self.detect_filler_words(text, timestamp))
        
        pause_event = self.detect_pause(timestamp)
        if pause_event:
            disfluency_events.append(pause_event)
        
        disfluency_events.extend(self.detect_repetition(text, timestamp))
        return disfluency_events


# Test the algorithm
print("=" * 60)
print("DISFLUENCY DETECTION ALGORITHM TEST")
print("=" * 60)

detector = DisfluencyDetector()

test_segments = [
    ("Um, I think that's a good idea", 0.0),
    ("Let me see", 1.5),
    ("You know, like, the main point is", 2.0),
    ("The the problem is", 3.2),
    ("Well, I mean, basically we need to", 4.5),
    ("Focus on the the key metrics", 5.0),
]

print("\nProcessing Test Transcript Segments:")
print("-" * 60)

all_events = []
for text, timestamp in test_segments:
    events = detector.process_transcript_segment(text, timestamp)
    all_events.extend(events)
    print("\nTime=" + str(timestamp) + "s: \"" + text + "\"")
    if events:
        for event in events:
            print("  WARNING " + event['type'].upper() + ": " + str(event['detail']))
    else:
        print("  OK No disfluencies detected")

print("\n" + "=" * 60)
print("SUMMARY: " + str(len(all_events)) + " disfluency events detected")
print("=" * 60)

# Test WPM
print("\nWPM Calculation Examples:")
print("-" * 60)

wpm_tests = [(100, 10), (25, 10), (30, 10)]

for word_count, duration in wpm_tests:
    wpm_metrics = detector.calculate_wpm(word_count, duration)
    print("\n" + str(word_count) + " words in " + str(duration) + "s:")
    print("  WPM: " + str(wpm_metrics['wpm']))
    print("  Status: " + wpm_metrics['status'].upper())
    print("  Target Range: " + wpm_metrics['target_range'])

print("\n" + "=" * 60)
print("Algorithm Implementation Complete")
print("=" * 60)

disfluency_detector = detector
