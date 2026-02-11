import os

print("=" * 80)
print("ORATORIQ - EXPRESS SERVER SETUP WITH TYPESCRIPT")
print("=" * 80)

# Create server directory structure
server_base = "oratoriq/server/src"
os.makedirs(server_base, exist_ok=True)
os.makedirs(f"{server_base}/middleware", exist_ok=True)
os.makedirs(f"{server_base}/routes", exist_ok=True)
os.makedirs(f"{server_base}/config", exist_ok=True)

# ============================================================================
# Environment Configuration (.env.example)
# ============================================================================
env_example = '''# Server Configuration
PORT=3001
NODE_ENV=development

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL_ID=mixtral-8x7b-32768

# Alternative Groq Models:
# GROQ_MODEL_ID=llama2-70b-4096
# GROQ_MODEL_ID=gemma-7b-it

# CORS Configuration
CLIENT_URL=http://localhost:5173

# Database (future)
# DATABASE_URL=postgresql://localhost:5432/oratoriq
'''

env_file = "oratoriq/server/.env.example"
os.makedirs("oratoriq/server", exist_ok=True)
with open(env_file, 'w') as f:
    f.write(env_example)

print(f"\n✓ Created environment template: {env_file}")

# ============================================================================
# Environment Config Module (config/env.ts)
# ============================================================================
env_config = '''/**
 * Environment Configuration
 * Validates and exports environment variables
 */

import dotenv from 'dotenv';

dotenv.config();

interface EnvConfig {
  port: number;
  nodeEnv: string;
  groqApiKey: string;
  groqModelId: string;
  clientUrl: string;
}

function validateEnv(): EnvConfig {
  const requiredVars = ['GROQ_API_KEY', 'GROQ_MODEL_ID'];
  const missing = requiredVars.filter(v => !process.env[v]);
  
  if (missing.length > 0) {
    console.warn(`⚠️  Missing environment variables: ${missing.join(', ')}`);
    console.warn('Using placeholder values - some features may not work');
  }

  return {
    port: parseInt(process.env.PORT || '3001', 10),
    nodeEnv: process.env.NODE_ENV || 'development',
    groqApiKey: process.env.GROQ_API_KEY || 'placeholder_api_key',
    groqModelId: process.env.GROQ_MODEL_ID || 'mixtral-8x7b-32768',
    clientUrl: process.env.CLIENT_URL || 'http://localhost:5173'
  };
}

export const env = validateEnv();

export default env;
'''

config_file = f"{server_base}/config/env.ts"
with open(config_file, 'w') as f:
    f.write(env_config)

print(f"✓ Created environment config: {config_file}")

# ============================================================================
# Error Handling Middleware (middleware/errorHandler.ts)
# ============================================================================
error_handler = '''/**
 * Error Handling Middleware
 * Centralized error handling for Express
 */

import { Request, Response, NextFunction } from 'express';

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

  // Handle unknown errors
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

error_handler_file = f"{server_base}/middleware/errorHandler.ts"
with open(error_handler_file, 'w') as f:
    f.write(error_handler)

print(f"✓ Created error handler: {error_handler_file}")

# ============================================================================
# Health Check Route (routes/health.ts)
# ============================================================================
health_route = '''/**
 * Health Check Route
 * Simple endpoint to verify server is running
 */

import { Router, Request, Response } from 'express';
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

health_route_file = f"{server_base}/routes/health.ts"
with open(health_route_file, 'w') as f:
    f.write(health_route)

print(f"✓ Created health route: {health_route_file}")

# ============================================================================
# Main Server File (index.ts)
# ============================================================================
index_ts = '''/**
 * OratorIQ Express Server with TypeScript
 * Main entry point for the API server
 */

import express, { Express, Request, Response } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import { env } from './config/env';
import { errorHandler, notFoundHandler } from './middleware/errorHandler';
import healthRouter from './routes/health';

// Initialize Express app
const app: Express = express();

// ============================================================================
// Middleware Setup
// ============================================================================

// Security middleware
app.use(helmet());

// CORS configuration
app.use(cors({
  origin: env.clientUrl,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Logging middleware
if (env.nodeEnv === 'development') {
  app.use(morgan('dev'));
} else {
  app.use(morgan('combined'));
}

// ============================================================================
// Routes
// ============================================================================

// Health check endpoint
app.use('/api/health', healthRouter);

// Root endpoint
app.get('/', (req: Request, res: Response) => {
  res.json({
    name: 'OratorIQ API',
    version: '1.0.0',
    description: 'Speech analysis and evaluation platform',
    endpoints: {
      health: '/api/health',
      docs: '/api/docs (coming soon)'
    }
  });
});

// Future routes will be added here:
// app.use('/api/sessions', sessionRouter);
// app.use('/api/evaluations', evaluationRouter);
// app.use('/api/transcribe', transcribeRouter);

// ============================================================================
// Error Handling
// ============================================================================

// 404 handler
app.use(notFoundHandler);

// Global error handler
app.use(errorHandler);

// ============================================================================
// Server Startup
// ============================================================================

const PORT = env.port;

app.listen(PORT, () => {
  console.log('='.repeat(80));
  console.log('🚀 ORATORIQ SERVER STARTED');
  console.log('='.repeat(80));
  console.log(`📡 Server running on: http://localhost:${PORT}`);
  console.log(`🌍 Environment: ${env.nodeEnv}`);
  console.log(`🔗 Client URL: ${env.clientUrl}`);
  console.log(`🤖 Groq Model: ${env.groqModelId}`);
  console.log('='.repeat(80));
  console.log('\\n📋 Available endpoints:');
  console.log(`   GET  /              - API info`);
  console.log(`   GET  /api/health    - Health check`);
  console.log('\\n✅ Server ready to accept requests\\n');
});

export default app;
'''

index_file = f"{server_base}/index.ts"
with open(index_file, 'w') as f:
    f.write(index_ts)

print(f"✓ Created main server file: {index_file}")

# ============================================================================
# TypeScript Configuration (tsconfig.json)
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
    "declarationMap": true,
    "sourceMap": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
'''

tsconfig_file = "oratoriq/server/tsconfig.json"
with open(tsconfig_file, 'w') as f:
    f.write(tsconfig)

print(f"✓ Created TypeScript config: {tsconfig_file}")

# ============================================================================
# Package.json for server
# ============================================================================
package_json = '''{
  "name": "@oratoriq/server",
  "version": "1.0.0",
  "description": "OratorIQ Express API Server with TypeScript",
  "main": "dist/index.js",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "type-check": "tsc --noEmit"
  },
  "keywords": ["express", "typescript", "api", "speech-analysis"],
  "author": "OratorIQ Team",
  "license": "MIT",
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "helmet": "^7.1.0",
    "morgan": "^1.10.0",
    "dotenv": "^16.3.1",
    "zod": "^3.22.4"
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

package_file = "oratoriq/server/package.json"
with open(package_file, 'w') as f:
    f.write(package_json)

print(f"✓ Created package.json: {package_file}")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 80)
print("SUCCESS - EXPRESS SERVER SETUP COMPLETE")
print("=" * 80)
print(f"\n📁 Server structure created:")
print(f"  oratoriq/server/")
print(f"    ├── src/")
print(f"    │   ├── index.ts              - Main server file")
print(f"    │   ├── config/")
print(f"    │   │   └── env.ts            - Environment config")
print(f"    │   ├── middleware/")
print(f"    │   │   └── errorHandler.ts   - Error handling")
print(f"    │   └── routes/")
print(f"    │       └── health.ts         - Health check endpoint")
print(f"    ├── tsconfig.json             - TypeScript configuration")
print(f"    ├── package.json              - Dependencies")
print(f"    └── .env.example              - Environment template")

print("\n✅ Features implemented:")
print("  • Express server with TypeScript")
print("  • Health check endpoint at /api/health")
print("  • CORS setup with configurable origin")
print("  • Error handling middleware (AppError + global handler)")
print("  • Environment configuration (Groq API keys, model IDs)")
print("  • Security headers (Helmet)")
print("  • Request logging (Morgan)")
print("  • Body parsing (JSON + URL-encoded)")
print("  • 404 handler for unknown routes")

print("\n🚀 To start the server:")
print("  1. cd oratoriq/server")
print("  2. npm install")
print("  3. cp .env.example .env")
print("  4. Edit .env with your Groq API credentials")
print("  5. npm run dev")

print("\n📡 Server will run on: http://localhost:3001")
print("   GET /              - API information")
print("   GET /api/health    - Health check endpoint")

express_server_setup_complete = True
