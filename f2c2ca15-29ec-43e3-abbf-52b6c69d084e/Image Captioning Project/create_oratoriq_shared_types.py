import os

print("=" * 80)
print("ORATORIQ - CREATING SHARED TYPES & SCHEMAS WITH FER SUPPORT")
print("=" * 80)

# Create directory structure
base_dir = "oratoriq/shared/types"
os.makedirs(base_dir, exist_ok=True)

# ============================================================================
# TypeScript Types (index.ts) - UPDATED WITH FER
# ============================================================================
types_content = '''/**
 * OratorIQ - Core Type Definitions
 * Shared types for session data, transcription, facial events (FER), and evaluation
 */

// ============================================================================
// Session Types
// ============================================================================

export interface Session {
  id: string;
  userId: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  duration: number; // milliseconds
  videoUrl?: string;
  audioUrl?: string;
  status: SessionStatus;
  evaluation?: EvaluationResult;
}

export enum SessionStatus {
  RECORDING = "recording",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed"
}

// ============================================================================
// Transcription Types
// ============================================================================

export interface TranscriptWord {
  word: string;
  start: number; // timestamp in milliseconds
  end: number;   // timestamp in milliseconds
  confidence: number; // 0-1
  speaker?: string;
}

export interface Transcript {
  sessionId: string;
  words: TranscriptWord[];
  fullText: string;
  language: string;
}

// ============================================================================
// Facial Expression Recognition (FER) Types - face-api.js
// ============================================================================

export interface FacialExpression {
  neutral: number;
  happy: number;
  sad: number;
  angry: number;
  fearful: number;
  disgusted: number;
  surprised: number;
}

export interface FaceLandmarks {
  positions: { x: number; y: number }[];
}

export interface FaceDetectionResult {
  timestamp: number;
  detected: boolean;
  expressions: FacialExpression;
  landmarks?: FaceLandmarks;
  attentionScore: number; // 0-1, derived from face presence and landmarks
}

export interface FacialEvent {
  timestamp: number; // milliseconds
  eventType: FacialEventType;
  confidence: number; // 0-1
  expressions?: FacialExpression;
  attentionScore?: number;
  details?: Record<string, any>;
}

export enum FacialEventType {
  NEUTRAL = "neutral",
  HAPPY = "happy",
  SAD = "sad",
  ANGRY = "angry",
  FEARFUL = "fearful",
  DISGUSTED = "disgusted",
  SURPRISED = "surprised",
  EYE_CONTACT = "eye_contact",
  LOOKING_AWAY = "looking_away",
  HEAD_NOD = "head_nod",
  HEAD_SHAKE = "head_shake"
}

// ============================================================================
// Disfluency Event Types
// ============================================================================

export interface DisfluencyEvent {
  timestamp: number; // milliseconds
  duration: number;  // milliseconds
  disfluencyType: DisfluencyType;
  text?: string;     // the actual disfluent words/sounds
  severity: DisfluencySeverity;
}

export enum DisfluencyType {
  FILLER_WORD = "filler_word",        // um, uh, like
  REPETITION = "repetition",          // repeated words
  PROLONGATION = "prolongation",      // stretched sounds
  PAUSE = "pause",                    // silent pauses
  FALSE_START = "false_start"         // restarted sentences
}

export enum DisfluencySeverity {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high"
}

// ============================================================================
// Evaluation Result Types
// ============================================================================

export interface EvaluationResult {
  sessionId: string;
  overallScore: number; // 0-100
  metrics: EvaluationMetrics;
  insights: Insight[];
  recommendations: string[];
  generatedAt: Date;
}

export interface EvaluationMetrics {
  clarity: MetricScore;
  pace: MetricScore;
  engagement: MetricScore;
  confidence: MetricScore;
  disfluency: MetricScore;
}

export interface MetricScore {
  score: number;     // 0-100
  category: ScoreCategory;
  details: string;
}

export enum ScoreCategory {
  EXCELLENT = "excellent",
  GOOD = "good",
  FAIR = "fair",
  NEEDS_IMPROVEMENT = "needs_improvement"
}

export interface Insight {
  type: InsightType;
  message: string;
  timestamp?: number;
  severity: "info" | "warning" | "critical";
}

export enum InsightType {
  PACE = "pace",
  CLARITY = "clarity",
  ENGAGEMENT = "engagement",
  DISFLUENCY = "disfluency",
  BODY_LANGUAGE = "body_language"
}
'''

types_file = os.path.join(base_dir, "index.ts")
with open(types_file, 'w') as f:
    f.write(types_content)

print(f"\n✓ Created TypeScript types with FER support: {types_file}")

# ============================================================================
# Zod Schemas (schemas.ts) - UPDATED WITH FER
# ============================================================================
schemas_content = '''/**
 * OratorIQ - Zod Validation Schemas
 * Runtime validation for API requests/responses including FER data
 */

import { z } from 'zod';

// ============================================================================
// Session Schemas
// ============================================================================

export const SessionStatusSchema = z.enum([
  'recording', 'processing', 'completed', 'failed'
]);

export const SessionSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  title: z.string().min(1).max(200),
  createdAt: z.date(),
  updatedAt: z.date(),
  duration: z.number().int().nonnegative(),
  videoUrl: z.string().url().optional(),
  audioUrl: z.string().url().optional(),
  status: SessionStatusSchema,
  evaluation: z.lazy(() => EvaluationResultSchema).optional()
});

// ============================================================================
// Transcription Schemas
// ============================================================================

export const TranscriptWordSchema = z.object({
  word: z.string(),
  start: z.number().nonnegative(),
  end: z.number().nonnegative(),
  confidence: z.number().min(0).max(1),
  speaker: z.string().optional()
});

export const TranscriptSchema = z.object({
  sessionId: z.string().uuid(),
  words: z.array(TranscriptWordSchema),
  fullText: z.string(),
  language: z.string().default('en')
});

// ============================================================================
// Facial Expression Recognition (FER) Schemas
// ============================================================================

export const FacialExpressionSchema = z.object({
  neutral: z.number().min(0).max(1),
  happy: z.number().min(0).max(1),
  sad: z.number().min(0).max(1),
  angry: z.number().min(0).max(1),
  fearful: z.number().min(0).max(1),
  disgusted: z.number().min(0).max(1),
  surprised: z.number().min(0).max(1)
});

export const FaceLandmarksSchema = z.object({
  positions: z.array(z.object({
    x: z.number(),
    y: z.number()
  }))
});

export const FaceDetectionResultSchema = z.object({
  timestamp: z.number().nonnegative(),
  detected: z.boolean(),
  expressions: FacialExpressionSchema,
  landmarks: FaceLandmarksSchema.optional(),
  attentionScore: z.number().min(0).max(1)
});

export const FacialEventTypeSchema = z.enum([
  'neutral', 'happy', 'sad', 'angry', 'fearful', 'disgusted', 'surprised',
  'eye_contact', 'looking_away', 'head_nod', 'head_shake'
]);

export const FacialEventSchema = z.object({
  timestamp: z.number().nonnegative(),
  eventType: FacialEventTypeSchema,
  confidence: z.number().min(0).max(1),
  expressions: FacialExpressionSchema.optional(),
  attentionScore: z.number().min(0).max(1).optional(),
  details: z.record(z.any()).optional()
});

// ============================================================================
// Disfluency Event Schemas
// ============================================================================

export const DisfluencyTypeSchema = z.enum([
  'filler_word', 'repetition', 'prolongation', 'pause', 'false_start'
]);

export const DisfluencySeveritySchema = z.enum(['low', 'medium', 'high']);

export const DisfluencyEventSchema = z.object({
  timestamp: z.number().nonnegative(),
  duration: z.number().nonnegative(),
  disfluencyType: DisfluencyTypeSchema,
  text: z.string().optional(),
  severity: DisfluencySeveritySchema
});

// ============================================================================
// Evaluation Result Schemas
// ============================================================================

export const ScoreCategorySchema = z.enum([
  'excellent', 'good', 'fair', 'needs_improvement'
]);

export const MetricScoreSchema = z.object({
  score: z.number().min(0).max(100),
  category: ScoreCategorySchema,
  details: z.string()
});

export const EvaluationMetricsSchema = z.object({
  clarity: MetricScoreSchema,
  pace: MetricScoreSchema,
  engagement: MetricScoreSchema,
  confidence: MetricScoreSchema,
  disfluency: MetricScoreSchema
});

export const InsightTypeSchema = z.enum([
  'pace', 'clarity', 'engagement', 'disfluency', 'body_language'
]);

export const InsightSchema = z.object({
  type: InsightTypeSchema,
  message: z.string(),
  timestamp: z.number().nonnegative().optional(),
  severity: z.enum(['info', 'warning', 'critical'])
});

export const EvaluationResultSchema = z.object({
  sessionId: z.string().uuid(),
  overallScore: z.number().min(0).max(100),
  metrics: EvaluationMetricsSchema,
  insights: z.array(InsightSchema),
  recommendations: z.array(z.string()),
  generatedAt: z.date()
});

// ============================================================================
// API Request/Response Schemas
// ============================================================================

export const CreateSessionRequestSchema = z.object({
  userId: z.string().uuid(),
  title: z.string().min(1).max(200)
});

export const CreateSessionResponseSchema = z.object({
  session: SessionSchema,
  message: z.string()
});

export const UploadRecordingRequestSchema = z.object({
  sessionId: z.string().uuid(),
  videoFile: z.instanceof(File).optional(),
  audioFile: z.instanceof(File).optional()
});

export const UploadRecordingResponseSchema = z.object({
  sessionId: z.string().uuid(),
  videoUrl: z.string().url().optional(),
  audioUrl: z.string().url().optional(),
  message: z.string()
});

export const GetEvaluationRequestSchema = z.object({
  sessionId: z.string().uuid()
});

export const GetEvaluationResponseSchema = z.object({
  evaluation: EvaluationResultSchema,
  transcript: TranscriptSchema,
  facialEvents: z.array(FacialEventSchema),
  disfluencyEvents: z.array(DisfluencyEventSchema)
});

export const ListSessionsRequestSchema = z.object({
  userId: z.string().uuid(),
  limit: z.number().int().positive().max(100).default(20),
  offset: z.number().int().nonnegative().default(0)
});

export const ListSessionsResponseSchema = z.object({
  sessions: z.array(SessionSchema),
  total: z.number().int().nonnegative(),
  limit: z.number().int().positive(),
  offset: z.number().int().nonnegative()
});

export const ErrorResponseSchema = z.object({
  error: z.string(),
  message: z.string(),
  statusCode: z.number().int(),
  details: z.record(z.any()).optional()
});

// ============================================================================
// Type Exports (inferred from schemas)
// ============================================================================

export type Session = z.infer<typeof SessionSchema>;
export type TranscriptWord = z.infer<typeof TranscriptWordSchema>;
export type Transcript = z.infer<typeof TranscriptSchema>;
export type FacialExpression = z.infer<typeof FacialExpressionSchema>;
export type FaceDetectionResult = z.infer<typeof FaceDetectionResultSchema>;
export type FacialEvent = z.infer<typeof FacialEventSchema>;
export type DisfluencyEvent = z.infer<typeof DisfluencyEventSchema>;
export type EvaluationResult = z.infer<typeof EvaluationResultSchema>;
export type CreateSessionRequest = z.infer<typeof CreateSessionRequestSchema>;
export type CreateSessionResponse = z.infer<typeof CreateSessionResponseSchema>;
export type GetEvaluationResponse = z.infer<typeof GetEvaluationResponseSchema>;
export type ListSessionsRequest = z.infer<typeof ListSessionsRequestSchema>;
export type ListSessionsResponse = z.infer<typeof ListSessionsResponseSchema>;
'''

schemas_file = os.path.join(base_dir, "schemas.ts")
with open(schemas_file, 'w') as f:
    f.write(schemas_content)

print(f"✓ Created Zod schemas with FER support: {schemas_file}")

# List created files
print("\n" + "=" * 80)
print("SUCCESS - SHARED TYPES WITH FER SUPPORT CREATED")
print("=" * 80)
print(f"\n📁 Files created in {base_dir}:")
print(f"  • index.ts - TypeScript type definitions")
print(f"  • schemas.ts - Zod validation schemas")
print("\n✅ Type-safe contracts established between client and server")
print("✅ Runtime validation schemas with Zod ready for use")
print("\n📦 Key types created:")
print("  • Session - Session data with status tracking")
print("  • TranscriptWord - Word-level transcription with timing")
print("  • FacialExpression - 7 emotion scores from face-api.js")
print("  • FaceDetectionResult - Complete FER result with attention score")
print("  • FacialEvent - Timestamped facial events with expressions")
print("  • DisfluencyEvent - Speech disfluency detection")
print("  • EvaluationResult - Complete evaluation with metrics")
print("\n🎭 FER Integration:")
print("  • FacialExpression: neutral, happy, sad, angry, fearful, disgusted, surprised")
print("  • FaceDetectionResult: timestamp, detected flag, expressions, landmarks, attentionScore")
print("  • FacialEvent: extended with expressions and attentionScore fields")
print("\n🔌 API schemas created:")
print("  • CreateSessionRequest/Response")
print("  • UploadRecordingRequest/Response")
print("  • GetEvaluationRequest/Response")
print("  • ListSessionsRequest/Response")
print("  • ErrorResponse")

shared_types_with_fer_created = True
