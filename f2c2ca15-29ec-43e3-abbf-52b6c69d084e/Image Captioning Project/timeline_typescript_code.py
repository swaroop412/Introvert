"""Generate TypeScript/JavaScript timeline system for frontend integration"""

typescript_code = """
// OratorIQ Unified Timeline System - TypeScript/JavaScript
// Session-relative timestamps (ms) + align() query utility

export interface TimelineEvent {
  timestamp_ms: number;
  type: 'expression' | 'transcript' | 'filler' | 'pause' | 'wpm';
  [key: string]: any;
}

export interface ExpressionEvent extends TimelineEvent {
  type: 'expression';
  expression: string;
  confidence: number;
  all_expressions: Record<string, number>;
  attention_score: number;
}

export interface TranscriptEvent extends TimelineEvent {
  type: 'transcript';
  text: string;
  is_final: boolean;
}

export interface FillerEvent extends TimelineEvent {
  type: 'filler';
  word: string;
  text: string;
}

export interface PauseEvent extends TimelineEvent {
  type: 'pause';
  duration_ms: number;
  end_ms: number;
}

export interface WPMEvent extends TimelineEvent {
  type: 'wpm';
  wpm: number;
  word_count: number;
  duration_s: number;
  status: 'optimal' | 'too_slow' | 'too_fast';
}

export interface AlignResult {
  time_slice: {
    start_ms: number;
    end_ms: number;
    duration_ms: number;
  };
  dominant_expression: {
    expression: string;
    count: number;
    avg_confidence: number;
  } | null;
  wpm_avg: number | null;
  fillers: Array<{timestamp_ms: number; word: string; text: string}>;
  pauses: Array<{timestamp_ms: number; duration_ms: number; end_ms: number}>;
  transcripts: Array<{timestamp_ms: number; text: string; is_final: boolean}>;
  expression_distribution: Record<string, number>;
  attention_avg: number | null;
  total_events: number;
}

export interface SessionExport {
  session_metadata: {
    session_start_time: number;
    duration_ms: number;
    total_events: number;
    event_counts: Record<string, number>;
  };
  events: TimelineEvent[];
}

export class UnifiedTimeline {
  private timeline_events: TimelineEvent[] = [];
  private session_start: number | null = null;

  private toRelativeMs(timestamp: number): number {
    if (this.session_start === null) {
      this.session_start = timestamp;
      return 0;
    }
    return timestamp - this.session_start;
  }

  addExpression(
    timestamp: number,
    expression: string,
    confidence: number,
    allExpressions: Record<string, number>,
    attentionScore: number
  ): void {
    this.timeline_events.push({
      timestamp_ms: this.toRelativeMs(timestamp),
      type: 'expression',
      expression,
      confidence,
      all_expressions: allExpressions,
      attention_score: attentionScore
    } as ExpressionEvent);
  }

  addTranscript(timestamp: number, text: string, isFinal: boolean = false): void {
    this.timeline_events.push({
      timestamp_ms: this.toRelativeMs(timestamp),
      type: 'transcript',
      text,
      is_final: isFinal
    } as TranscriptEvent);
  }

  addFiller(timestamp: number, word: string, text: string): void {
    this.timeline_events.push({
      timestamp_ms: this.toRelativeMs(timestamp),
      type: 'filler',
      word,
      text
    } as FillerEvent);
  }

  addPause(timestampStart: number, timestampEnd: number, durationMs: number): void {
    this.timeline_events.push({
      timestamp_ms: this.toRelativeMs(timestampStart),
      type: 'pause',
      duration_ms: durationMs,
      end_ms: this.toRelativeMs(timestampEnd)
    } as PauseEvent);
  }

  addWPM(
    timestamp: number,
    wpm: number,
    wordCount: number,
    durationS: number,
    status: 'optimal' | 'too_slow' | 'too_fast'
  ): void {
    this.timeline_events.push({
      timestamp_ms: this.toRelativeMs(timestamp),
      type: 'wpm',
      wpm,
      word_count: wordCount,
      duration_s: durationS,
      status
    } as WPMEvent);
  }

  align(tStartMs: number, tEndMs: number): AlignResult {
    const sortedEvents = [...this.timeline_events].sort((a, b) => a.timestamp_ms - b.timestamp_ms);
    const sliceEvents = sortedEvents.filter(
      e => tStartMs <= e.timestamp_ms && e.timestamp_ms <= tEndMs
    );

    const result: AlignResult = {
      time_slice: { start_ms: tStartMs, end_ms: tEndMs, duration_ms: tEndMs - tStartMs },
      dominant_expression: null,
      wpm_avg: null,
      fillers: [],
      pauses: [],
      transcripts: [],
      expression_distribution: {},
      attention_avg: null,
      total_events: sliceEvents.length
    };

    const exprCounts: Record<string, number> = {};
    const exprConfidences: Record<string, number[]> = {};
    const attentionVals: number[] = [];
    const wpmVals: number[] = [];

    for (const e of sliceEvents) {
      if (e.type === 'expression') {
        const expr = (e as ExpressionEvent).expression;
        exprCounts[expr] = (exprCounts[expr] || 0) + 1;
        if (!exprConfidences[expr]) exprConfidences[expr] = [];
        exprConfidences[expr].push((e as ExpressionEvent).confidence);
        attentionVals.push((e as ExpressionEvent).attention_score);
      } else if (e.type === 'wpm') {
        wpmVals.push((e as WPMEvent).wpm);
      } else if (e.type === 'filler') {
        const fe = e as FillerEvent;
        result.fillers.push({ timestamp_ms: e.timestamp_ms, word: fe.word, text: fe.text });
      } else if (e.type === 'pause') {
        const pe = e as PauseEvent;
        result.pauses.push({ 
          timestamp_ms: e.timestamp_ms, 
          duration_ms: pe.duration_ms, 
          end_ms: pe.end_ms 
        });
      } else if (e.type === 'transcript') {
        const te = e as TranscriptEvent;
        result.transcripts.push({ 
          timestamp_ms: e.timestamp_ms, 
          text: te.text, 
          is_final: te.is_final 
        });
      }
    }

    if (Object.keys(exprCounts).length > 0) {
      const dominant = Object.entries(exprCounts).reduce((a, b) => b[1] > a[1] ? b : a)[0];
      result.dominant_expression = {
        expression: dominant,
        count: exprCounts[dominant],
        avg_confidence: exprConfidences[dominant].reduce((a, b) => a + b, 0) / exprConfidences[dominant].length
      };
      result.expression_distribution = exprCounts;
    }

    if (wpmVals.length > 0) {
      result.wpm_avg = wpmVals.reduce((a, b) => a + b, 0) / wpmVals.length;
    }

    if (attentionVals.length > 0) {
      result.attention_avg = attentionVals.reduce((a, b) => a + b, 0) / attentionVals.length;
    }

    return result;
  }

  exportSession(): SessionExport {
    const sortedEvents = [...this.timeline_events].sort((a, b) => a.timestamp_ms - b.timestamp_ms);
    const durationMs = sortedEvents.length > 0 
      ? Math.max(...sortedEvents.map(e => e.timestamp_ms)) 
      : 0;

    const counts: Record<string, number> = {};
    for (const e of sortedEvents) {
      counts[e.type] = (counts[e.type] || 0) + 1;
    }

    return {
      session_metadata: {
        session_start_time: this.session_start || 0,
        duration_ms: durationMs,
        total_events: sortedEvents.length,
        event_counts: counts
      },
      events: sortedEvents
    };
  }

  getSessionStartTime(): number | null {
    return this.session_start;
  }

  getAllEvents(): TimelineEvent[] {
    return [...this.timeline_events].sort((a, b) => a.timestamp_ms - b.timestamp_ms);
  }

  clear(): void {
    this.timeline_events = [];
    this.session_start = null;
  }
}

// Example usage:
// const timeline = new UnifiedTimeline();
// timeline.addExpression(Date.now(), 'happy', 0.85, {happy: 0.85, neutral: 0.15}, 0.92);
// timeline.addTranscript(Date.now(), "Hello world", true);
// const result = timeline.align(0, 5000);
// const session = timeline.exportSession();
"""

print("=" * 70)
print("TYPESCRIPT/JAVASCRIPT TIMELINE IMPLEMENTATION")
print("=" * 70)

print("\n✅ Generated TypeScript timeline system for frontend")
print("\n📋 Features:")
print("  • Full TypeScript types and interfaces")
print("  • Class-based API matching Python version")
print("  • Session-relative timestamps")
print("  • align() query utility")
print("  • exportSession() for JSON export")
print("  • Helper methods: getSessionStartTime(), getAllEvents(), clear()")

print("\n🔧 Integration points:")
print("  1. Import into React components")
print("  2. Connect to useFaceAPI hook for expression events")
print("  3. Connect to STT pipeline for transcript events")
print("  4. Connect to disfluency detector for filler/pause/WPM")
print("  5. Export session.json on session end")

print("\n📁 Save to: oratoriq/client/src/lib/UnifiedTimeline.ts")

print("\n" + "=" * 70)
print("CODE OUTPUT")
print("=" * 70)
print(typescript_code)

typescript_timeline_code = typescript_code
