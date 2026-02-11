// OratorIQ Unified Timeline System - Vanilla JS
// Session-relative timestamps (ms) + align() query utility

class UnifiedTimeline {
  constructor() {
    this.timeline_events = [];
    this.session_start = null;
  }

  toRelativeMs(timestamp) {
    if (this.session_start === null) {
      this.session_start = timestamp;
      return 0;
    }
    return timestamp - this.session_start;
  }

  addExpression(timestamp, expression, confidence, allExpressions, attentionScore) {
    this.timeline_events.push({
      timestamp_ms: this.toRelativeMs(timestamp),
      type: 'expression',
      expression,
      confidence,
      all_expressions: allExpressions,
      attention_score: attentionScore
    });
  }

  addTranscript(timestamp, text, isFinal = false) {
    this.timeline_events.push({
      timestamp_ms: this.toRelativeMs(timestamp),
      type: 'transcript',
      text,
      is_final: isFinal
    });
  }

  addFiller(timestamp, word, text) {
    this.timeline_events.push({
      timestamp_ms: this.toRelativeMs(timestamp),
      type: 'filler',
      word,
      text
    });
  }

  addPause(timestampStart, timestampEnd, durationMs) {
    this.timeline_events.push({
      timestamp_ms: this.toRelativeMs(timestampStart),
      type: 'pause',
      duration_ms: durationMs,
      end_ms: this.toRelativeMs(timestampEnd)
    });
  }

  addWPM(timestamp, wpm, wordCount, durationS, status) {
    this.timeline_events.push({
      timestamp_ms: this.toRelativeMs(timestamp),
      type: 'wpm',
      wpm,
      word_count: wordCount,
      duration_s: durationS,
      status
    });
  }

  align(tStartMs, tEndMs) {
    const sortedEvents = [...this.timeline_events].sort((a, b) => a.timestamp_ms - b.timestamp_ms);
    const sliceEvents = sortedEvents.filter(
      e => tStartMs <= e.timestamp_ms && e.timestamp_ms <= tEndMs
    );

    const result = {
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

    const exprCounts = {};
    const exprConfidences = {};
    const attentionVals = [];
    const wpmVals = [];

    for (const e of sliceEvents) {
      if (e.type === 'expression') {
        const expr = e.expression;
        exprCounts[expr] = (exprCounts[expr] || 0) + 1;
        if (!exprConfidences[expr]) exprConfidences[expr] = [];
        exprConfidences[expr].push(e.confidence);
        attentionVals.push(e.attention_score);
      } else if (e.type === 'wpm') {
        wpmVals.push(e.wpm);
      } else if (e.type === 'filler') {
        const fe = e;
        result.fillers.push({ timestamp_ms: e.timestamp_ms, word: fe.word, text: fe.text });
      } else if (e.type === 'pause') {
        const pe = e;
        result.pauses.push({ 
          timestamp_ms: e.timestamp_ms, 
          duration_ms: pe.duration_ms, 
          end_ms: pe.end_ms 
        });
      } else if (e.type === 'transcript') {
        const te = e;
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

  exportSession() {
    const sortedEvents = [...this.timeline_events].sort((a, b) => a.timestamp_ms - b.timestamp_ms);
    const durationMs = sortedEvents.length > 0 
      ? Math.max(...sortedEvents.map(e => e.timestamp_ms)) 
      : 0;

    const counts = {};
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

  getSessionStartTime() {
    return this.session_start;
  }

  getAllEvents() {
    return [...this.timeline_events].sort((a, b) => a.timestamp_ms - b.timestamp_ms);
  }

  clear() {
    this.timeline_events = [];
    this.session_start = null;
  }
}