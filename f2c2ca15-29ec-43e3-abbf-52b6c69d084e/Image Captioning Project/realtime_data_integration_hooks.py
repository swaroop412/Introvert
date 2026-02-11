"""
Real-time Data Integration Hooks for OratorIQ
Custom React hooks to update metrics and charts in real-time
"""

realtime_hooks_typescript = """
import { useState, useEffect, useCallback } from 'react';

// Custom hook for real-time metrics updates
export const useRealtimeMetrics = () => {
  const [metrics, setMetrics] = useState({
    wpm: { current: 0, average: 0 },
    fillers: { perMinute: 0, total: 0, duration: 0 },
    pauses: { average: 0, total: 0, longest: 0 },
    expression: { dominant: 'neutral', confidence: 0, percentage: 0, emoji: '😐' }
  });

  // Update WPM
  const updateWPM = useCallback((currentWPM: number, averageWPM: number) => {
    setMetrics(prev => ({
      ...prev,
      wpm: { current: currentWPM, average: averageWPM }
    }));
  }, []);

  // Update filler words
  const updateFillers = useCallback((fillersPerMinute: number, totalFillers: number, duration: number) => {
    setMetrics(prev => ({
      ...prev,
      fillers: { perMinute: fillersPerMinute, total: totalFillers, duration }
    }));
  }, []);

  // Update pauses
  const updatePauses = useCallback((averagePause: number, totalPauses: number, longestPause: number) => {
    setMetrics(prev => ({
      ...prev,
      pauses: { average: averagePause, total: totalPauses, longest: longestPause }
    }));
  }, []);

  // Update dominant expression
  const updateExpression = useCallback((expression: string, confidence: number, percentage: number) => {
    const emojiMap: Record<string, string> = {
      neutral: '😐',
      happy: '😊',
      sad: '😢',
      angry: '😠',
      surprised: '😲',
      fearful: '😨',
      disgusted: '🤢'
    };
    
    setMetrics(prev => ({
      ...prev,
      expression: {
        dominant: expression,
        confidence,
        percentage,
        emoji: emojiMap[expression.toLowerCase()] || '😐'
      }
    }));
  }, []);

  return {
    metrics,
    updateWPM,
    updateFillers,
    updatePauses,
    updateExpression
  };
};

// Custom hook for session data (charts)
export const useSessionData = () => {
  const [sessionData, setSessionData] = useState({
    rubricScores: {
      clarity: 0,
      pace: 0,
      confidence: 0,
      engagement: 0,
      structure: 0
    },
    fillersByMinute: [] as { minute: number; count: number }[],
    wpmOverTime: [] as { timestamp: number; wpm: number }[],
    emotionDistribution: {
      neutral: 0,
      happy: 0,
      sad: 0,
      angry: 0,
      surprised: 0,
      fearful: 0,
      disgusted: 0
    }
  });

  // Update rubric scores
  const updateRubricScores = useCallback((scores: {
    clarity: number;
    pace: number;
    confidence: number;
    engagement: number;
    structure: number;
  }) => {
    setSessionData(prev => ({
      ...prev,
      rubricScores: scores
    }));
  }, []);

  // Add filler data point
  const addFillerDataPoint = useCallback((minute: number, count: number) => {
    setSessionData(prev => {
      const updated = [...prev.fillersByMinute];
      const existingIndex = updated.findIndex(d => d.minute === minute);
      
      if (existingIndex >= 0) {
        updated[existingIndex] = { minute, count };
      } else {
        updated.push({ minute, count });
        updated.sort((a, b) => a.minute - b.minute);
      }
      
      return {
        ...prev,
        fillersByMinute: updated
      };
    });
  }, []);

  // Add WPM data point
  const addWPMDataPoint = useCallback((timestamp: number, wpm: number) => {
    setSessionData(prev => ({
      ...prev,
      wpmOverTime: [...prev.wpmOverTime, { timestamp, wpm }]
    }));
  }, []);

  // Update emotion distribution
  const updateEmotionDistribution = useCallback((emotions: {
    neutral: number;
    happy: number;
    sad: number;
    angry: number;
    surprised: number;
    fearful: number;
    disgusted: number;
  }) => {
    setSessionData(prev => ({
      ...prev,
      emotionDistribution: emotions
    }));
  }, []);

  // Reset session data
  const resetSessionData = useCallback(() => {
    setSessionData({
      rubricScores: {
        clarity: 0,
        pace: 0,
        confidence: 0,
        engagement: 0,
        structure: 0
      },
      fillersByMinute: [],
      wpmOverTime: [],
      emotionDistribution: {
        neutral: 0,
        happy: 0,
        sad: 0,
        angry: 0,
        surprised: 0,
        fearful: 0,
        disgusted: 0
      }
    });
  }, []);

  return {
    sessionData,
    updateRubricScores,
    addFillerDataPoint,
    addWPMDataPoint,
    updateEmotionDistribution,
    resetSessionData
  };
};

// Combined hook for the main app
export const useOratorIQData = () => {
  const metricsHook = useRealtimeMetrics();
  const sessionHook = useSessionData();
  
  return {
    ...metricsHook,
    ...sessionHook
  };
};

// Example integration with Zustand store
export const oratorIQStoreSlice = (set: any, get: any) => ({
  // Metrics state
  currentMetrics: {
    wpm: { current: 0, average: 0 },
    fillers: { perMinute: 0, total: 0, duration: 0 },
    pauses: { average: 0, total: 0, longest: 0 },
    expression: { dominant: 'neutral', confidence: 0, percentage: 0, emoji: '😐' }
  },
  
  // Session data state
  sessionData: {
    rubricScores: { clarity: 0, pace: 0, confidence: 0, engagement: 0, structure: 0 },
    fillersByMinute: [],
    wpmOverTime: [],
    emotionDistribution: { neutral: 0, happy: 0, sad: 0, angry: 0, surprised: 0, fearful: 0, disgusted: 0 }
  },
  
  // Actions
  updateMetrics: (metrics: any) => set({ currentMetrics: metrics }),
  updateSessionData: (data: any) => set((state: any) => ({
    sessionData: { ...state.sessionData, ...data }
  })),
  
  // Real-time update handlers
  handleTranscriptUpdate: (transcript: string, timestamp: number) => {
    const state = get();
    // Calculate WPM
    const wordCount = transcript.split(' ').length;
    const minutes = timestamp / 60;
    const wpm = Math.round(wordCount / minutes);
    
    set((state: any) => ({
      currentMetrics: {
        ...state.currentMetrics,
        wpm: { ...state.currentMetrics.wpm, current: wpm }
      }
    }));
  },
  
  handleDisfluencyDetection: (disfluencies: any[]) => {
    const state = get();
    const totalDuration = state.sessionData.wpmOverTime.length > 0 
      ? state.sessionData.wpmOverTime[state.sessionData.wpmOverTime.length - 1].timestamp 
      : 0;
    const fillersPerMinute = (disfluencies.length / (totalDuration / 60)) || 0;
    
    set((state: any) => ({
      currentMetrics: {
        ...state.currentMetrics,
        fillers: {
          perMinute: fillersPerMinute,
          total: disfluencies.length,
          duration: totalDuration
        }
      }
    }));
  },
  
  handleExpressionUpdate: (expression: any) => {
    set((state: any) => ({
      currentMetrics: {
        ...state.currentMetrics,
        expression: {
          dominant: expression.emotion,
          confidence: expression.confidence,
          percentage: expression.percentage,
          emoji: expression.emoji
        }
      }
    }));
  }
});
"""

print("✅ Real-time Data Integration Hooks Created")
print("\n🎣 Custom Hooks:")
print("  - useRealtimeMetrics() - Updates MetricsCards in real-time")
print("  - useSessionData() - Manages chart data updates")
print("  - useOratorIQData() - Combined hook for all data")
print("\n📦 Zustand Store Integration:")
print("  - oratorIQStoreSlice - Store slice with actions")
print("  - handleTranscriptUpdate - WPM calculation")
print("  - handleDisfluencyDetection - Filler words tracking")
print("  - handleExpressionUpdate - Emotion updates")
print("\n✨ Features:")
print("  - Optimized with useCallback for performance")
print("  - Type-safe interfaces")
print("  - Automatic emoji mapping for expressions")
print("  - Real-time data aggregation")
print("  - Chart data accumulation (time-series)")
