"""
TranscriptPanel React Component with Word-Level Timestamp Hover
Interactive transcript viewer with scroll-to-time synchronization
"""

transcript_panel_code = '''
import React, { useEffect, useRef, useState } from 'react';

interface Word {
  word: string;
  start: number;
  end: number;
  confidence?: number;
}

interface TranscriptPanelProps {
  words: Word[];
  currentTime: number;
  onSeek?: (timestamp: number) => void;
}

export const TranscriptPanel: React.FC<TranscriptPanelProps> = ({
  words,
  currentTime,
  onSeek
}) => {
  const [hoveredWordIndex, setHoveredWordIndex] = useState<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const activeWordRef = useRef<HTMLSpanElement>(null);

  // Auto-scroll to current word
  useEffect(() => {
    if (activeWordRef.current && containerRef.current) {
      const container = containerRef.current;
      const activeWord = activeWordRef.current;
      
      const containerRect = container.getBoundingClientRect();
      const wordRect = activeWord.getBoundingClientRect();
      
      // Check if word is outside viewport
      if (wordRect.top < containerRect.top || wordRect.bottom > containerRect.bottom) {
        activeWord.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, [currentTime]);

  // Find active word based on current time
  const activeWordIndex = words.findIndex(
    (word) => currentTime >= word.start && currentTime < word.end
  );

  const handleWordClick = (word: Word) => {
    if (onSeek) {
      onSeek(word.start);
    }
  };

  const formatTimestamp = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = (seconds % 60).toFixed(2);
    return `${mins}:${secs.padStart(5, '0')}`;
  };

  return (
    <div
      ref={containerRef}
      style={{
        backgroundColor: '#1D1D20',
        color: '#fbfbff',
        padding: '24px',
        borderRadius: '8px',
        maxHeight: '500px',
        overflowY: 'auto',
        fontFamily: 'system-ui, -apple-system, sans-serif',
        lineHeight: '1.8',
        fontSize: '16px'
      }}
    >
      <h2 style={{ 
        marginTop: 0, 
        marginBottom: '16px',
        fontSize: '20px',
        fontWeight: 600,
        color: '#fbfbff'
      }}>
        📝 Transcript
      </h2>

      <div style={{ position: 'relative' }}>
        {words.map((word, index) => {
          const isActive = index === activeWordIndex;
          const isHovered = index === hoveredWordIndex;

          return (
            <React.Fragment key={index}>
              <span
                ref={isActive ? activeWordRef : null}
                onMouseEnter={() => setHoveredWordIndex(index)}
                onMouseLeave={() => setHoveredWordIndex(null)}
                onClick={() => handleWordClick(word)}
                style={{
                  backgroundColor: isActive ? '#ffd400' : isHovered ? '#A1C9F4' : 'transparent',
                  color: isActive || isHovered ? '#1D1D20' : '#fbfbff',
                  padding: '2px 4px',
                  borderRadius: '3px',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  fontWeight: isActive ? 600 : 400,
                  position: 'relative',
                  display: 'inline-block'
                }}
                title={`${formatTimestamp(word.start)} - ${formatTimestamp(word.end)}`}
              >
                {word.word}
                
                {/* Timestamp tooltip on hover */}
                {isHovered && (
                  <span style={{
                    position: 'absolute',
                    bottom: '100%',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    backgroundColor: '#1D1D20',
                    color: '#fbfbff',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    whiteSpace: 'nowrap',
                    marginBottom: '4px',
                    border: '1px solid #909094',
                    zIndex: 1000,
                    pointerEvents: 'none'
                  }}>
                    {formatTimestamp(word.start)}
                  </span>
                )}
              </span>
              {' '}
            </React.Fragment>
          );
        })}
      </div>

      <div style={{
        marginTop: '16px',
        paddingTop: '16px',
        borderTop: '1px solid #909094',
        fontSize: '13px',
        color: '#909094'
      }}>
        <p style={{ margin: 0 }}>
          💡 <strong>Hover</strong> over words to see timestamps • <strong>Click</strong> words to jump to that moment
        </p>
      </div>
    </div>
  );
};

export default TranscriptPanel;
'''

print("=" * 70)
print("✅ TRANSCRIPT PANEL COMPONENT CREATED")
print("=" * 70)

print("\n📦 Component: TranscriptPanel")
print("-" * 70)
print("\n🎯 Key Features:")
print("  • Word-level timestamp display on hover")
print("  • Auto-scroll to current word during playback")
print("  • Click any word to seek to that timestamp")
print("  • Visual highlighting of active word (yellow)")
print("  • Hover preview with timestamp tooltip")
print("  • Professional styling with Zerve design system")

print("\n📋 Props Interface:")
print("""
  interface TranscriptPanelProps {
    words: Word[];          // Array of word objects with timestamps
    currentTime: number;    // Current playback time in seconds
    onSeek?: (timestamp: number) => void;  // Callback for seeking
  }

  interface Word {
    word: string;      // The word text
    start: number;     // Start timestamp (seconds)
    end: number;       // End timestamp (seconds)
    confidence?: number;  // Optional confidence score
  }
""")

print("\n🎨 Styling:")
print("  • Background: #1D1D20 (Zerve dark)")
print("  • Text: #fbfbff (primary)")
print("  • Active word: #ffd400 (yellow highlight)")
print("  • Hover: #A1C9F4 (light blue)")
print("  • Smooth transitions and scroll behavior")

print("\n💫 Interactions:")
print("  • Auto-scrolls to keep active word visible")
print("  • Hover shows timestamp tooltip above word")
print("  • Click triggers onSeek callback")
print("  • Tooltip format: M:SS.SS")

print("\n🔧 Usage Example:")
print("""
  import { TranscriptPanel } from './TranscriptPanel';

  const words = [
    { word: "Hello", start: 0.0, end: 0.5 },
    { word: "world", start: 0.5, end: 1.0 },
    // ... more words
  ];

  <TranscriptPanel
    words={words}
    currentTime={audioCurrentTime}
    onSeek={(time) => audioRef.current.currentTime = time}
  />
""")

print("\n" + "=" * 70)
print("📄 Component code saved to variable: transcript_panel_code")
print("=" * 70)
