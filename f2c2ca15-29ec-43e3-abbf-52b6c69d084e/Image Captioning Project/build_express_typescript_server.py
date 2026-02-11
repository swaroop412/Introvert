import os

print("=" * 80)
print("ORATORIQ - EXPRESS SERVER WITH TYPESCRIPT")
print("=" * 80)

# Create server directory structure
server_base = "oratoriq/server/src"
os.makedirs(server_base, exist_ok=True)
os.makedirs(f"{server_base}/middleware", exist_ok=True)
os.makedirs(f"{server_base}/routes", exist_ok=True)
os.makedirs(f"{server_base}/config", exist_ok=True)
os.makedirs(f"{server_base}/services", exist_ok=True)

# ============================================================================
# 1. Environment Configuration (.env.example)
# ============================================================================
env_example = '''# Server Configuration
PORT=3001
NODE_ENV=development

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# CORS Configuration
CLIENT_URL=http://localhost:5173
'''

env_file = "oratoriq/server/.env.example"
os.makedirs("oratoriq/server", exist_ok=True)
with open(env_file, 'w') as f:
    f.write(env_example)

print(f"\n✓ Created: {env_file}")

# ============================================================================
# 2. Environment Config Module (config/env.ts)
# ============================================================================
env_config = '''import dotenv from 'dotenv';

dotenv.config();

interface EnvConfig {
  port: number;
  nodeEnv: string;
  groqApiKey: string;
  clientUrl: string;
}

function validateEnv(): EnvConfig {
  const requiredVars = ['GROQ_API_KEY'];
  const missing = requiredVars.filter(v => !process.env[v]);
  
  if (missing.length > 0) {
    console.warn(`⚠️  Missing: ${missing.join(', ')}`);
  }

  return {
    port: parseInt(process.env.PORT || '3001', 10),
    nodeEnv: process.env.NODE_ENV || 'development',
    groqApiKey: process.env.GROQ_API_KEY || 'placeholder',
    clientUrl: process.env.CLIENT_URL || 'http://localhost:5173'
  };
}

export const env = validateEnv();
export default env;
'''

with open(f"{server_base}/config/env.ts", 'w') as f:
    f.write(env_config)
print(f"✓ Created: {server_base}/config/env.ts")

# ============================================================================
# 3. Error Handling Middleware (middleware/errorHandler.ts)
# ============================================================================
error_handler = '''import { Request, Response, NextFunction } from 'express';

export class AppError extends Error {
  statusCode: number;
  isOperational: boolean;

  constructor(message: string, statusCode: number = 500) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;
    Error.captureStackTrace(this, this.constructor);
  }
}

export function errorHandler(
  err: Error | AppError,
  req: Request,
  res: Response,
  next: NextFunction
) {
  console.error('Error:', err);

  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      error: err.name,
      message: err.message,
      statusCode: err.statusCode,
      ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
    });
  }

  return res.status(500).json({
    error: 'InternalServerError',
    message: 'An unexpected error occurred',
    statusCode: 500,
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
}

export function notFoundHandler(req: Request, res: Response) {
  res.status(404).json({
    error: 'NotFound',
    message: `Route ${req.method} ${req.path} not found`,
    statusCode: 404
  });
}
'''

with open(f"{server_base}/middleware/errorHandler.ts", 'w') as f:
    f.write(error_handler)
print(f"✓ Created: {server_base}/middleware/errorHandler.ts")

# ============================================================================
# 4. Health Check Route (routes/health.ts)
# ============================================================================
health_route = '''import { Router, Request, Response } from 'express';
import { env } from '../config/env';

const router = Router();

router.get('/', (req: Request, res: Response) => {
  res.json({
    status: 'ok',
    message: 'OratorIQ API is running',
    timestamp: new Date().toISOString(),
    environment: env.nodeEnv,
    version: '1.0.0'
  });
});

export default router;
'''

with open(f"{server_base}/routes/health.ts", 'w') as f:
    f.write(health_route)
print(f"✓ Created: {server_base}/routes/health.ts")

# ============================================================================
# 5. Groq LLM Service (services/groqService.ts)
# ============================================================================
groq_service = '''import Groq from 'groq-sdk';
import { env } from '../config/env';
import { AppError } from '../middleware/errorHandler';

const groq = new Groq({
  apiKey: env.groqApiKey
});

export interface EvaluationSection {
  score: number;
  feedback: string;
}

export interface EvaluationResult {
  overallScore: number;
  sections: {
    content: EvaluationSection;
    technicalDepth: EvaluationSection;
    communication: EvaluationSection;
    delivery: EvaluationSection;
  };
  strengths: string[];
  improvements: string[];
  suggestedPractice: string[];
}

export interface EvaluateRequest {
  mode: 'interview' | 'speech';
  transcript: string;
  context?: {
    topic?: string;
    targetAudience?: string;
    duration?: number;
  };
}

async function callGroq(systemPrompt: string, userPrompt: string, model: string): Promise<string> {
  const completion = await groq.chat.completions.create({
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt }
    ],
    model: model,
    temperature: 0.3,
    max_tokens: 2048,
  });

  return completion.choices[0]?.message?.content || '';
}

function buildInterviewPrompt(transcript: string, context?: any): { system: string; user: string } {
  const systemPrompt = `You are an expert interview coach and evaluator. Analyze interview responses with focus on:
- Content quality and relevance
- Technical depth and accuracy
- Communication clarity and structure
- Delivery and confidence

Provide scores (0-100) and actionable feedback for each dimension.`;

  const userPrompt = `Evaluate this interview response:

${context?.topic ? `Topic: ${context.topic}` : ''}
${context?.targetAudience ? `Audience: ${context.targetAudience}` : ''}

TRANSCRIPT:
${transcript}

Return evaluation in this JSON format:
{
  "overallScore": <number 0-100>,
  "sections": {
    "content": { "score": <number 0-100>, "feedback": "<string>" },
    "technicalDepth": { "score": <number 0-100>, "feedback": "<string>" },
    "communication": { "score": <number 0-100>, "feedback": "<string>" },
    "delivery": { "score": <number 0-100>, "feedback": "<string>" }
  },
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "improvements": ["<improvement 1>", "<improvement 2>", "<improvement 3>"],
  "suggestedPractice": ["<practice 1>", "<practice 2>", "<practice 3>"]
}`;

  return { system: systemPrompt, user: userPrompt };
}

function buildSpeechPrompt(transcript: string, context?: any): { system: string; user: string } {
  const systemPrompt = `You are an expert public speaking coach. Evaluate speeches focusing on:
- Content organization and message clarity
- Technical knowledge and depth
- Communication effectiveness and engagement
- Delivery style, pace, and presence

Provide scores (0-100) and constructive feedback for each area.`;

  const userPrompt = `Evaluate this speech:

${context?.topic ? `Topic: ${context.topic}` : ''}
${context?.targetAudience ? `Target Audience: ${context.targetAudience}` : ''}
${context?.duration ? `Duration: ${context.duration} seconds` : ''}

TRANSCRIPT:
${transcript}

Return evaluation in this JSON format:
{
  "overallScore": <number 0-100>,
  "sections": {
    "content": { "score": <number 0-100>, "feedback": "<string>" },
    "technicalDepth": { "score": <number 0-100>, "feedback": "<string>" },
    "communication": { "score": <number 0-100>, "feedback": "<string>" },
    "delivery": { "score": <number 0-100>, "feedback": "<string>" }
  },
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "improvements": ["<improvement 1>", "<improvement 2>", "<improvement 3>"],
  "suggestedPractice": ["<practice 1>", "<practice 2>", "<practice 3>"]
}`;

  return { system: systemPrompt, user: userPrompt };
}

export async function evaluateTranscript(request: EvaluateRequest): Promise<EvaluationResult> {
  if (!request.transcript || request.transcript.trim().length === 0) {
    throw new AppError('Transcript is required', 400);
  }

  if (!['interview', 'speech'].includes(request.mode)) {
    throw new AppError('Mode must be either "interview" or "speech"', 400);
  }

  // Build prompts based on mode
  const prompts = request.mode === 'interview'
    ? buildInterviewPrompt(request.transcript, request.context)
    : buildSpeechPrompt(request.transcript, request.context);

  // Try Llama-3.1-70b first, fallback to Mixtral
  let response: string;
  try {
    response = await callGroq(prompts.system, prompts.user, 'llama-3.1-70b-versatile');
  } catch (error: any) {
    console.warn('Llama-3.1-70b failed, falling back to Mixtral:', error.message);
    response = await callGroq(prompts.system, prompts.user, 'mixtral-8x7b-32768');
  }

  // Parse JSON response
  const jsonMatch = response.match(/\\{[\\s\\S]*\\}/);
  if (!jsonMatch) {
    throw new AppError('Failed to parse evaluation response', 500);
  }

  const evaluation = JSON.parse(jsonMatch[0]);
  return evaluation as EvaluationResult;
}
'''

with open(f"{server_base}/services/groqService.ts", 'w') as f:
    f.write(groq_service)
print(f"✓ Created: {server_base}/services/groqService.ts")

# ============================================================================
# 6. Evaluate Route (routes/evaluate.ts)
# ============================================================================
evaluate_route = '''import { Router, Request, Response, NextFunction } from 'express';
import { evaluateTranscript, EvaluateRequest } from '../services/groqService';
import { AppError } from '../middleware/errorHandler';

const router = Router();

router.post('/', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { mode, transcript, context } = req.body as EvaluateRequest;

    if (!mode || !transcript) {
      throw new AppError('Missing required fields: mode and transcript', 400);
    }

    const result = await evaluateTranscript({ mode, transcript, context });
    
    res.json(result);
  } catch (error) {
    next(error);
  }
});

export default router;
'''

with open(f"{server_base}/routes/evaluate.ts", 'w') as f:
    f.write(evaluate_route)
print(f"✓ Created: {server_base}/routes/evaluate.ts")

# ============================================================================
# 7. Main Server File (index.ts)
# ============================================================================
index_ts = '''import express, { Express, Request, Response } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import { env } from './config/env';
import { errorHandler, notFoundHandler } from './middleware/errorHandler';
import healthRouter from './routes/health';
import evaluateRouter from './routes/evaluate';

const app: Express = express();

// Middleware
app.use(helmet());
app.use(cors({
  origin: env.clientUrl,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(morgan(env.nodeEnv === 'development' ? 'dev' : 'combined'));

// Routes
app.use('/api/health', healthRouter);
app.use('/api/evaluate', evaluateRouter);

app.get('/', (req: Request, res: Response) => {
  res.json({
    name: 'OratorIQ API',
    version: '1.0.0',
    description: 'Speech analysis and evaluation platform',
    endpoints: {
      health: 'GET /api/health',
      evaluate: 'POST /api/evaluate'
    }
  });
});

// Error handlers
app.use(notFoundHandler);
app.use(errorHandler);

// Start server
const PORT = env.port;
app.listen(PORT, () => {
  console.log('🚀 OratorIQ Server Started');
  console.log(`📡 Server: http://localhost:${PORT}`);
  console.log(`🌍 Environment: ${env.nodeEnv}`);
  console.log('\\n✅ Ready to accept requests\\n');
});

export default app;
'''

with open(f"{server_base}/index.ts", 'w') as f:
    f.write(index_ts)
print(f"✓ Created: {server_base}/index.ts")

# ============================================================================
# 8. TypeScript Config (tsconfig.json)
# ============================================================================
tsconfig = '''{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node",
    "declaration": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
'''

with open("oratoriq/server/tsconfig.json", 'w') as f:
    f.write(tsconfig)
print(f"✓ Created: oratoriq/server/tsconfig.json")

# ============================================================================
# 9. Package.json
# ============================================================================
package_json = '''{
  "name": "@oratoriq/server",
  "version": "1.0.0",
  "description": "OratorIQ Express API Server with TypeScript and Groq LLM",
  "main": "dist/index.js",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "helmet": "^7.1.0",
    "morgan": "^1.10.0",
    "dotenv": "^16.3.1",
    "groq-sdk": "^0.3.2"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/cors": "^2.8.17",
    "@types/morgan": "^1.9.9",
    "@types/node": "^20.10.6",
    "typescript": "^5.3.3",
    "tsx": "^4.7.0"
  }
}
'''

with open("oratoriq/server/package.json", 'w') as f:
    f.write(package_json)
print(f"✓ Created: oratoriq/server/package.json")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 80)
print("✅ EXPRESS SERVER WITH LLM EVALUATION COMPLETE")
print("=" * 80)

print("\n📁 Structure:")
print("  oratoriq/server/")
print("    ├── src/")
print("    │   ├── index.ts                     - Main server")
print("    │   ├── config/env.ts                - Environment config")
print("    │   ├── middleware/errorHandler.ts   - Error handling")
print("    │   ├── services/groqService.ts      - Groq LLM service")
print("    │   └── routes/")
print("    │       ├── health.ts                - Health endpoint")
print("    │       └── evaluate.ts              - Evaluation endpoint")
print("    ├── tsconfig.json")
print("    ├── package.json")
print("    └── .env.example")

print("\n✅ Features:")
print("  • Express + TypeScript")
print("  • Groq LLM integration (Llama-3.1-70b + Mixtral fallback)")
print("  • POST /api/evaluate - LLM evaluation endpoint")
print("  • Interview & Speech mode prompts")
print("  • Structured rubric scoring (Content, Technical, Communication, Delivery)")
print("  • GET /api/health - Health check")
print("  • CORS, Helmet, Morgan, Error handling")

print("\n🚀 Endpoints:")
print("  POST /api/evaluate")
print("    Body: {")
print("      mode: 'interview' | 'speech',")
print("      transcript: string,")
print("      context?: { topic?, targetAudience?, duration? }")
print("    }")
print("    Response: {")
print("      overallScore: number,")
print("      sections: { content, technicalDepth, communication, delivery },")
print("      strengths: string[],")
print("      improvements: string[],")
print("      suggestedPractice: string[]")
print("    }")

print("\n📝 Quick Start:")
print("  cd oratoriq/server")
print("  npm install")
print("  cp .env.example .env")
print("  # Add your GROQ_API_KEY to .env")
print("  npm run dev")

print("\n📡 Server: http://localhost:3001")
print("   GET  /              - API info")
print("   GET  /api/health    - Health check")
print("   POST /api/evaluate  - LLM evaluation")

evaluation_service_complete = True
print(f"\n✓ evaluation_service_complete = {evaluation_service_complete}")
