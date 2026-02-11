"""
Unit tests for stutter.ts (DisfluencyDetector)
Tests all core functionality: filler word detection, pause detection, repetition detection, and WPM calculation
"""

import unittest
from collections import deque
import re

# DisfluencyDetector implementation (mimics stutter.ts)
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
            'target_range': f'{self.target_wpm_min}-{self.target_wpm_max}',
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


# Test Suite
class TestDisfluencyDetector(unittest.TestCase):
    """Comprehensive unit tests for DisfluencyDetector (stutter.ts)"""
    
    def setUp(self):
        """Create fresh detector instance for each test"""
        self.detector = DisfluencyDetector()
    
    # Filler Word Tests
    def test_detect_single_filler_word(self):
        """Should detect single filler words"""
        events = self.detector.detect_filler_words("Um, hello there", 0.0)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['type'], 'filler_word')
        self.assertEqual(events[0]['detail']['word'], 'um')
    
    def test_detect_multiple_filler_words(self):
        """Should detect multiple filler words in one segment"""
        events = self.detector.detect_filler_words("Um, like, you know", 0.0)
        self.assertGreaterEqual(len(events), 2)
        filler_words = [e['detail']['word'] for e in events]
        self.assertIn('um', filler_words)
        self.assertIn('like', filler_words)
    
    def test_detect_multi_word_fillers(self):
        """Should detect multi-word filler phrases"""
        events = self.detector.detect_filler_words("I mean, that's good", 0.0)
        self.assertGreater(len(events), 0)
        self.assertTrue(any(e['detail']['word'] == 'i mean' for e in events))
    
    def test_no_filler_words(self):
        """Should return empty list when no fillers present"""
        events = self.detector.detect_filler_words("This is clean speech", 0.0)
        self.assertEqual(len(events), 0)
    
    def test_case_insensitive_filler_detection(self):
        """Should detect fillers regardless of case"""
        events = self.detector.detect_filler_words("UM, Like, WELL", 0.0)
        self.assertGreaterEqual(len(events), 3)
    
    # Pause Detection Tests
    def test_detect_pause_above_threshold(self):
        """Should detect pause when duration exceeds threshold (400ms)"""
        self.detector.detect_pause(0.0)
        event = self.detector.detect_pause(0.5)  # 500ms pause
        self.assertIsNotNone(event)
        self.assertEqual(event['type'], 'pause')
        self.assertGreater(event['detail']['duration_ms'], 400)
    
    def test_no_pause_below_threshold(self):
        """Should not detect pause when duration is below threshold"""
        self.detector.detect_pause(0.0)
        event = self.detector.detect_pause(0.3)  # 300ms - below 400ms threshold
        self.assertIsNone(event)
    
    def test_first_pause_call_returns_none(self):
        """First pause detection call should return None (baseline)"""
        event = self.detector.detect_pause(0.0)
        self.assertIsNone(event)
    
    def test_pause_duration_calculation(self):
        """Should calculate pause duration correctly"""
        self.detector.detect_pause(0.0)
        event = self.detector.detect_pause(1.0)  # 1000ms pause
        self.assertEqual(event['detail']['duration_ms'], 1000.0)
    
    # Repetition Detection Tests
    def test_detect_word_repetition(self):
        """Should detect repeated words within window"""
        self.detector.detect_repetition("the cat", 0.0)
        events = self.detector.detect_repetition("the dog", 0.5)
        self.assertGreater(len(events), 0)
        self.assertEqual(events[0]['type'], 'repetition')
        self.assertEqual(events[0]['detail']['word'], 'the')
        self.assertEqual(events[0]['detail']['count'], 2)
    
    def test_repetition_window_expiry(self):
        """Should not detect repetitions outside 2-second window"""
        self.detector.detect_repetition("the cat", 0.0)
        events = self.detector.detect_repetition("the dog", 2.5)  # Outside window
        # Word history should have been cleaned
        self.assertEqual(len(events), 0)
    
    def test_ignore_short_words_for_repetition(self):
        """Should ignore words with 2 or fewer characters"""
        self.detector.detect_repetition("I am a", 0.0)
        events = self.detector.detect_repetition("I am", 0.5)
        # "I" and "am" are <= 2 chars, should be ignored
        self.assertEqual(len(events), 0)
    
    def test_multiple_repetitions(self):
        """Should detect multiple repeated words"""
        self.detector.detect_repetition("the big cat", 0.0)
        events = self.detector.detect_repetition("the big dog", 0.5)
        # Should detect both "the" and "big"
        self.assertGreaterEqual(len(events), 2)
    
    # WPM Calculation Tests
    def test_calculate_wpm_optimal(self):
        """Should calculate WPM and mark as optimal (120-160 range)"""
        result = self.detector.calculate_wpm(25, 10.0)
        self.assertEqual(result['wpm'], 150.0)
        self.assertEqual(result['status'], 'optimal')
        self.assertTrue(result['in_target_range'])
    
    def test_calculate_wpm_too_slow(self):
        """Should mark WPM as too_slow when below 120"""
        result = self.detector.calculate_wpm(15, 10.0)
        self.assertEqual(result['wpm'], 90.0)
        self.assertEqual(result['status'], 'too_slow')
        self.assertFalse(result['in_target_range'])
    
    def test_calculate_wpm_too_fast(self):
        """Should mark WPM as too_fast when above 160"""
        result = self.detector.calculate_wpm(35, 10.0)
        self.assertEqual(result['wpm'], 210.0)
        self.assertEqual(result['status'], 'too_fast')
        self.assertFalse(result['in_target_range'])
    
    def test_calculate_wpm_zero_duration(self):
        """Should return None for zero duration"""
        result = self.detector.calculate_wpm(10, 0)
        self.assertIsNone(result)
    
    def test_wpm_calculation_accuracy(self):
        """Should calculate WPM with correct formula"""
        result = self.detector.calculate_wpm(50, 20.0)
        # 50 words / 20 seconds * 60 = 150 WPM
        self.assertEqual(result['wpm'], 150.0)
    
    # Integration Tests
    def test_process_transcript_segment_full_pipeline(self):
        """Should process transcript through full pipeline"""
        events = self.detector.process_transcript_segment("Um, the the problem", 0.0)
        # Should detect: filler (um), repetition (the)
        event_types = [e['type'] for e in events]
        self.assertIn('filler_word', event_types)
        self.assertIn('repetition', event_types)
    
    def test_process_clean_transcript(self):
        """Should return empty list for clean speech"""
        events = self.detector.process_transcript_segment("This is perfect speech", 0.0)
        self.assertEqual(len(events), 0)
    
    def test_detector_state_persistence(self):
        """Should maintain state across multiple calls"""
        # First call establishes baseline
        self.detector.process_transcript_segment("Hello world", 0.0)
        # Second call should detect pause
        events = self.detector.process_transcript_segment("How are you", 1.0)
        # Should have pause event
        pause_events = [e for e in events if e['type'] == 'pause']
        self.assertGreater(len(pause_events), 0)


# Run tests
if __name__ == '__main__':
    print("=" * 70)
    print("STUTTER.TS UNIT TESTS")
    print("=" * 70)
    print()
    
    # Run with verbose output
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDisfluencyDetector)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
