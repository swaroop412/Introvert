# OratorIQ Unified Timeline System ✅

## Overview
The unified timeline system normalizes all OratorIQ session events to **session-relative timestamps** (milliseconds from session start) and provides powerful query utilities for time-slice analysis.

## Core Features

### 1. **Session-Relative Timestamps**
All events are normalized to milliseconds from session start (t=0), making temporal alignment trivial:
- `0ms` = Session start
- Timestamps are always relative, not absolute
- Easy to query any time slice

### 2. **Event Types Supported**
- **expression**: Facial expressions with confidence scores and attention
- **transcript**: Speech-to-text segments (interim and final)
- **filler**: Detected filler words ("um", "uh", "like", etc.)
- **pause**: Detected pauses >400ms
- **wpm**: Words-per-minute calculations with status

### 3. **align(tStart, tEnd) Query Utility**
Query any time slice and get comprehensive aligned data:

```python
result = align(0, 3000)  # First 3 seconds

# Returns:
{
  'time_slice': {start_ms, end_ms, duration_ms},
  'dominant_expression': {expression, count, avg_confidence},
  'wpm_avg': 145.5,
  'fillers': [{timestamp_ms, word, text}, ...],
  'pauses': [{timestamp_ms, duration_ms, end_ms}, ...],
  'transcripts': [{timestamp_ms, text, is_final}, ...],
  'expression_distribution': {'happy': 3, 'neutral': 2},
  'attention_avg': 0.88,
  'total_events': 12
}
```

### 4. **Session Export**
Generate complete session.json with metadata and all events:

```python
session_data = export_session()

# Returns:
{
  'session_metadata': {
    'session_start_time': 1700000000000,
    'duration_ms': 45230,
    'total_events': 127,
    'event_counts': {
      'expression': 45,
      'transcript': 32,
      'filler': 8,
      'pause': 12,
      'wpm': 30
    }
  },
  'events': [...]  # All events sorted by timestamp
}
```

## API Functions

### Adding Events
```python
# Expression
add_expression(timestamp, expression, confidence, all_expressions, attention_score)

# Transcript
add_transcript(timestamp, text, is_final=False)

# Filler word
add_filler(timestamp, word, full_text)

# Pause
add_pause(timestamp_start, timestamp_end, duration_ms)

# WPM
add_wpm(timestamp, wpm, word_count, duration_s, status)
```

### Querying
```python
# Query time slice
align(t_start_ms, t_end_ms)

# Export full session
export_session()
```

## Integration Points

### Frontend (React/TypeScript)
The timeline system should be integrated with:
1. **useFaceAPI hook** - Expression events flow into timeline
2. **STT streaming** - Transcript segments added in real-time
3. **Disfluency detector** - Filler/pause/WPM events added
4. **Session recorder** - Exports timeline on session end

### Data Flow
```
Webcam → FaceAPI → add_expression()
                ↓
Microphone → STT → add_transcript()
                ↓
            Timeline ← Disfluency Detector
                ↓
        align() queries for UI updates
                ↓
        export_session() on session end
```

## Success Criteria Met ✅

1. ✅ **Timeline queries work correctly** - align() returns proper aggregated data
2. ✅ **Session export contains complete aligned data** - export_session() includes all events with metadata
3. ✅ **All events normalized to session-relative timestamps** - ms from start
4. ✅ **Dominant expression extraction** - Most frequent expression in time slice
5. ✅ **WPM aggregation** - Average WPM for time slices
6. ✅ **Filler/pause tracking** - All disfluencies tracked with timestamps

## Next Steps for Full Implementation

1. **Create TypeScript/JavaScript version** for frontend
2. **Integrate with useFaceAPI hook** to stream expression events
3. **Connect to STT pipeline** for transcript events
4. **Wire up disfluency detector** for filler/pause/WPM events
5. **Add session export UI** to download session.json
6. **Build timeline visualization** component for playback

---

**Status**: Core timeline system implemented and validated ✅
