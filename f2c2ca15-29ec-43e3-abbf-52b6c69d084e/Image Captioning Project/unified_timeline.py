"""OratorIQ Unified Timeline System - Session-relative timestamps + align() query"""

import json

timeline_events = []
session_start = None

def to_relative_ms(timestamp):
    """Convert absolute timestamp to session-relative ms"""
    global session_start
    if session_start is None:
        session_start = timestamp
        return 0
    return timestamp - session_start

def add_expression(timestamp, expression, confidence, all_expr, attention):
    """Add facial expression event"""
    timeline_events.append({
        'timestamp_ms': to_relative_ms(timestamp),
        'type': 'expression',
        'expression': expression,
        'confidence': confidence,
        'all_expressions': all_expr,
        'attention_score': attention
    })

def add_transcript(timestamp, text, is_final=False):
    """Add transcript segment"""
    timeline_events.append({
        'timestamp_ms': to_relative_ms(timestamp),
        'type': 'transcript',
        'text': text,
        'is_final': is_final
    })

def add_filler(timestamp, word, text):
    """Add filler word"""
    timeline_events.append({
        'timestamp_ms': to_relative_ms(timestamp),
        'type': 'filler',
        'word': word,
        'text': text
    })

def add_pause(ts_start, ts_end, duration_ms):
    """Add pause detection"""
    timeline_events.append({
        'timestamp_ms': to_relative_ms(ts_start),
        'type': 'pause',
        'duration_ms': duration_ms,
        'end_ms': to_relative_ms(ts_end)
    })

def add_wpm(timestamp, wpm, word_count, duration_s, status):
    """Add WPM calculation"""
    timeline_events.append({
        'timestamp_ms': to_relative_ms(timestamp),
        'type': 'wpm',
        'wpm': wpm,
        'word_count': word_count,
        'duration_s': duration_s,
        'status': status
    })

def align(t_start_ms, t_end_ms):
    """Query aligned data for time slice [t_start_ms, t_end_ms]"""
    sorted_events = sorted(timeline_events, key=lambda e: e['timestamp_ms'])
    slice_events = [e for e in sorted_events if t_start_ms <= e['timestamp_ms'] <= t_end_ms]
    
    result = {
        'time_slice': {'start_ms': t_start_ms, 'end_ms': t_end_ms, 'duration_ms': t_end_ms - t_start_ms},
        'dominant_expression': None,
        'wpm_avg': None,
        'fillers': [],
        'pauses': [],
        'transcripts': [],
        'expression_distribution': {},
        'attention_avg': None,
        'total_events': len(slice_events)
    }
    
    expr_counts = {}
    expr_confidences = {}
    attention_vals = []
    wpm_vals = []
    
    for e in slice_events:
        if e['type'] == 'expression':
            expr = e['expression']
            expr_counts[expr] = expr_counts.get(expr, 0) + 1
            if expr not in expr_confidences:
                expr_confidences[expr] = []
            expr_confidences[expr].append(e['confidence'])
            attention_vals.append(e['attention_score'])
            
        elif e['type'] == 'wpm':
            wpm_vals.append(e['wpm'])
            
        elif e['type'] == 'filler':
            result['fillers'].append({'timestamp_ms': e['timestamp_ms'], 'word': e['word'], 'text': e['text']})
            
        elif e['type'] == 'pause':
            result['pauses'].append({'timestamp_ms': e['timestamp_ms'], 'duration_ms': e['duration_ms'], 'end_ms': e['end_ms']})
            
        elif e['type'] == 'transcript':
            result['transcripts'].append({'timestamp_ms': e['timestamp_ms'], 'text': e['text'], 'is_final': e['is_final']})
    
    if expr_counts:
        dominant = max(expr_counts.items(), key=lambda x: x[1])[0]
        result['dominant_expression'] = {
            'expression': dominant,
            'count': expr_counts[dominant],
            'avg_confidence': sum(expr_confidences[dominant]) / len(expr_confidences[dominant])
        }
        result['expression_distribution'] = expr_counts
    
    if wpm_vals:
        result['wpm_avg'] = sum(wpm_vals) / len(wpm_vals)
    
    if attention_vals:
        result['attention_avg'] = sum(attention_vals) / len(attention_vals)
    
    return result

def export_session():
    """Export complete session as JSON"""
    sorted_events = sorted(timeline_events, key=lambda e: e['timestamp_ms'])
    duration_ms = max([e['timestamp_ms'] for e in sorted_events]) if sorted_events else 0
    
    counts = {}
    for e in sorted_events:
        counts[e['type']] = counts.get(e['type'], 0) + 1
    
    return {
        'session_metadata': {
            'session_start_time': session_start,
            'duration_ms': duration_ms,
            'total_events': len(sorted_events),
            'event_counts': counts
        },
        'events': sorted_events
    }

# Demo
print("=" * 70)
print("ORATORIQ UNIFIED TIMELINE SYSTEM")
print("=" * 70)

base = 1700000000000

add_expression(base, 'neutral', 0.85, {'neutral': 0.85, 'happy': 0.10}, 0.92)
add_transcript(base + 100, "Hello everyone", False)
add_filler(base + 500, "um", "Hello everyone, um")
add_expression(base + 1000, 'happy', 0.75, {'happy': 0.75, 'neutral': 0.15}, 0.88)
add_pause(base + 1200, base + 1800, 600)
add_wpm(base + 2000, 145.5, 25, 10.0, 'optimal')
add_expression(base + 2500, 'happy', 0.80, {'happy': 0.80, 'neutral': 0.10}, 0.90)

print(f"\n✅ Timeline: {len(timeline_events)} events")

print("\n" + "=" * 70)
print("TESTING align() QUERY")
print("=" * 70)

result = align(0, 3000)
print(f"\n📊 align(0, 3000):")
print(f"   Duration: {result['time_slice']['duration_ms']}ms")
print(f"   Events: {result['total_events']}")
print(f"   Dominant: {result['dominant_expression']}")
print(f"   WPM: {result['wpm_avg']}")
print(f"   Attention: {result['attention_avg']:.2f}")
print(f"   Fillers: {len(result['fillers'])}")
print(f"   Pauses: {len(result['pauses'])}")

print("\n" + "=" * 70)
print("SESSION EXPORT")
print("=" * 70)

session = export_session()
print(f"\n✅ {session['session_metadata']['total_events']} events")
print(f"   Duration: {session['session_metadata']['duration_ms']}ms")
print(f"   Breakdown: {session['session_metadata']['event_counts']}")

print("\n📄 JSON sample:")
print(json.dumps({'session_metadata': session['session_metadata'], 'events': session['events'][:2]}, indent=2))

print("\n" + "=" * 70)
print("✅ UNIFIED TIMELINE READY")
print("=" * 70)
