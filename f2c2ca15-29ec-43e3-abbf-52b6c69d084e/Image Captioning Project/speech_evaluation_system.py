"""
OratorIQ Speech Mode - Evaluation System
Analyzes complete speech sessions: identifies strongest segments, 
peak confusion moments, notable quotes, and provides overall assessment
"""

import re
from collections import defaultdict

class SpeechEvaluationSystem:
    """Evaluates speech sessions and identifies key moments and quotes"""
    
    def __init__(self):
        self.evaluation_criteria = {
            'excellent': {'wpm_range': (130, 150), 'max_fillers_per_min': 2, 'max_long_pauses': 1},
            'good': {'wpm_range': (120, 160), 'max_fillers_per_min': 4, 'max_long_pauses': 3},
            'needs_improvement': {'wpm_range': (100, 180), 'max_fillers_per_min': 8, 'max_long_pauses': 5}
        }
    
    def evaluate_session(self, engine):
        """Comprehensive session evaluation"""
        metrics = engine.get_current_metrics()
        key_moments = engine.get_key_moments()
        
        # Overall performance rating
        rating = self._calculate_rating(metrics)
        
        # Strongest segment analysis
        strongest_segment = self._find_strongest_segment(engine)
        
        # Notable quotes (segments without fillers)
        notable_quotes = self._extract_notable_quotes(engine)
        
        # Improvement recommendations
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
        """Calculate overall performance rating"""
        wpm = metrics['wpm']
        fillers_per_min = metrics['fillers_per_min']
        
        # Check each tier
        for rating, criteria in self.evaluation_criteria.items():
            wpm_min, wpm_max = criteria['wpm_range']
            if (wpm_min <= wpm <= wpm_max and 
                fillers_per_min <= criteria['max_fillers_per_min']):
                return rating
        
        return 'needs_significant_improvement'
    
    def _find_strongest_segment(self, engine):
        """Find the best 30-second segment based on minimal fillers and optimal pace"""
        if not engine.filler_events or engine.session_start is None:
            return None
        
        session_duration = engine.get_current_metrics()['session_duration_s']
        
        best_score = -float('inf')
        best_segment = None
        
        # Check every 5-second window up to 30s
        window_size = 30
        step_size = 5
        
        for start_offset in range(0, int(session_duration - window_size) + 1, step_size):
            window_start = engine.session_start + start_offset
            window_end = window_start + window_size
            
            # Count fillers in window
            fillers_in_window = sum(1 for f in engine.filler_events 
                                   if window_start <= f['timestamp'] < window_end)
            
            # Count pauses in window
            pauses_in_window = sum(1 for p in engine.pause_events 
                                  if window_start <= p['timestamp'] < window_end)
            
            # Count words in window
            words_in_window = sum(1 for t in engine.word_timestamps 
                                 if window_start <= t < window_end)
            
            # Calculate WPM for this window
            wpm = (words_in_window / window_size) * 60
            
            # Score: prioritize low fillers, optimal WPM, few pauses
            wpm_penalty = abs(wpm - 140)  # 140 is ideal WPM
            score = -fillers_in_window * 10 - pauses_in_window * 5 - wpm_penalty * 0.5
            
            if score > best_score and words_in_window > 10:  # At least some content
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
        """Extract clean segments without fillers as notable quotes"""
        # This is a placeholder - in real implementation would need transcript segments
        # For now, we'll identify time periods with no fillers
        if not engine.filler_events:
            return []
        
        quotes = []
        
        # Find gaps between fillers (>10s) as potential quote moments
        sorted_fillers = sorted(engine.filler_events, key=lambda f: f['timestamp'])
        
        for i in range(len(sorted_fillers) - 1):
            gap_duration = sorted_fillers[i+1]['timestamp'] - sorted_fillers[i]['timestamp']
            
            if gap_duration > 10:  # 10+ seconds without fillers
                quote_time = sorted_fillers[i]['timestamp'] + gap_duration / 2
                relative_time = quote_time - engine.session_start
                
                quotes.append({
                    'timestamp_offset_s': round(relative_time, 1),
                    'duration_s': round(gap_duration, 1),
                    'note': 'Clean delivery - no fillers',
                    'context': f"Between T+{round(sorted_fillers[i]['timestamp'] - engine.session_start, 1)}s and T+{round(sorted_fillers[i+1]['timestamp'] - engine.session_start, 1)}s"
                })
        
        return quotes[:3]  # Top 3 quotes
    
    def _generate_recommendations(self, metrics, key_moments):
        """Generate improvement recommendations"""
        recommendations = []
        
        # WPM feedback
        if metrics['wpm_status'] == 'too_slow':
            recommendations.append({
                'category': 'pace',
                'priority': 'high',
                'message': f"Increase speaking pace - current {metrics['wpm']} WPM is below target range {metrics['wpm_target_range']}"
            })
        elif metrics['wpm_status'] == 'too_fast':
            recommendations.append({
                'category': 'pace',
                'priority': 'high',
                'message': f"Slow down - current {metrics['wpm']} WPM exceeds target range {metrics['wpm_target_range']}"
            })
        else:
            recommendations.append({
                'category': 'pace',
                'priority': 'low',
                'message': f"Good pace maintained at {metrics['wpm']} WPM"
            })
        
        # Filler words feedback
        if metrics['fillers_per_min'] > 5:
            recommendations.append({
                'category': 'fillers',
                'priority': 'high',
                'message': f"Reduce filler words - {metrics['fillers_per_min']:.1f}/min is high. Practice pausing instead of using fillers."
            })
        elif metrics['fillers_per_min'] > 3:
            recommendations.append({
                'category': 'fillers',
                'priority': 'medium',
                'message': f"Moderate filler usage at {metrics['fillers_per_min']:.1f}/min. Aim for under 2/min."
            })
        else:
            recommendations.append({
                'category': 'fillers',
                'priority': 'low',
                'message': f"Excellent filler control at {metrics['fillers_per_min']:.1f}/min"
            })
        
        # Pause feedback
        long_pauses = sum(1 for m in key_moments if m['type'] == 'long_pause')
        if long_pauses > 3:
            recommendations.append({
                'category': 'pauses',
                'priority': 'medium',
                'message': f"{long_pauses} long pauses detected. Work on smoother transitions between thoughts."
            })
        
        return recommendations


# Demo evaluation system
print("=" * 70)
print("SPEECH MODE - EVALUATION SYSTEM")
print("=" * 70)

# Create a mock engine with sample data for testing
import time
from collections import deque

class MockEngine:
    def __init__(self):
        self.session_start = time.time() - 60  # 60 seconds ago
        self.word_timestamps = deque()
        self.filler_events = []
        self.pause_events = []
        self.total_words = 150
        self.total_fillers = 8
        
        # Add sample data
        base_time = self.session_start
        for i in range(150):
            self.word_timestamps.append(base_time + i * 0.4)
        
        # Add some filler events
        filler_times = [5, 12, 18, 25, 35, 42, 48, 55]
        for t in filler_times:
            self.filler_events.append({
                'timestamp': base_time + t,
                'word': 'um',
                'text': 'sample text'
            })
        
        # Add pause events
        self.pause_events.append({
            'timestamp': base_time + 20,
            'duration_ms': 1500,
            'end_timestamp': base_time + 21.5
        })
        self.pause_events.append({
            'timestamp': base_time + 45,
            'duration_ms': 1200,
            'end_timestamp': base_time + 46.2
        })
    
    def get_current_metrics(self):
        return {
            'wpm': 145.0,
            'wpm_status': 'optimal',
            'wpm_target_range': '120-160',
            'fillers_per_min': 8.0,
            'recent_fillers_60s': 8,
            'total_fillers': self.total_fillers,
            'recent_pauses_60s': 2,
            'total_pauses': 2,
            'total_words': self.total_words,
            'session_duration_s': 60.0
        }
    
    def get_key_moments(self):
        return [
            {
                'type': 'peak_confusion',
                'timestamp': self.session_start + 25,
                'description': '3 filler words in 30s window',
                'severity': 'medium'
            },
            {
                'type': 'long_pause',
                'timestamp': self.session_start + 20,
                'description': 'Pause: 1500ms',
                'severity': 'medium'
            }
        ]

mock_engine = MockEngine()

evaluator = SpeechEvaluationSystem()
evaluation = evaluator.evaluate_session(mock_engine)

print("\n📊 SESSION EVALUATION RESULTS")
print("=" * 70)

print(f"\n🎯 Overall Rating: {evaluation['overall_rating'].upper()}")

print("\n📈 Metrics Summary:")
for key, value in evaluation['metrics_summary'].items():
    print(f"   {key}: {value}")

if evaluation['strongest_segment']:
    print(f"\n💪 Strongest Segment:")
    seg = evaluation['strongest_segment']
    print(f"   Time: T+{seg['start_offset_s']}s to T+{seg['start_offset_s'] + seg['duration_s']}s")
    print(f"   WPM: {seg['wpm']} | Fillers: {seg['fillers']} | Pauses: {seg['pauses']}")
    print(f"   Score: {seg['score']}")

print(f"\n🔑 Key Moments: {len(evaluation['key_moments'])} identified")
for moment in evaluation['key_moments']:
    relative_time = moment['timestamp'] - mock_engine.session_start
    print(f"   • {moment['type']} at T+{relative_time:.1f}s - {moment['description']}")

if evaluation['notable_quotes']:
    print(f"\n💬 Notable Quotes: {len(evaluation['notable_quotes'])} clean segments")
    for quote in evaluation['notable_quotes']:
        print(f"   • T+{quote['timestamp_offset_s']}s ({quote['duration_s']}s) - {quote['note']}")

print(f"\n💡 Recommendations:")
for rec in evaluation['recommendations']:
    priority_icon = '🔴' if rec['priority'] == 'high' else ('🟡' if rec['priority'] == 'medium' else '🟢')
    print(f"   {priority_icon} [{rec['category'].upper()}] {rec['message']}")

print("\n" + "=" * 70)
print("✅ EVALUATION SYSTEM READY")
print("=" * 70)

speech_evaluator = evaluator
demo_evaluation = evaluation
