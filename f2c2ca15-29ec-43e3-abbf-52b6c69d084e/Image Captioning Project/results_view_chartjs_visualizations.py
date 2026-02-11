"""
ResultsView Component with Chart.js Visualizations
Comprehensive charts: Radar (rubric scores), Bar (fillers by minute), Line (WPM over time), Pie (emotion distribution)
"""

results_view_typescript = """
import React, { useEffect, useRef } from 'react';
import { Chart, ChartConfiguration, registerables } from 'chart.js';

// Register Chart.js components
Chart.register(...registerables);

interface ResultsViewProps {
  sessionData: SessionData;
}

interface SessionData {
  rubricScores: RubricScores;
  fillersByMinute: FillersByMinute[];
  wpmOverTime: WPMDataPoint[];
  emotionDistribution: EmotionDistribution;
}

interface RubricScores {
  clarity: number;
  pace: number;
  confidence: number;
  engagement: number;
  structure: number;
}

interface FillersByMinute {
  minute: number;
  count: number;
}

interface WPMDataPoint {
  timestamp: number;
  wpm: number;
}

interface EmotionDistribution {
  neutral: number;
  happy: number;
  sad: number;
  angry: number;
  surprised: number;
  fearful: number;
  disgusted: number;
}

export const ResultsView: React.FC<ResultsViewProps> = ({ sessionData }) => {
  const radarChartRef = useRef<HTMLCanvasElement>(null);
  const barChartRef = useRef<HTMLCanvasElement>(null);
  const lineChartRef = useRef<HTMLCanvasElement>(null);
  const pieChartRef = useRef<HTMLCanvasElement>(null);

  const radarChartInstance = useRef<Chart | null>(null);
  const barChartInstance = useRef<Chart | null>(null);
  const lineChartInstance = useRef<Chart | null>(null);
  const pieChartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    // Cleanup previous charts
    if (radarChartInstance.current) radarChartInstance.current.destroy();
    if (barChartInstance.current) barChartInstance.current.destroy();
    if (lineChartInstance.current) lineChartInstance.current.destroy();
    if (pieChartInstance.current) pieChartInstance.current.destroy();

    // Radar Chart: Rubric Scores
    if (radarChartRef.current) {
      const ctx = radarChartRef.current.getContext('2d');
      if (ctx) {
        const radarConfig: ChartConfiguration<'radar'> = {
          type: 'radar',
          data: {
            labels: ['Clarity', 'Pace', 'Confidence', 'Engagement', 'Structure'],
            datasets: [{
              label: 'Performance Scores',
              data: [
                sessionData.rubricScores.clarity,
                sessionData.rubricScores.pace,
                sessionData.rubricScores.confidence,
                sessionData.rubricScores.engagement,
                sessionData.rubricScores.structure
              ],
              backgroundColor: 'rgba(161, 201, 244, 0.2)',
              borderColor: '#A1C9F4',
              borderWidth: 2,
              pointBackgroundColor: '#A1C9F4',
              pointBorderColor: '#fff',
              pointHoverBackgroundColor: '#fff',
              pointHoverBorderColor: '#A1C9F4'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
              r: {
                beginAtZero: true,
                max: 10,
                ticks: {
                  stepSize: 2,
                  color: '#909094'
                },
                grid: {
                  color: '#3a3a3f'
                },
                pointLabels: {
                  color: '#fbfbff',
                  font: {
                    size: 12
                  }
                }
              }
            },
            plugins: {
              legend: {
                display: true,
                position: 'top',
                labels: {
                  color: '#fbfbff'
                }
              },
              title: {
                display: true,
                text: 'Performance Rubric Scores',
                color: '#fbfbff',
                font: {
                  size: 16,
                  weight: 'bold'
                }
              }
            }
          }
        };
        radarChartInstance.current = new Chart(ctx, radarConfig);
      }
    }

    // Bar Chart: Fillers by Minute
    if (barChartRef.current) {
      const ctx = barChartRef.current.getContext('2d');
      if (ctx) {
        const barConfig: ChartConfiguration<'bar'> = {
          type: 'bar',
          data: {
            labels: sessionData.fillersByMinute.map(d => `Min ${d.minute}`),
            datasets: [{
              label: 'Filler Words',
              data: sessionData.fillersByMinute.map(d => d.count),
              backgroundColor: '#FFB482',
              borderColor: '#FFB482',
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  color: '#909094',
                  stepSize: 1
                },
                grid: {
                  color: '#3a3a3f'
                },
                title: {
                  display: true,
                  text: 'Count',
                  color: '#fbfbff'
                }
              },
              x: {
                ticks: {
                  color: '#909094'
                },
                grid: {
                  display: false
                },
                title: {
                  display: true,
                  text: 'Time',
                  color: '#fbfbff'
                }
              }
            },
            plugins: {
              legend: {
                display: true,
                labels: {
                  color: '#fbfbff'
                }
              },
              title: {
                display: true,
                text: 'Filler Words Per Minute',
                color: '#fbfbff',
                font: {
                  size: 16,
                  weight: 'bold'
                }
              }
            }
          }
        };
        barChartInstance.current = new Chart(ctx, barConfig);
      }
    }

    // Line Chart: WPM Over Time
    if (lineChartRef.current) {
      const ctx = lineChartRef.current.getContext('2d');
      if (ctx) {
        const lineConfig: ChartConfiguration<'line'> = {
          type: 'line',
          data: {
            labels: sessionData.wpmOverTime.map((d, i) => `${Math.floor(d.timestamp / 60)}:${(d.timestamp % 60).toString().padStart(2, '0')}`),
            datasets: [{
              label: 'Words Per Minute',
              data: sessionData.wpmOverTime.map(d => d.wpm),
              borderColor: '#8DE5A1',
              backgroundColor: 'rgba(141, 229, 161, 0.1)',
              borderWidth: 2,
              fill: true,
              tension: 0.4,
              pointRadius: 3,
              pointBackgroundColor: '#8DE5A1'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
              y: {
                beginAtZero: false,
                ticks: {
                  color: '#909094'
                },
                grid: {
                  color: '#3a3a3f'
                },
                title: {
                  display: true,
                  text: 'WPM',
                  color: '#fbfbff'
                }
              },
              x: {
                ticks: {
                  color: '#909094',
                  maxRotation: 45,
                  minRotation: 0
                },
                grid: {
                  display: false
                },
                title: {
                  display: true,
                  text: 'Time (mm:ss)',
                  color: '#fbfbff'
                }
              }
            },
            plugins: {
              legend: {
                display: true,
                labels: {
                  color: '#fbfbff'
                }
              },
              title: {
                display: true,
                text: 'Speaking Pace Over Time',
                color: '#fbfbff',
                font: {
                  size: 16,
                  weight: 'bold'
                }
              }
            }
          }
        };
        lineChartInstance.current = new Chart(ctx, lineConfig);
      }
    }

    // Pie Chart: Emotion Distribution
    if (pieChartRef.current) {
      const ctx = pieChartRef.current.getContext('2d');
      if (ctx) {
        const emotions = sessionData.emotionDistribution;
        const pieConfig: ChartConfiguration<'pie'> = {
          type: 'pie',
          data: {
            labels: ['Neutral', 'Happy', 'Sad', 'Angry', 'Surprised', 'Fearful', 'Disgusted'],
            datasets: [{
              data: [
                emotions.neutral,
                emotions.happy,
                emotions.sad,
                emotions.angry,
                emotions.surprised,
                emotions.fearful,
                emotions.disgusted
              ],
              backgroundColor: [
                '#A1C9F4',  // Neutral - light blue
                '#8DE5A1',  // Happy - green
                '#FF9F9B',  // Sad - coral
                '#FFB482',  // Angry - orange
                '#D0BBFF',  // Surprised - lavender
                '#9467BD',  // Fearful - purple
                '#C49C94'   // Disgusted - brown
              ],
              borderColor: '#1D1D20',
              borderWidth: 2
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
              legend: {
                display: true,
                position: 'right',
                labels: {
                  color: '#fbfbff',
                  padding: 15,
                  font: {
                    size: 11
                  }
                }
              },
              title: {
                display: true,
                text: 'Emotion Distribution',
                color: '#fbfbff',
                font: {
                  size: 16,
                  weight: 'bold'
                }
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    const label = context.label || '';
                    const value = context.parsed || 0;
                    const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
                    const percentage = ((value / total) * 100).toFixed(1);
                    return `${label}: ${percentage}%`;
                  }
                }
              }
            }
          }
        };
        pieChartInstance.current = new Chart(ctx, pieConfig);
      }
    }

    // Cleanup on unmount
    return () => {
      if (radarChartInstance.current) radarChartInstance.current.destroy();
      if (barChartInstance.current) barChartInstance.current.destroy();
      if (lineChartInstance.current) lineChartInstance.current.destroy();
      if (pieChartInstance.current) pieChartInstance.current.destroy();
    };
  }, [sessionData]);

  return (
    <div className="results-view bg-[#1D1D20] p-8 rounded-lg">
      <h2 className="text-3xl font-bold text-[#fbfbff] mb-8">Session Results</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Radar Chart */}
        <div className="chart-container bg-gray-800 p-6 rounded-lg">
          <canvas ref={radarChartRef} />
        </div>

        {/* Bar Chart */}
        <div className="chart-container bg-gray-800 p-6 rounded-lg">
          <canvas ref={barChartRef} />
        </div>

        {/* Line Chart */}
        <div className="chart-container bg-gray-800 p-6 rounded-lg">
          <canvas ref={lineChartRef} />
        </div>

        {/* Pie Chart */}
        <div className="chart-container bg-gray-800 p-6 rounded-lg">
          <canvas ref={pieChartRef} />
        </div>
      </div>
    </div>
  );
};
"""

print("✅ ResultsView Component with Chart.js Visualizations Created")
print("\n📊 Charts included:")
print("  1. Radar Chart - Performance Rubric Scores (Clarity, Pace, Confidence, Engagement, Structure)")
print("  2. Bar Chart - Filler Words Per Minute (time-series distribution)")
print("  3. Line Chart - Speaking Pace Over Time (WPM trend with smooth curves)")
print("  4. Pie Chart - Emotion Distribution (7 emotions with percentage tooltips)")
print("\n✨ Features:")
print("  - Real-time chart updates via sessionData prop")
print("  - Proper cleanup on unmount (prevents memory leaks)")
print("  - Zerve design system colors (#1D1D20 bg, #fbfbff text, #909094 secondary)")
print("  - Responsive 2x2 grid layout")
print("  - Professional styling with dark theme")
print("  - Interactive tooltips and legends")
