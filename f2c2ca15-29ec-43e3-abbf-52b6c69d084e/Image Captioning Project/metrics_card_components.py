"""
MetricsCard Components for OratorIQ
Real-time metrics display: WPM, Filler/min, Avg Pause, Dominant Expression
"""

metrics_card_typescript = """
import React from 'react';

interface MetricsCardProps {
  title: string;
  value: string | number;
  unit?: string;
  icon?: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  className?: string;
}

export const MetricsCard: React.FC<MetricsCardProps> = ({
  title,
  value,
  unit,
  icon,
  trend,
  trendValue,
  className = ''
}) => {
  const getTrendColor = () => {
    if (!trend) return '';
    return trend === 'up' ? 'text-green-500' : trend === 'down' ? 'text-red-500' : 'text-gray-500';
  };

  return (
    <div className={`bg-gray-800 rounded-lg p-6 shadow-lg ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-gray-400 text-sm font-medium">{title}</h3>
        {icon && <div className="text-gray-400">{icon}</div>}
      </div>
      <div className="flex items-baseline">
        <span className="text-3xl font-bold text-white">{value}</span>
        {unit && <span className="ml-2 text-gray-400 text-lg">{unit}</span>}
      </div>
      {trend && trendValue && (
        <div className={`mt-2 flex items-center text-sm ${getTrendColor()}`}>
          <span>{trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}</span>
          <span className="ml-1">{trendValue}</span>
        </div>
      )}
    </div>
  );
};

// WPM Metrics Card
interface WPMMetricsProps {
  currentWPM: number;
  averageWPM: number;
  targetWPM?: number;
}

export const WPMMetrics: React.FC<WPMMetricsProps> = ({ 
  currentWPM, 
  averageWPM, 
  targetWPM = 150 
}) => {
  const trend = currentWPM > averageWPM ? 'up' : currentWPM < averageWPM ? 'down' : 'neutral';
  const trendValue = `${Math.abs(currentWPM - averageWPM).toFixed(0)} from avg`;
  
  return (
    <MetricsCard
      title="Words Per Minute"
      value={currentWPM.toFixed(0)}
      unit="WPM"
      trend={trend}
      trendValue={trendValue}
      icon={<span>⚡</span>}
    />
  );
};

// Filler Words Metrics Card
interface FillerMetricsProps {
  fillersPerMinute: number;
  totalFillers: number;
  duration: number; // in seconds
}

export const FillerMetrics: React.FC<FillerMetricsProps> = ({ 
  fillersPerMinute, 
  totalFillers, 
  duration 
}) => {
  const quality = fillersPerMinute < 2 ? 'up' : fillersPerMinute > 4 ? 'down' : 'neutral';
  
  return (
    <MetricsCard
      title="Filler Words"
      value={fillersPerMinute.toFixed(1)}
      unit="per min"
      trend={quality}
      trendValue={`${totalFillers} total`}
      icon={<span>🗣️</span>}
    />
  );
};

// Pause Metrics Card
interface PauseMetricsProps {
  averagePauseDuration: number; // in seconds
  totalPauses: number;
  longestPause: number;
}

export const PauseMetrics: React.FC<PauseMetricsProps> = ({ 
  averagePauseDuration, 
  totalPauses, 
  longestPause 
}) => {
  const quality = averagePauseDuration < 1.5 ? 'up' : averagePauseDuration > 3 ? 'down' : 'neutral';
  
  return (
    <MetricsCard
      title="Average Pause"
      value={averagePauseDuration.toFixed(1)}
      unit="sec"
      trend={quality}
      trendValue={`${totalPauses} pauses`}
      icon={<span>⏸️</span>}
    />
  );
};

// Dominant Expression Card
interface ExpressionMetricsProps {
  dominantExpression: string;
  confidence: number;
  percentage: number;
  emoji: string;
}

export const ExpressionMetrics: React.FC<ExpressionMetricsProps> = ({ 
  dominantExpression, 
  confidence, 
  percentage,
  emoji 
}) => {
  return (
    <MetricsCard
      title="Dominant Expression"
      value={dominantExpression}
      trendValue={`${percentage.toFixed(0)}% of time`}
      icon={<span className="text-2xl">{emoji}</span>}
    />
  );
};

// Metrics Dashboard Container
interface MetricsDashboardProps {
  wpmData: WPMMetricsProps;
  fillerData: FillerMetricsProps;
  pauseData: PauseMetricsProps;
  expressionData: ExpressionMetricsProps;
}

export const MetricsDashboard: React.FC<MetricsDashboardProps> = ({
  wpmData,
  fillerData,
  pauseData,
  expressionData
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <WPMMetrics {...wpmData} />
      <FillerMetrics {...fillerData} />
      <PauseMetrics {...pauseData} />
      <ExpressionMetrics {...expressionData} />
    </div>
  );
};
"""

print("✅ MetricsCard Components Created")
print("\n📦 Components included:")
print("  - MetricsCard (base component)")
print("  - WPMMetrics (Words Per Minute)")
print("  - FillerMetrics (Filler Words/min)")
print("  - PauseMetrics (Average Pause Duration)")
print("  - ExpressionMetrics (Dominant Expression)")
print("  - MetricsDashboard (container for all metrics)")
print("\n✨ Features:")
print("  - Real-time value updates")
print("  - Trend indicators (up/down/neutral)")
print("  - Icon support")
print("  - Responsive grid layout")
print("  - Dark theme styling")
