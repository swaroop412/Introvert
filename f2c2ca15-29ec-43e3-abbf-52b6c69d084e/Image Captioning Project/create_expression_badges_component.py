print("=" * 80)
print("ORATORIQ - REAL-TIME EXPRESSION BADGES OVERLAY")
print("=" * 80)

import os

components_dir = "oratoriq/client/src/components"
os.makedirs(components_dir, exist_ok=True)

# ============================================================================
# ExpressionBadges Component - Real-time overlay on video
# ============================================================================
expression_badges = """import React from 'react';
import { FaceDetectionResult } from '../../../shared/types';

interface ExpressionBadgesProps {
  detection: FaceDetectionResult | null;
  className?: string;
}

export const ExpressionBadges: React.FC<ExpressionBadgesProps> = ({ 
  detection, 
  className = '' 
}) => {
  if (!detection || !detection.detected) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <div className="px-3 py-1 bg-gray-700 bg-opacity-80 rounded-full text-gray-300 text-sm font-medium">
          No face detected
        </div>
      </div>
    );
  }

  const { expressions, attentionScore } = detection;

  // Get top 3 expressions
  const expressionEntries = Object.entries(expressions)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3);

  // Expression emoji mapping
  const emojiMap: Record<string, string> = {
    neutral: '😐',
    happy: '😊',
    sad: '😢',
    angry: '😠',
    fearful: '😨',
    disgusted: '🤢',
    surprised: '😲',
  };

  // Color mapping based on expression
  const colorMap: Record<string, string> = {
    neutral: 'bg-gray-600',
    happy: 'bg-green-600',
    sad: 'bg-blue-600',
    angry: 'bg-red-600',
    fearful: 'bg-purple-600',
    disgusted: 'bg-yellow-600',
    surprised: 'bg-orange-600',
  };

  // Attention color
  const getAttentionColor = (score: number): string => {
    if (score >= 0.7) return 'bg-green-600';
    if (score >= 0.4) return 'bg-yellow-600';
    return 'bg-red-600';
  };

  return (
    <div className={`flex flex-wrap items-center gap-2 ${className}`}>
      {/* Top expressions */}
      {expressionEntries.map(([expression, confidence]) => (
        <div
          key={expression}
          className={`px-3 py-1 ${colorMap[expression] || 'bg-gray-600'} bg-opacity-90 rounded-full text-white text-sm font-medium flex items-center gap-2 shadow-lg`}
        >
          <span className="text-base">{emojiMap[expression] || '😐'}</span>
          <span className="capitalize">{expression}</span>
          <span className="text-xs opacity-75">
            {Math.round(confidence * 100)}%
          </span>
        </div>
      ))}
      
      {/* Attention score badge */}
      <div
        className={`px-3 py-1 ${getAttentionColor(attentionScore)} bg-opacity-90 rounded-full text-white text-sm font-medium flex items-center gap-2 shadow-lg`}
      >
        <span className="text-base">👁️</span>
        <span>Attention</span>
        <span className="text-xs opacity-75">
          {Math.round(attentionScore * 100)}%
        </span>
      </div>
    </div>
  );
};

// Compact version for smaller overlay
export const ExpressionBadgesCompact: React.FC<ExpressionBadgesProps> = ({ 
  detection, 
  className = '' 
}) => {
  if (!detection || !detection.detected) {
    return (
      <div className={`inline-flex items-center gap-1 ${className}`}>
        <span className="text-gray-400 text-xs">No face</span>
      </div>
    );
  }

  const { expressions, attentionScore } = detection;

  // Get dominant expression
  const dominantExpression = Object.entries(expressions)
    .sort(([, a], [, b]) => b - a)[0];

  const emojiMap: Record<string, string> = {
    neutral: '😐',
    happy: '😊',
    sad: '😢',
    angry: '😠',
    fearful: '😨',
    disgusted: '🤢',
    surprised: '😲',
  };

  const colorMap: Record<string, string> = {
    neutral: 'bg-gray-600',
    happy: 'bg-green-600',
    sad: 'bg-blue-600',
    angry: 'bg-red-600',
    fearful: 'bg-purple-600',
    disgusted: 'bg-yellow-600',
    surprised: 'bg-orange-600',
  };

  const getAttentionColor = (score: number): string => {
    if (score >= 0.7) return 'text-green-400';
    if (score >= 0.4) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className={`inline-flex items-center gap-2 ${className}`}>
      {/* Dominant expression */}
      <div
        className={`px-2 py-0.5 ${colorMap[dominantExpression[0]] || 'bg-gray-600'} bg-opacity-90 rounded-full text-white text-xs font-medium flex items-center gap-1 shadow-md`}
      >
        <span>{emojiMap[dominantExpression[0]] || '😐'}</span>
        <span className="opacity-75">{Math.round(dominantExpression[1] * 100)}%</span>
      </div>
      
      {/* Attention icon */}
      <span className={`text-lg ${getAttentionColor(attentionScore)}`}>
        👁️
      </span>
    </div>
  );
};
"""

badges_path = os.path.join(components_dir, "ExpressionBadges.tsx")
with open(badges_path, 'w') as f:
    f.write(expression_badges)

print(f"\n✓ Created {badges_path}")

print("\n" + "=" * 80)
print("EXPRESSION BADGES COMPONENT CREATED")
print("=" * 80)
print("\n✅ Features:")
print("  • Real-time expression badges with emoji + percentage")
print("  • Top 3 expressions displayed with color coding")
print("  • Attention score badge with eye icon")
print("  • Compact variant for minimal overlay")
print("  • Color-coded by emotion (green=happy, red=angry, etc.)")
print("  • 'No face detected' fallback")
print("  • Professional styling with Tailwind CSS")
print("\n🎨 Visual design:")
print("  • Rounded badge pills with semi-transparent backgrounds")
print("  • Expression emoji for quick recognition")
print("  • Percentage confidence display")
print("  • Color-coded attention score (green>70%, yellow>40%, red<40%)")
print("\n🎯 Ticket requirement:")
print("  ✓ Real-time expression badges overlay")

expression_badges_created = True
print(f"\n📄 Component saved: {badges_path}")
