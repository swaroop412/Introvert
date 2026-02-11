"""
DisfluencyTimeline React Component
Horizontal timeline showing disfluency markers that jump to transcript on click
"""

disfluency_timeline_code = '''
import React, { useMemo } from 'react';

interface DisfluencyEvent {
  type: 'filler_word' | 'pause' | 'repetition';
  timestamp: number;
  detail: {
    word?: string;
    duration_ms?: number;
    count?: number;
    [key: string]: any;
  };
}

interface DisfluencyTimelineProps {
  events: DisfluencyEvent[];
  duration: number;
  currentTime: number;
  onSeek?: (timestamp: number) => void;
}

export const DisfluencyTimeline: React.FC<DisfluencyTimelineProps> = ({
  events,
  duration,
  currentTime,
  onSeek
}) => {
  // Group events by type for legend
  const eventCounts = useMemo(() => {
    const counts = {
      filler_word: 0,
      pause: 0,
      repetition: 0
    };
    events.forEach(event => {
      if (event.type in counts) {
        counts[event.type]++;
      }
    });
    return counts;
  }, [events]);

  // Color mapping for event types
  const eventStyles = {
    filler_word: {
      color: '#FF9F9B',
      label: 'Filler Words',
      icon: '💬'
    },
    pause: {
      color: '#FFB482',
      label: 'Pauses',
      icon: '⏸️'
    },
    repetition: {
      color: '#D0BBFF',
      label: 'Repetitions',
      icon: '🔄'
    }
  };

  const handleMarkerClick = (event: DisfluencyEvent) => {
    if (onSeek) {
      onSeek(event.timestamp);
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getMarkerTooltip = (event: DisfluencyEvent): string => {
    const time = formatTime(event.timestamp);
    switch (event.type) {
      case 'filler_word':
        return `${time} - Filler: "${event.detail.word}"`;
      case 'pause':
        return `${time} - Pause: ${event.detail.duration_ms}ms`;
      case 'repetition':
        return `${time} - Repeated: "${event.detail.word}" (${event.detail.count}x)`;
      default:
        return `${time}`;
    }
  };

  return (
    <div style={{
      backgroundColor: '#1D1D20',
      padding: '24px',
      borderRadius: '8px',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <h2 style={{ 
        marginTop: 0, 
        marginBottom: '16px',
        fontSize: '20px',
        fontWeight: 600,
        color: '#fbfbff'
      }}>
        📊 Disfluency Timeline
      </h2>

      {/* Legend */}
      <div style={{
        display: 'flex',
        gap: '20px',
        marginBottom: '20px',
        fontSize: '13px'
      }}>
        {Object.entries(eventStyles).map(([type, style]) => (
          <div key={type} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '16px' }}>{style.icon}</span>
            <div
              style={{
                width: '12px',
                height: '12px',
                backgroundColor: style.color,
                borderRadius: '2px'
              }}
            />
            <span style={{ color: '#fbfbff' }}>
              {style.label} ({eventCounts[type as keyof typeof eventCounts]})
            </span>
          </div>
        ))}
      </div>

      {/* Timeline container */}
      <div style={{
        position: 'relative',
        height: '80px',
        backgroundColor: '#2A2A2E',
        borderRadius: '4px',
        border: '1px solid #3E3E42',
        overflow: 'visible'
      }}>
        {/* Progress indicator */}
        <div
          style={{
            position: 'absolute',
            left: `${(currentTime / duration) * 100}%`,
            top: 0,
            bottom: 0,
            width: '2px',
            backgroundColor: '#ffd400',
            zIndex: 10,
            transition: 'left 0.1s linear'
          }}
        >
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '8px',
            height: '8px',
            backgroundColor: '#ffd400',
            borderRadius: '50%',
            border: '2px solid #1D1D20'
          }} />
        </div>

        {/* Disfluency markers */}
        {events.map((event, index) => {
          const position = (event.timestamp / duration) * 100;
          const style = eventStyles[event.type];

          return (
            <div
              key={index}
              onClick={() => handleMarkerClick(event)}
              title={getMarkerTooltip(event)}
              style={{
                position: 'absolute',
                left: `${position}%`,
                top: '50%',
                transform: 'translate(-50%, -50%)',
                width: '10px',
                height: '40px',
                backgroundColor: style.color,
                borderRadius: '2px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                opacity: 0.8,
                border: '1px solid rgba(0, 0, 0, 0.2)',
                zIndex: 5
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.opacity = '1';
                e.currentTarget.style.height = '60px';
                e.currentTarget.style.zIndex = '20';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.opacity = '0.8';
                e.currentTarget.style.height = '40px';
                e.currentTarget.style.zIndex = '5';
              }}
            />
          );
        })}

        {/* Time markers */}
        <div style={{
          position: 'absolute',
          bottom: '-20px',
          left: 0,
          right: 0,
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '11px',
          color: '#909094'
        }}>
          <span>0:00</span>
          <span>{formatTime(duration / 2)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      <div style={{
        marginTop: '28px',
        paddingTop: '16px',
        borderTop: '1px solid #909094',
        fontSize: '13px',
        color: '#909094'
      }}>
        <p style={{ margin: 0 }}>
          💡 <strong>Click</strong> markers to jump to that moment in the transcript
        </p>
      </div>
    </div>
  );
};

export default DisfluencyTimeline;
'''

print("=" * 70)
print("✅ DISFLUENCY TIMELINE COMPONENT CREATED")
print("=" * 70)

print("\n📦 Component: DisfluencyTimeline")
print("-" * 70)
print("\n🎯 Key Features:")
print("  • Horizontal timeline with duration-based positioning")
print("  • Color-coded markers for different disfluency types")
print("  • Interactive markers that expand on hover")
print("  • Click markers to seek to that timestamp")
print("  • Current playback position indicator")
print("  • Legend with event counts")
print("  • Time markers at start, middle, and end")

print("\n📋 Props Interface:")
print("""
  interface DisfluencyTimelineProps {
    events: DisfluencyEvent[];  // Array of disfluency events
    duration: number;           // Total duration in seconds
    currentTime: number;        // Current playback time
    onSeek?: (timestamp: number) => void;  // Callback for seeking
  }

  interface DisfluencyEvent {
    type: 'filler_word' | 'pause' | 'repetition';
    timestamp: number;
    detail: {
      word?: string;
      duration_ms?: number;
      count?: number;
    };
  }
""")

print("\n🎨 Color Mapping:")
print("  • Filler Words (💬): #FF9F9B (coral)")
print("  • Pauses (⏸️): #FFB482 (orange)")
print("  • Repetitions (🔄): #D0BBFF (lavender)")
print("  • Current time: #ffd400 (yellow)")
print("  • Background: #1D1D20 / #2A2A2E")

print("\n💫 Interactions:")
print("  • Markers expand on hover (40px → 60px)")
print("  • Tooltips show event details and timestamp")
print("  • Click triggers onSeek callback")
print("  • Current time indicator follows playback")

print("\n🔧 Usage Example:")
print("""
  import { DisfluencyTimeline } from './DisfluencyTimeline';

  const events = [
    { type: 'filler_word', timestamp: 2.5, detail: { word: 'um' } },
    { type: 'pause', timestamp: 5.0, detail: { duration_ms: 600 } },
    { type: 'repetition', timestamp: 8.2, detail: { word: 'the', count: 2 } }
  ];

  <DisfluencyTimeline
    events={events}
    duration={totalDuration}
    currentTime={audioCurrentTime}
    onSeek={(time) => audioRef.current.currentTime = time}
  />
""")

print("\n📊 Integration with Disfluency Detection:")
print("""
  The DisfluencyDetector class provides events in the correct format:
  
  const detector = new DisfluencyDetector();
  const events = detector.process_transcript_segment(text, timestamp);
  
  These events can be directly passed to the DisfluencyTimeline component.
""")

print("\n" + "=" * 70)
print("📄 Component code saved to variable: disfluency_timeline_code")
print("=" * 70)
