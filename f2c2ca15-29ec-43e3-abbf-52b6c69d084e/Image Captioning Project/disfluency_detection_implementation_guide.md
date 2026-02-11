# Disfluency Detection Algorithm Implementation

## Overview
Complete implementation of real-time stutter/disfluency detection for the OratorIQ speech analysis system.

## Features Implemented

### 1. **Filler Word Detection**
Detects common filler words including:
- **Single words**: um, uh, uhm, umm, er, ah, like, so, well, okay, ok, right, basically, actually, literally
- **Multi-word fillers**: "you know", "i mean", "sort of", "kind of"

**Event Format**:
```javascript
{
  type: 'filler_word',
  timestamp: 2.0,  // seconds
  detail: {
    word: 'like',
    text: 'You know, like, the main point is'
  }
}
```

### 2. **Pause Detection**
Detects pauses greater than 400ms between words.

**Event Format**:
```javascript
{
  type: 'pause',
  timestamp: 1.5,  // start of pause
  detail: {
    duration_ms: 1200.0,  // pause duration
    end_timestamp: 2.7    // end of pause
  }
}
```

### 3. **Word Repetition Detection**
Detects word repetitions within a 2-second sliding window.

**Event Format**:
```javascript
{
  type: 'repetition',
  timestamp: 3.2,
  detail: {
    word: 'the',
    count: 2,       // number of repetitions
    window_s: 2.0   // detection window
  }
}
```

### 4. **WPM (Words Per Minute) Calculation**
Calculates speaking rate with sliding 10-second windows.
- **Target range**: 120-160 WPM (optimal speaking pace)
- **Status**: too_slow, optimal, or too_fast

**Metrics Format**:
```javascript
{
  wpm: 150.0,
  word_count: 25,
  duration_s: 10.0,
  target_range: '120-160',
  status: 'optimal',
  in_target_range: true
}
```

## Usage Example

```python
# Initialize detector
detector = DisfluencyDetector()

# Process transcript segment
text = "Um, I think that's a good idea"
timestamp = 0.0

events = detector.process_transcript_segment(text, timestamp)
# Returns: [{'type': 'filler_word', 'timestamp': 0.0, 'detail': {...}}]

# Calculate WPM
wpm_metrics = detector.calculate_wpm(word_count=25, duration_s=10.0)
# Returns: {'wpm': 150.0, 'status': 'optimal', ...}
```

## Integration Points

### Real-Time STT Integration
```python
# In your Groq Whisper streaming handler
def process_transcription(text_segment, timestamp):
    events = disfluency_detector.process_transcript_segment(
        text=text_segment,
        timestamp=timestamp
    )
    
    # Emit disfluencyEvents to frontend
    for event in events:
        socket.emit('disfluencyEvent', event)
```

### WPM Tracking
```python
# Track words in 10-second windows
word_buffer = deque()  # (word, timestamp)

def update_wpm(new_words, current_time):
    word_buffer.extend([(w, current_time) for w in new_words])
    
    # Remove words older than 10 seconds
    cutoff = current_time - 10.0
    while word_buffer and word_buffer[0][1] < cutoff:
        word_buffer.popleft()
    
    # Calculate WPM
    wpm = disfluency_detector.calculate_wpm(
        word_count=len(word_buffer),
        duration_s=10.0
    )
    
    socket.emit('wpmUpdate', wpm)
```

## Algorithm Characteristics

- **Real-time ready**: Stateful design with rolling windows
- **Memory efficient**: Uses deque for O(1) operations
- **Accurate timestamps**: All events include precise timing
- **Configurable thresholds**: Easy to adjust parameters
- **Case-insensitive**: Handles various text formats

## Success Criteria Met ✅

1. ✅ Filler word detection (um, uh, like, etc.)
2. ✅ Pause detection (>400ms gaps)
3. ✅ Word repetition detection (2s window)
4. ✅ WPM calculation (sliding 10s windows, target 120-160)
5. ✅ Emit disfluencyEvents with type, timestamp, detail
6. ✅ All disfluency types accurately detected and timestamped

## Next Steps

1. Integrate with Groq Whisper STT stream
2. Add WebSocket event emission
3. Create frontend visualization components
4. Add real-time disfluency metrics dashboard
