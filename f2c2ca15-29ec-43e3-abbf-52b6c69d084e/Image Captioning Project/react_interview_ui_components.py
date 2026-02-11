"""
React Interview Mode UI Components
Domain selector, question panel, timer, Next/Prev navigation, answer display
"""

print("=" * 80)
print("REACT INTERVIEW MODE UI COMPONENTS")
print("=" * 80)

# Domain Selector Component
domain_selector_component = '''
// components/DomainSelector.tsx
import React from 'react';

interface DomainSelectorProps {
  onDomainSelect: (domain: string) => void;
  disabled?: boolean;
}

const DOMAINS = ['DSA', 'Web', 'Python', 'Java', 'System Design'];

export const DomainSelector: React.FC<DomainSelectorProps> = ({ 
  onDomainSelect, 
  disabled = false 
}) => {
  return (
    <div className="domain-selector">
      <h2>Select Interview Domain</h2>
      <div className="domain-grid">
        {DOMAINS.map(domain => (
          <button
            key={domain}
            className="domain-button"
            onClick={() => onDomainSelect(domain)}
            disabled={disabled}
          >
            {domain}
          </button>
        ))}
      </div>
    </div>
  );
};
'''

# Question Display with Timer
question_display_component = '''
// components/QuestionDisplay.tsx
import React, { useEffect, useState } from 'react';

interface QuestionDisplayProps {
  question: {
    id: string;
    question: string;
    difficulty: string;
  };
  questionNumber: number;
  totalQuestions: number;
  startTime: Date;
}

export const QuestionDisplay: React.FC<QuestionDisplayProps> = ({
  question,
  questionNumber,
  totalQuestions,
  startTime
}) => {
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime.getTime()) / 1000);
      setElapsedTime(elapsed);
    }, 1000);

    return () => clearInterval(timer);
  }, [startTime]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getDifficultyColor = (difficulty: string) => {
    switch(difficulty.toLowerCase()) {
      case 'easy': return '#17b26a';
      case 'medium': return '#ffd400';
      case 'hard': return '#f04438';
      default: return '#909094';
    }
  };

  return (
    <div className="question-display">
      <div className="question-header">
        <div className="question-meta">
          <span className="question-number">
            Question {questionNumber} of {totalQuestions}
          </span>
          <span 
            className="difficulty-badge"
            style={{ backgroundColor: getDifficultyColor(question.difficulty) }}
          >
            {question.difficulty}
          </span>
        </div>
        <div className="timer">
          <span className="timer-icon">⏱️</span>
          <span className="timer-value">{formatTime(elapsedTime)}</span>
        </div>
      </div>
      <div className="question-text">
        {question.question}
      </div>
    </div>
  );
};
'''

# Navigation Controls
navigation_component = '''
// components/NavigationControls.tsx
import React from 'react';

interface NavigationControlsProps {
  hasPrevious: boolean;
  hasNext: boolean;
  onPrevious: () => void;
  onNext: () => void;
  onComplete: () => void;
  isLastQuestion: boolean;
}

export const NavigationControls: React.FC<NavigationControlsProps> = ({
  hasPrevious,
  hasNext,
  onPrevious,
  onNext,
  onComplete,
  isLastQuestion
}) => {
  return (
    <div className="navigation-controls">
      <button
        className="nav-button secondary"
        onClick={onPrevious}
        disabled={!hasPrevious}
      >
        ← Previous
      </button>
      
      {isLastQuestion ? (
        <button
          className="nav-button primary complete"
          onClick={onComplete}
        >
          Complete Interview ✓
        </button>
      ) : (
        <button
          className="nav-button primary"
          onClick={onNext}
          disabled={!hasNext}
        >
          Next →
        </button>
      )}
    </div>
  );
};
'''

# Answer Capture with Silence Detection
answer_capture_component = '''
// components/AnswerCapture.tsx
import React, { useState, useEffect, useRef } from 'react';

interface AnswerCaptureProps {
  onAnswerComplete: (transcript: string, autoCompleted: boolean, silenceDuration: number) => void;
  silenceThreshold?: number;
}

export const AnswerCapture: React.FC<AnswerCaptureProps> = ({
  onAnswerComplete,
  silenceThreshold = 4.0
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [lastSpeechTime, setLastSpeechTime] = useState<Date | null>(null);
  const [silenceDuration, setSilenceDuration] = useState(0);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Monitor silence duration
  useEffect(() => {
    if (!isRecording || !lastSpeechTime) return;

    silenceTimerRef.current = setInterval(() => {
      const elapsed = (Date.now() - lastSpeechTime.getTime()) / 1000;
      setSilenceDuration(elapsed);

      // Auto-complete on 4s silence
      if (elapsed >= silenceThreshold) {
        handleAutoComplete();
      }
    }, 100);

    return () => {
      if (silenceTimerRef.current) {
        clearInterval(silenceTimerRef.current);
      }
    };
  }, [isRecording, lastSpeechTime, silenceThreshold]);

  const handleStartRecording = () => {
    setIsRecording(true);
    setTranscript('');
    setLastSpeechTime(new Date());
    setSilenceDuration(0);
  };

  const handleStopRecording = () => {
    setIsRecording(false);
    onAnswerComplete(transcript, false, silenceDuration);
  };

  const handleAutoComplete = () => {
    setIsRecording(false);
    if (silenceTimerRef.current) {
      clearInterval(silenceTimerRef.current);
    }
    onAnswerComplete(transcript, true, silenceDuration);
  };

  const handleTranscriptUpdate = (newText: string) => {
    setTranscript(prev => prev + ' ' + newText);
    setLastSpeechTime(new Date());
    setSilenceDuration(0);
  };

  return (
    <div className="answer-capture">
      <div className="recording-controls">
        {!isRecording ? (
          <button 
            className="record-button start"
            onClick={handleStartRecording}
          >
            🎤 Start Recording
          </button>
        ) : (
          <>
            <button 
              className="record-button stop"
              onClick={handleStopRecording}
            >
              ⏹️ Stop Recording
            </button>
            <div className="recording-indicator">
              <span className="pulse">🔴</span>
              <span>Recording...</span>
            </div>
          </>
        )}
      </div>

      {isRecording && silenceDuration > 0 && (
        <div className="silence-indicator">
          <span>Silence: {silenceDuration.toFixed(1)}s</span>
          {silenceDuration >= 3 && (
            <span className="warning">Auto-completing soon...</span>
          )}
        </div>
      )}

      <div className="transcript-display">
        <h3>Your Answer:</h3>
        <div className="transcript-text">
          {transcript || 'Your answer will appear here...'}
        </div>
      </div>
    </div>
  );
};
'''

# Evaluation Display
evaluation_display_component = '''
// components/EvaluationDisplay.tsx
import React from 'react';

interface Evaluation {
  scores: {
    correctness: number;
    completeness: number;
    clarity: number;
    overall: number;
  };
  feedback: {
    strengths: string[];
    improvements: string[];
    overall: string;
  };
}

interface EvaluationDisplayProps {
  evaluation: Evaluation;
  loading?: boolean;
}

export const EvaluationDisplay: React.FC<EvaluationDisplayProps> = ({
  evaluation,
  loading = false
}) => {
  if (loading) {
    return (
      <div className="evaluation-loading">
        <div className="spinner"></div>
        <p>Evaluating your answer...</p>
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#17b26a';
    if (score >= 60) return '#ffd400';
    return '#f04438';
  };

  return (
    <div className="evaluation-display">
      <h3>Evaluation Results</h3>
      
      <div className="scores-grid">
        <div className="score-card">
          <div className="score-label">Correctness</div>
          <div 
            className="score-value"
            style={{ color: getScoreColor(evaluation.scores.correctness) }}
          >
            {evaluation.scores.correctness}
          </div>
        </div>
        <div className="score-card">
          <div className="score-label">Completeness</div>
          <div 
            className="score-value"
            style={{ color: getScoreColor(evaluation.scores.completeness) }}
          >
            {evaluation.scores.completeness}
          </div>
        </div>
        <div className="score-card">
          <div className="score-label">Clarity</div>
          <div 
            className="score-value"
            style={{ color: getScoreColor(evaluation.scores.clarity) }}
          >
            {evaluation.scores.clarity}
          </div>
        </div>
        <div className="score-card overall">
          <div className="score-label">Overall</div>
          <div 
            className="score-value large"
            style={{ color: getScoreColor(evaluation.scores.overall) }}
          >
            {evaluation.scores.overall}
          </div>
        </div>
      </div>

      <div className="feedback-section">
        <div className="feedback-block strengths">
          <h4>💪 Strengths</h4>
          <ul>
            {evaluation.feedback.strengths.map((strength, idx) => (
              <li key={idx}>{strength}</li>
            ))}
          </ul>
        </div>

        <div className="feedback-block improvements">
          <h4>📈 Areas for Improvement</h4>
          <ul>
            {evaluation.feedback.improvements.map((improvement, idx) => (
              <li key={idx}>{improvement}</li>
            ))}
          </ul>
        </div>

        <div className="feedback-block overall">
          <h4>Overall Feedback</h4>
          <p>{evaluation.feedback.overall}</p>
        </div>
      </div>
    </div>
  );
};
'''

# Main Interview Container
interview_container = '''
// components/InterviewContainer.tsx
import React, { useState, useEffect } from 'react';
import { DomainSelector } from './DomainSelector';
import { QuestionDisplay } from './QuestionDisplay';
import { AnswerCapture } from './AnswerCapture';
import { NavigationControls } from './NavigationControls';
import { EvaluationDisplay } from './EvaluationDisplay';
import { interviewApi } from '../api/interviewApi';

export const InterviewContainer: React.FC = () => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<any>(null);
  const [questionStartTime, setQuestionStartTime] = useState<Date>(new Date());
  const [showEvaluation, setShowEvaluation] = useState(false);
  const [evaluation, setEvaluation] = useState<any>(null);
  const [evaluating, setEvaluating] = useState(false);

  const handleDomainSelect = async (domain: string) => {
    const response = await interviewApi.startSession(domain);
    if (response.success) {
      setSessionId(response.session_id);
      await loadCurrentQuestion(response.session_id);
    }
  };

  const loadCurrentQuestion = async (id: string) => {
    const response = await interviewApi.getCurrentQuestion(id);
    if (response.success) {
      setCurrentQuestion(response);
      setQuestionStartTime(new Date());
      setShowEvaluation(false);
      setEvaluation(null);
    }
  };

  const handleAnswerComplete = async (
    transcript: string, 
    autoCompleted: boolean, 
    silenceDuration: number
  ) => {
    if (!sessionId) return;

    // Submit answer
    await interviewApi.submitAnswer(sessionId, {
      transcript,
      silence_duration: silenceDuration,
      auto_completed: autoCompleted
    });

    // Evaluate answer
    setEvaluating(true);
    const evalResponse = await interviewApi.evaluateAnswer(
      sessionId, 
      currentQuestion.question.id
    );
    
    if (evalResponse.success) {
      setEvaluation(evalResponse.evaluation);
      setShowEvaluation(true);
    }
    setEvaluating(false);
  };

  const handleNext = async () => {
    if (!sessionId) return;
    await interviewApi.navigateNext(sessionId);
    await loadCurrentQuestion(sessionId);
  };

  const handlePrevious = async () => {
    if (!sessionId) return;
    await interviewApi.navigatePrevious(sessionId);
    await loadCurrentQuestion(sessionId);
  };

  if (!sessionId) {
    return <DomainSelector onDomainSelect={handleDomainSelect} />;
  }

  if (!currentQuestion) {
    return <div>Loading...</div>;
  }

  return (
    <div className="interview-container">
      <QuestionDisplay
        question={currentQuestion.question}
        questionNumber={currentQuestion.question_number}
        totalQuestions={currentQuestion.total_questions}
        startTime={questionStartTime}
      />

      <AnswerCapture
        onAnswerComplete={handleAnswerComplete}
        silenceThreshold={4.0}
      />

      {showEvaluation && evaluation && (
        <EvaluationDisplay 
          evaluation={evaluation} 
          loading={evaluating}
        />
      )}

      <NavigationControls
        hasPrevious={currentQuestion.has_previous}
        hasNext={currentQuestion.has_next}
        onPrevious={handlePrevious}
        onNext={handleNext}
        onComplete={() => alert('Interview Complete!')}
        isLastQuestion={!currentQuestion.has_next}
      />
    </div>
  );
};
'''

# Save all components
import os
os.makedirs("interview_implementation/components", exist_ok=True)

components = {
    "DomainSelector.tsx": domain_selector_component,
    "QuestionDisplay.tsx": question_display_component,
    "NavigationControls.tsx": navigation_component,
    "AnswerCapture.tsx": answer_capture_component,
    "EvaluationDisplay.tsx": evaluation_display_component,
    "InterviewContainer.tsx": interview_container
}

for filename, content in components.items():
    filepath = f"interview_implementation/components/{filename}"
    with open(filepath, "w") as f:
        f.write(content)
    print(f"✅ Created: {filepath}")

print("\n" + "=" * 80)
print("REACT COMPONENTS SUMMARY")
print("=" * 80)

print("\n📦 Components Created:\n")
print("1. DomainSelector - 5 domain buttons for interview selection")
print("2. QuestionDisplay - Question text, difficulty badge, per-question timer")
print("3. NavigationControls - Previous/Next buttons, Complete button on last question")
print("4. AnswerCapture - Record button, transcript display, 4s silence detection")
print("5. EvaluationDisplay - Score cards (correctness/completeness/clarity), feedback")
print("6. InterviewContainer - Main orchestrator connecting all components")

print("\n🎯 Key Features:\n")
print("• Real-time per-question timer (MM:SS format)")
print("• Color-coded difficulty badges (Easy=green, Medium=yellow, Hard=red)")
print("• 4-second silence auto-completion with warning countdown")
print("• Score visualization with color coding (80+=green, 60+=yellow, <60=red)")
print("• Strengths/improvements lists with detailed feedback")
print("• Navigation state management (disable buttons appropriately)")
print("• Loading states for evaluation")

print("\n🔌 Integration Points:\n")
print("• interviewApi.startSession(domain)")
print("• interviewApi.getCurrentQuestion(sessionId)")
print("• interviewApi.submitAnswer(sessionId, answerData)")
print("• interviewApi.evaluateAnswer(sessionId, questionId)")
print("• interviewApi.navigateNext/Previous(sessionId)")

print("\n🎨 Styling Notes:\n")
print("• Uses Zerve design system colors")
print("• Dark background (#1D1D20)")
print("• Primary text (#fbfbff)")
print("• Accent colors (#ffd400, #17b26a, #f04438)")
print("• Responsive layout with flexbox/grid")

react_components_complete = True
