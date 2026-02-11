"""
OratorIQ Unified Timeline System
Normalizes all events to session-relative timestamps (ms from start)
Provides align() utility to query data for any time slice
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class TimelineEvent:
    """Base timeline event with session-relative timestamp"""
    timestamp_ms: int  # Milliseconds from session start
    event_type: str    # 'expression', 'transcript', 'filler', 'pause', 'wpm'
    data: Dict[str, Any]  # Event-specific data


class UnifiedTimeline:
    """
    Unified timeline system for OratorIQ session data.
    All events stored with session-relative timestamps in milliseconds.
    """
    
    def __init__(self, session_start_time: Optional[int] = None):
        """
        Initialize timeline with optional session start time.
        
        Args:
            session_start_time: Unix timestamp (ms) when session started.
                               If None, first event sets the baseline.
        """
        self.session_start_time = session_start_time
        self.events: List[TimelineEvent] = []
        self._sorted = True
        
    def _to_relative_ms(self, timestamp: int) -> int:
        """Convert absolute timestamp to session-relative milliseconds"""
        if self.session_start_time is None:
            # First event - set baseline
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
    
    def add_transcript_event(self, timestamp: int, text: str, 
                           is_final: bool = False):
        """Add transcript segment"""
        event = TimelineEvent(
            timestamp_ms=self._to_relative_ms(timestamp),
            event_type='transcript',
            data={
                'text': text,
                'is_final': is_final
            }
        )
        self.events.append(event)
        self._sorted = False
    
    def add_filler_event(self, timestamp: int, word: str, text: str):
        """Add filler word detection"""
        event = TimelineEvent(
            timestamp_ms=self._to_relative_ms(timestamp),
            event_type='filler',
            data={
                'word': word,
                'text': text
            }
        )
        self.events.append(event)
        self._sorted = False
    
    def add_pause_event(self, timestamp_start: int, timestamp_end: int, 
                       duration_ms: float):
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
        """
        Query aligned data for a time slice.
        
        Args:
            t_start_ms: Start time (ms from session start)
            t_end_ms: End time (ms from session start)
            
        Returns:
            Dictionary with:
            - dominant_expression: Most frequent expression in slice
            - wpm_avg: Average WPM in slice
            - fillers: List of filler events in slice
            - pauses: List of pause events in slice
            - transcripts: List of transcript segments in slice
            - expression_distribution: Count of each expression
            - attention_avg: Average attention score
        """
        self._ensure_sorted()
        
        # Filter events in time slice
        slice_events = [e for e in self.events 
                       if t_start_ms <= e.timestamp_ms <= t_end_ms]
        
        # Initialize result structure
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
        
        # Process events by type
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
        
        # Calculate aggregates
        if expression_scores:
            # Dominant expression = most frequent
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
        
        # Convert defaultdict to dict for JSON serialization
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
        """
        Export complete session data as JSON-serializable dict.
        
        Returns:
            Complete session data with metadata and all events
        """
        self._ensure_sorted()
        
        # Calculate session metadata
        duration_ms = max([e.timestamp_ms for e in self.events]) if self.events else 0
        
        # Count events by type
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


# Demonstration
print("=" * 70)
print("ORATORIQ UNIFIED TIMELINE SYSTEM")
print("=" * 70)

# Create timeline
timeline = UnifiedTimeline()

# Simulate session events (using ms timestamps)
base_time = 1700000000000  # Example start time

# Add various events
timeline.add_expression_event(
    base_time, 
    'neutral', 
    0.85,
    {'neutral': 0.85, 'happy': 0.10, 'sad': 0.05},
    0.92
)

timeline.add_transcript_event(base_time + 100, "Hello everyone", is_final=False)
timeline.add_transcript_event(base_time + 500, "Hello everyone, um", is_final=True)
timeline.add_filler_event(base_time + 500, "um", "Hello everyone, um")

timeline.add_expression_event(
    base_time + 1000,
    'happy',
    0.75,
    {'neutral': 0.15, 'happy': 0.75, 'sad': 0.10},
    0.88
)

timeline.add_pause_event(base_time + 1200, base_time + 1800, 600)
timeline.add_wpm_event(base_time + 2000, 145.5, 25, 10.0, 'optimal')

timeline.add_expression_event(
    base_time + 2500,
    'happy',
    0.80,
    {'neutral': 0.10, 'happy': 0.80, 'sad': 0.10},
    0.90
)

print(f"\n✅ Timeline initialized with {len(timeline.events)} events")
print(f"📅 Session start: {timeline.session_start_time}")

# Test align() query
print("\n" + "=" * 70)
print("TESTING align() QUERY UTILITY")
print("=" * 70)

slice_result = timeline.align(0, 3000)

print(f"\n📊 Query: align(0, 3000) - First 3 seconds")
print(f"   Duration: {slice_result['time_slice']['duration_ms']}ms")
print(f"   Total events: {slice_result['total_events']}")
print(f"   Dominant expression: {slice_result['dominant_expression']}")
print(f"   Average WPM: {slice_result['wpm_avg']}")
print(f"   Average attention: {slice_result['attention_avg']:.2f}")
print(f"   Fillers detected: {len(slice_result['fillers'])}")
print(f"   Pauses detected: {len(slice_result['pauses'])}")
print(f"   Transcript segments: {len(slice_result['transcripts'])}")
print(f"   Expression distribution: {slice_result['expression_distribution']}")

# Export session
print("\n" + "=" * 70)
print("SESSION EXPORT")
print("=" * 70)

session_export = timeline.export_session()
print(f"\n✅ Session exported successfully")
print(f"   Duration: {session_export['session_metadata']['duration_ms']}ms")
print(f"   Total events: {session_export['session_metadata']['total_events']}")
print(f"   Event breakdown: {session_export['session_metadata']['event_counts']}")

# Pretty print sample
print("\n📄 Sample JSON export (first 2 events):")
sample_export = {
    'session_metadata': session_export['session_metadata'],
    'events': session_export['events'][:2]
}
print(json.dumps(sample_export, indent=2))

print("\n" + "=" * 70)
print("✅ UNIFIED TIMELINE SYSTEM READY")
print("=" * 70)
print("\n🎯 Features:")
print("  ✓ Session-relative timestamps (ms from start)")
print("  ✓ align(tStart, tEnd) query utility")
print("  ✓ Dominant expression extraction")
print("  ✓ WPM aggregation")
print("  ✓ Filler/pause tracking")
print("  ✓ session.json export")
print("  ✓ All event types unified")

# Export the timeline class for downstream use
unified_timeline_class = UnifiedTimeline
demo_timeline = timeline
