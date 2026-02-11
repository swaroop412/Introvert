"""
Unit tests for timeline.ts (UnifiedTimeline)
Tests timeline event management, align() query utility, and session export functionality
"""

import unittest
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

# UnifiedTimeline implementation (mimics timeline.ts)
@dataclass
class TimelineEvent:
    """Base timeline event with session-relative timestamp"""
    timestamp_ms: int
    event_type: str
    data: Dict[str, Any]

class UnifiedTimeline:
    """Unified timeline system for OratorIQ session data"""
    
    def __init__(self, session_start_time: Optional[int] = None):
        self.session_start_time = session_start_time
        self.events: List[TimelineEvent] = []
        self._sorted = True
        
    def _to_relative_ms(self, timestamp: int) -> int:
        """Convert absolute timestamp to session-relative milliseconds"""
        if self.session_start_time is None:
            self.session_start_time = timestamp
            return 0
        return timestamp - self.session_start_time
    
    def add_expression_event(self, timestamp: int, expression: str, 
                           confidence: float, all_expressions: Dict[str, float],
                           attention_score: float):
        """Add facial expression event"""
        event = TimelineEvent(
            timestamp_ms=self._to_relative_ms(timestamp),
            event_type='expression',
            data={
                'expression': expression,
                'confidence': confidence,
                'all_expressions': all_expressions,
                'attention_score': attention_score
            }
        )
        self.events.append(event)
        self._sorted = False
    
    def add_transcript_event(self, timestamp: int, text: str, is_final: bool = False):
        """Add transcript segment"""
        event = TimelineEvent(
            timestamp_ms=self._to_relative_ms(timestamp),
            event_type='transcript',
            data={'text': text, 'is_final': is_final}
        )
        self.events.append(event)
        self._sorted = False
    
    def add_filler_event(self, timestamp: int, word: str, text: str):
        """Add filler word detection"""
        event = TimelineEvent(
            timestamp_ms=self._to_relative_ms(timestamp),
            event_type='filler',
            data={'word': word, 'text': text}
        )
        self.events.append(event)
        self._sorted = False
    
    def add_pause_event(self, timestamp_start: int, timestamp_end: int, duration_ms: float):
        """Add pause detection"""
        event = TimelineEvent(
            timestamp_ms=self._to_relative_ms(timestamp_start),
            event_type='pause',
            data={
                'duration_ms': duration_ms,
                'end_ms': self._to_relative_ms(timestamp_end)
            }
        )
        self.events.append(event)
        self._sorted = False
    
    def add_wpm_event(self, timestamp: int, wpm: float, word_count: int,
                     duration_s: float, status: str):
        """Add WPM calculation"""
        event = TimelineEvent(
            timestamp_ms=self._to_relative_ms(timestamp),
            event_type='wpm',
            data={
                'wpm': wpm,
                'word_count': word_count,
                'duration_s': duration_s,
                'status': status
            }
        )
        self.events.append(event)
        self._sorted = False
    
    def _ensure_sorted(self):
        """Ensure events are sorted by timestamp"""
        if not self._sorted:
            self.events.sort(key=lambda e: e.timestamp_ms)
            self._sorted = True
    
    def align(self, t_start_ms: int, t_end_ms: int) -> Dict[str, Any]:
        """Query aligned data for a time slice"""
        self._ensure_sorted()
        
        slice_events = [e for e in self.events 
                       if t_start_ms <= e.timestamp_ms <= t_end_ms]
        
        result = {
            'time_slice': {'start_ms': t_start_ms, 'end_ms': t_end_ms, 
                          'duration_ms': t_end_ms - t_start_ms},
            'dominant_expression': None,
            'wpm_avg': None,
            'fillers': [],
            'pauses': [],
            'transcripts': [],
            'expression_distribution': defaultdict(int),
            'attention_avg': None,
            'total_events': len(slice_events)
        }
        
        expression_scores = defaultdict(list)
        attention_scores = []
        wpm_values = []
        
        for event in slice_events:
            if event.event_type == 'expression':
                expr = event.data['expression']
                confidence = event.data['confidence']
                result['expression_distribution'][expr] += 1
                expression_scores[expr].append(confidence)
                attention_scores.append(event.data['attention_score'])
                
            elif event.event_type == 'wpm':
                wpm_values.append(event.data['wpm'])
                
            elif event.event_type == 'filler':
                result['fillers'].append({
                    'timestamp_ms': event.timestamp_ms,
                    'word': event.data['word'],
                    'text': event.data['text']
                })
                
            elif event.event_type == 'pause':
                result['pauses'].append({
                    'timestamp_ms': event.timestamp_ms,
                    'duration_ms': event.data['duration_ms'],
                    'end_ms': event.data['end_ms']
                })
                
            elif event.event_type == 'transcript':
                result['transcripts'].append({
                    'timestamp_ms': event.timestamp_ms,
                    'text': event.data['text'],
                    'is_final': event.data['is_final']
                })
        
        if expression_scores:
            dominant = max(result['expression_distribution'].items(), 
                         key=lambda x: x[1])[0]
            result['dominant_expression'] = {
                'expression': dominant,
                'count': result['expression_distribution'][dominant],
                'avg_confidence': sum(expression_scores[dominant]) / len(expression_scores[dominant])
            }
        
        if wpm_values:
            result['wpm_avg'] = sum(wpm_values) / len(wpm_values)
        
        if attention_scores:
            result['attention_avg'] = sum(attention_scores) / len(attention_scores)
        
        result['expression_distribution'] = dict(result['expression_distribution'])
        
        return result
    
    def get_all_events(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all events, optionally filtered by type"""
        self._ensure_sorted()
        
        if event_type:
            filtered = [e for e in self.events if e.event_type == event_type]
        else:
            filtered = self.events
        
        return [{'timestamp_ms': e.timestamp_ms, 
                 'event_type': e.event_type, 
                 'data': e.data} for e in filtered]
    
    def export_session(self) -> Dict[str, Any]:
        """Export complete session data as JSON-serializable dict"""
        self._ensure_sorted()
        
        duration_ms = max([e.timestamp_ms for e in self.events]) if self.events else 0
        
        event_counts = defaultdict(int)
        for event in self.events:
            event_counts[event.event_type] += 1
        
        return {
            'session_metadata': {
                'session_start_time': self.session_start_time,
                'duration_ms': duration_ms,
                'total_events': len(self.events),
                'event_counts': dict(event_counts)
            },
            'events': [
                {
                    'timestamp_ms': e.timestamp_ms,
                    'event_type': e.event_type,
                    'data': e.data
                }
                for e in self.events
            ]
        }


# Test Suite
class TestUnifiedTimeline(unittest.TestCase):
    """Comprehensive unit tests for UnifiedTimeline (timeline.ts)"""
    
    def setUp(self):
        """Create fresh timeline instance for each test"""
        self.timeline = UnifiedTimeline()
        self.base_time = 1700000000000  # Example absolute timestamp
    
    # Initialization Tests
    def test_init_with_start_time(self):
        """Should initialize with provided session start time"""
        timeline = UnifiedTimeline(session_start_time=1000)
        self.assertEqual(timeline.session_start_time, 1000)
    
    def test_init_without_start_time(self):
        """Should initialize with None start time"""
        timeline = UnifiedTimeline()
        self.assertIsNone(timeline.session_start_time)
    
    def test_first_event_sets_baseline(self):
        """First event should set session_start_time if None"""
        self.timeline.add_transcript_event(1000, "Hello", True)
        self.assertEqual(self.timeline.session_start_time, 1000)
        self.assertEqual(self.timeline.events[0].timestamp_ms, 0)
    
    # Relative Timestamp Conversion Tests
    def test_relative_timestamp_conversion(self):
        """Should convert absolute timestamps to relative ms"""
        self.timeline.add_transcript_event(self.base_time, "First", True)
        self.timeline.add_transcript_event(self.base_time + 1000, "Second", True)
        
        self.assertEqual(self.timeline.events[0].timestamp_ms, 0)
        self.assertEqual(self.timeline.events[1].timestamp_ms, 1000)
    
    # Event Addition Tests
    def test_add_expression_event(self):
        """Should add expression event correctly"""
        self.timeline.add_expression_event(
            self.base_time, 'happy', 0.85,
            {'happy': 0.85, 'neutral': 0.15},
            0.92
        )
        self.assertEqual(len(self.timeline.events), 1)
        self.assertEqual(self.timeline.events[0].event_type, 'expression')
        self.assertEqual(self.timeline.events[0].data['expression'], 'happy')
    
    def test_add_transcript_event(self):
        """Should add transcript event correctly"""
        self.timeline.add_transcript_event(self.base_time, "Hello world", True)
        self.assertEqual(len(self.timeline.events), 1)
        self.assertEqual(self.timeline.events[0].event_type, 'transcript')
        self.assertEqual(self.timeline.events[0].data['text'], "Hello world")
        self.assertTrue(self.timeline.events[0].data['is_final'])
    
    def test_add_filler_event(self):
        """Should add filler event correctly"""
        self.timeline.add_filler_event(self.base_time, "um", "Um, hello")
        self.assertEqual(len(self.timeline.events), 1)
        self.assertEqual(self.timeline.events[0].event_type, 'filler')
        self.assertEqual(self.timeline.events[0].data['word'], "um")
    
    def test_add_pause_event(self):
        """Should add pause event correctly"""
        self.timeline.add_pause_event(self.base_time, self.base_time + 500, 500.0)
        self.assertEqual(len(self.timeline.events), 1)
        self.assertEqual(self.timeline.events[0].event_type, 'pause')
        self.assertEqual(self.timeline.events[0].data['duration_ms'], 500.0)
    
    def test_add_wpm_event(self):
        """Should add WPM event correctly"""
        self.timeline.add_wpm_event(self.base_time, 150.0, 25, 10.0, 'optimal')
        self.assertEqual(len(self.timeline.events), 1)
        self.assertEqual(self.timeline.events[0].event_type, 'wpm')
        self.assertEqual(self.timeline.events[0].data['wpm'], 150.0)
    
    # Event Sorting Tests
    def test_events_auto_sort(self):
        """Should automatically sort events by timestamp"""
        self.timeline.add_transcript_event(self.base_time + 2000, "Third", True)
        self.timeline.add_transcript_event(self.base_time, "First", True)
        self.timeline.add_transcript_event(self.base_time + 1000, "Second", True)
        
        self.timeline._ensure_sorted()
        
        self.assertEqual(self.timeline.events[0].data['text'], "First")
        self.assertEqual(self.timeline.events[1].data['text'], "Second")
        self.assertEqual(self.timeline.events[2].data['text'], "Third")
    
    # align() Query Tests
    def test_align_basic_query(self):
        """Should return aligned data for time slice"""
        self.timeline.add_expression_event(
            self.base_time, 'happy', 0.85, {'happy': 0.85}, 0.92
        )
        self.timeline.add_transcript_event(self.base_time + 500, "Hello", True)
        
        result = self.timeline.align(0, 1000)
        
        self.assertEqual(result['time_slice']['start_ms'], 0)
        self.assertEqual(result['time_slice']['end_ms'], 1000)
        self.assertEqual(result['total_events'], 2)
    
    def test_align_dominant_expression(self):
        """Should calculate dominant expression correctly"""
        self.timeline.add_expression_event(
            self.base_time, 'happy', 0.85, {'happy': 0.85}, 0.92
        )
        self.timeline.add_expression_event(
            self.base_time + 500, 'happy', 0.80, {'happy': 0.80}, 0.90
        )
        self.timeline.add_expression_event(
            self.base_time + 1000, 'neutral', 0.75, {'neutral': 0.75}, 0.88
        )
        
        result = self.timeline.align(0, 2000)
        
        self.assertIsNotNone(result['dominant_expression'])
        self.assertEqual(result['dominant_expression']['expression'], 'happy')
        self.assertEqual(result['dominant_expression']['count'], 2)
    
    def test_align_wpm_average(self):
        """Should calculate average WPM in time slice"""
        self.timeline.add_wpm_event(self.base_time, 140.0, 25, 10.0, 'optimal')
        self.timeline.add_wpm_event(self.base_time + 1000, 160.0, 30, 10.0, 'optimal')
        
        result = self.timeline.align(0, 2000)
        
        self.assertEqual(result['wpm_avg'], 150.0)
    
    def test_align_fillers_collection(self):
        """Should collect all fillers in time slice"""
        self.timeline.add_filler_event(self.base_time, "um", "Um, hello")
        self.timeline.add_filler_event(self.base_time + 500, "like", "Like, yeah")
        
        result = self.timeline.align(0, 1000)
        
        self.assertEqual(len(result['fillers']), 2)
        self.assertEqual(result['fillers'][0]['word'], "um")
        self.assertEqual(result['fillers'][1]['word'], "like")
    
    def test_align_pauses_collection(self):
        """Should collect all pauses in time slice"""
        self.timeline.add_pause_event(self.base_time, self.base_time + 500, 500.0)
        self.timeline.add_pause_event(self.base_time + 1000, self.base_time + 1600, 600.0)
        
        result = self.timeline.align(0, 2000)
        
        self.assertEqual(len(result['pauses']), 2)
        self.assertEqual(result['pauses'][0]['duration_ms'], 500.0)
    
    def test_align_attention_average(self):
        """Should calculate average attention score"""
        self.timeline.add_expression_event(
            self.base_time, 'happy', 0.85, {'happy': 0.85}, 0.90
        )
        self.timeline.add_expression_event(
            self.base_time + 500, 'neutral', 0.80, {'neutral': 0.80}, 0.80
        )
        
        result = self.timeline.align(0, 1000)
        
        self.assertIsNotNone(result['attention_avg'])
        self.assertEqual(result['attention_avg'], 0.85)
    
    def test_align_empty_slice(self):
        """Should handle empty time slice correctly"""
        self.timeline.add_transcript_event(self.base_time, "Hello", True)
        
        result = self.timeline.align(5000, 6000)
        
        self.assertEqual(result['total_events'], 0)
        self.assertIsNone(result['dominant_expression'])
        self.assertEqual(len(result['fillers']), 0)
    
    # get_all_events() Tests
    def test_get_all_events_unfiltered(self):
        """Should return all events when no filter applied"""
        self.timeline.add_transcript_event(self.base_time, "Hello", True)
        self.timeline.add_filler_event(self.base_time + 500, "um", "Um")
        
        events = self.timeline.get_all_events()
        
        self.assertEqual(len(events), 2)
    
    def test_get_all_events_filtered(self):
        """Should return only filtered event type"""
        self.timeline.add_transcript_event(self.base_time, "Hello", True)
        self.timeline.add_filler_event(self.base_time + 500, "um", "Um")
        self.timeline.add_transcript_event(self.base_time + 1000, "World", True)
        
        events = self.timeline.get_all_events(event_type='transcript')
        
        self.assertEqual(len(events), 2)
        self.assertTrue(all(e['event_type'] == 'transcript' for e in events))
    
    # export_session() Tests
    def test_export_session_metadata(self):
        """Should export session with correct metadata"""
        self.timeline.add_transcript_event(self.base_time, "Hello", True)
        self.timeline.add_filler_event(self.base_time + 1000, "um", "Um")
        
        export = self.timeline.export_session()
        
        self.assertIn('session_metadata', export)
        self.assertEqual(export['session_metadata']['total_events'], 2)
        self.assertEqual(export['session_metadata']['duration_ms'], 1000)
    
    def test_export_session_event_counts(self):
        """Should count events by type in export"""
        self.timeline.add_transcript_event(self.base_time, "Hello", True)
        self.timeline.add_transcript_event(self.base_time + 500, "World", True)
        self.timeline.add_filler_event(self.base_time + 1000, "um", "Um")
        
        export = self.timeline.export_session()
        
        self.assertEqual(export['session_metadata']['event_counts']['transcript'], 2)
        self.assertEqual(export['session_metadata']['event_counts']['filler'], 1)
    
    def test_export_session_events_structure(self):
        """Should export events with correct structure"""
        self.timeline.add_transcript_event(self.base_time, "Hello", True)
        
        export = self.timeline.export_session()
        
        self.assertIn('events', export)
        self.assertEqual(len(export['events']), 1)
        self.assertIn('timestamp_ms', export['events'][0])
        self.assertIn('event_type', export['events'][0])
        self.assertIn('data', export['events'][0])


# Run tests
if __name__ == '__main__':
    print("=" * 70)
    print("TIMELINE.TS UNIT TESTS")
    print("=" * 70)
    print()
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUnifiedTimeline)
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
