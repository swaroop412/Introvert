# OratorIQ - AI-Powered Speech Analysis Platform

**OratorIQ** is a real-time speech analysis system that provides comprehensive feedback on presentation skills, interview performance, and communication effectiveness using AI-powered speech-to-text, facial expression recognition, and disfluency detection.

---

## 🚀 Quick Start (< 5 Minutes)

### Prerequisites
- **Node.js** 18+ and **npm** 8+
- **Git**
- **Groq API Key** (for production STT)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/oratoriq.git
cd oratoriq

# Install dependencies for both client and server
npm install
cd client && npm install && cd ..
cd server && npm install && cd ..
```

### Environment Variables

Create `.env` files in both `client/` and `server/` directories:

**`server/.env`**
```bash
# Required for production
GROQ_API_KEY=your_groq_api_key_here

# Optional (defaults shown)
PORT=3001
DEV_MODE=false
CORS_ORIGIN=http://localhost:5173
```

**`client/.env`**
```bash
# Server URL
VITE_API_URL=http://localhost:3001

# Dev Mode (uses mock data)
VITE_DEV_MODE=false
```

### Running the Application

```bash
# Terminal 1 - Start server
cd server
npm run dev

# Terminal 2 - Start client
cd client
npm run dev
```

**Access the app:** Open [http://localhost:5173](http://localhost:5173)

---

## 📁 Project Structure

```
oratoriq/
├── client/                  # React + Vite frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── WebcamRecorder.tsx
│   │   │   ├── TranscriptPanel.tsx
│   │   │   ├── Timeline.tsx
│   │   │   ├── MetricsCards.tsx
│   │   │   └── ResultsView.tsx
│   │   ├── hooks/          # Custom React hooks
│   │   │   ├── useFaceAPI.ts
│   │   │   └── useStreamingTranscriber.ts
│   │   ├── store/          # Zustand state management
│   │   │   └── sessionStore.ts
│   │   ├── utils/          # Utility modules
│   │   │   ├── stutter.ts  # Disfluency detection
│   │   │   └── timeline.ts # Timeline system
│   │   ├── mocks/          # Mock providers for dev mode
│   │   └── App.tsx         # Main application
│   └── package.json
│
├── server/                  # Express + TypeScript backend
│   ├── src/
│   │   ├── routes/         # API routes
│   │   │   ├── transcribe.ts
│   │   │   ├── interview.ts
│   │   │   └── evaluate.ts
│   │   ├── services/       # Business logic
│   │   │   ├── groqService.ts
│   │   │   └── evaluationService.ts
│   │   └── server.ts       # Express app
│   ├── tests/              # Unit tests
│   │   ├── stutter.test.ts
│   │   └── timeline.test.ts
│   └── package.json
│
├── shared/                  # Shared TypeScript types
│   └── types.ts
│
└── sample-data/            # Demo data for testing
    ├── demo_transcript.json
    ├── demo_facial_events.json
    └── complete_session.json
```

---

## 🧪 Testing

### Run Unit Tests

```bash
# Server tests
cd server
npm test

# Run specific test file
npm test -- stutter.test.ts

# Watch mode
npm test -- --watch
```

### Test Coverage

```bash
cd server
npm run test:coverage
```

### Manual Testing Checklist

#### ✅ Core Functionality
- [ ] **Webcam & Microphone Access**: Permissions granted, video preview shows
- [ ] **Speech-to-Text**: Transcription appears in real-time during recording
- [ ] **Facial Expression Recognition**: Expression badges update during recording
- [ ] **Disfluency Detection**: Filler words, pauses, repetitions highlighted in transcript
- [ ] **WPM Calculation**: Words-per-minute calculated and displayed accurately
- [ ] **Timeline Alignment**: Timeline shows synchronized events

#### ✅ Interview Mode
- [ ] **Question Loading**: Interview questions load correctly
- [ ] **Response Recording**: Can record answer to each question
- [ ] **Evaluation**: Scores and feedback generated after response
- [ ] **Export Results**: Can export session data as JSON

#### ✅ Dev Mode
- [ ] **Mock STT**: Works without Groq API key
- [ ] **Mock FER**: Works without face-api.js models
- [ ] **Sample Data Loading**: Can load demo transcript and events

#### ✅ Error Handling
- [ ] **No Webcam**: Graceful error message
- [ ] **No Microphone**: Graceful error message
- [ ] **API Failure**: Error displayed, app doesn't crash
- [ ] **Network Issues**: Retry logic works

---

## 🏗️ Architecture Overview

### Frontend Architecture

**State Management (Zustand)**
```typescript
sessionStore.ts
├── transcripts[]         // Real-time transcript segments
├── expressions[]         // Facial expression events
├── disfluencies[]        // Detected filler words, pauses, repetitions
├── wpmEvents[]          // Words-per-minute calculations
└── timeline             // UnifiedTimeline instance
```

**Data Flow**
```
WebcamRecorder → useFaceAPI → expressions → sessionStore
              → useStreamingTranscriber → transcripts → DisfluencyDetector → disfluencies → sessionStore
                                                                                           → timeline.align()
```

### Backend Architecture

**API Endpoints**
```
POST /api/transcribe        # Groq Whisper streaming STT
GET  /api/interview/questions  # Fetch interview questions
POST /api/interview/evaluate   # Evaluate interview response
POST /api/session/export       # Export session data
```

**Services**
- **GroqService**: Handles Groq API integration (Whisper, Llama)
- **EvaluationService**: Analyzes speech quality and content
- **DisfluencyService**: Server-side disfluency detection

---

## 🛠️ Key Technologies

| Technology | Purpose |
|------------|---------|
| **React + Vite** | Frontend framework and build tool |
| **TypeScript** | Type-safe development |
| **Zustand** | Lightweight state management |
| **face-api.js** | Facial expression recognition |
| **Groq API** | Ultra-fast STT (Whisper) and LLM (Llama) |
| **Express** | Backend API server |
| **Chart.js** | Data visualization |
| **Tailwind CSS** | Styling |

---

## 📊 Core Modules

### 1. **Disfluency Detection (stutter.ts)**

Detects speech disfluencies in real-time:
- **Filler words**: um, uh, like, you know, etc.
- **Pauses**: >400ms gaps between words
- **Repetitions**: Word repetitions within 2-second window
- **WPM**: Calculates words-per-minute (target: 120-160)

**Usage:**
```typescript
import { DisfluencyDetector } from './utils/stutter';

const detector = new DisfluencyDetector();
const events = detector.processTranscriptSegment(text, timestamp);
```

### 2. **Timeline System (timeline.ts)**

Unified event timeline with session-relative timestamps:
- Normalizes all events to milliseconds from session start
- Provides `align(tStart, tEnd)` query for time-slice analysis
- Calculates dominant expressions, WPM averages, attention scores

**Usage:**
```typescript
import { UnifiedTimeline } from './utils/timeline';

const timeline = new UnifiedTimeline();
timeline.addTranscriptEvent(timestamp, text, isFinal);
timeline.addExpressionEvent(timestamp, expression, confidence, allExpressions, attentionScore);

const slice = timeline.align(0, 5000); // Query first 5 seconds
console.log(slice.dominant_expression, slice.wpm_avg);
```

### 3. **Mock Providers (for Dev Mode)**

Enable testing without external dependencies:
- **MockSTTProvider**: Generates demo transcripts
- **MockFERProvider**: Generates facial expression events
- **MockInterviewProvider**: Provides interview questions and mock evaluations
- **MockDataGenerator**: Creates complete session data

**Enable Dev Mode:**
```bash
# In .env files
DEV_MODE=true         # server/.env
VITE_DEV_MODE=true    # client/.env
```

---

## 📦 Sample Data Files

Located in `sample-data/` directory:

| File | Description |
|------|-------------|
| `demo_transcript.json` | Sample speech transcript with timestamps |
| `demo_facial_events.json` | Sample facial expression events |
| `demo_disfluency_events.json` | Sample filler words, pauses, repetitions |
| `demo_wpm_events.json` | Sample WPM calculations |
| `complete_session.json` | Full session export with all event types |

**Load Sample Data:**
```typescript
import demoSession from '../sample-data/complete_session.json';
sessionStore.loadSession(demoSession);
```

---

## 🔧 npm Scripts

### Server Commands
```bash
npm run dev          # Start development server with nodemon
npm run build        # Compile TypeScript to dist/
npm start            # Run production server
npm test             # Run unit tests
npm run test:watch   # Run tests in watch mode
npm run lint         # Lint code with ESLint
```

### Client Commands
```bash
npm run dev          # Start Vite dev server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Lint code with ESLint
npm test             # Run Vitest tests
```

---

## 🌐 Environment Variables Reference

### Server Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | Yes* | - | Groq API key for STT/LLM (*not required in dev mode) |
| `PORT` | No | 3001 | Server port |
| `DEV_MODE` | No | false | Enable mock providers |
| `CORS_ORIGIN` | No | http://localhost:5173 | Allowed CORS origin |

### Client Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | Yes | http://localhost:3001 | Backend API URL |
| `VITE_DEV_MODE` | No | false | Enable frontend mock providers |

---

## 🐛 Troubleshooting

### Common Issues

**Issue: "GROQ_API_KEY not found"**
- **Solution**: Add `GROQ_API_KEY=your_key` to `server/.env` OR enable dev mode with `DEV_MODE=true`

**Issue: Webcam/microphone not working**
- **Solution**: Ensure HTTPS or localhost, check browser permissions

**Issue: Tests failing**
- **Solution**: Run `npm install` in server directory, ensure Node.js 18+

**Issue: CORS errors**
- **Solution**: Check `CORS_ORIGIN` in `server/.env` matches client URL

**Issue: face-api.js models not loading**
- **Solution**: Ensure models are in `client/public/models/` directory OR enable `VITE_DEV_MODE=true`

---

## 📚 API Reference

### POST `/api/transcribe`
Streams audio chunks to Groq Whisper for transcription.

**Request Body:**
```json
{
  "audio": "base64_encoded_audio_blob"
}
```

**Response:**
```json
{
  "text": "transcribed text segment",
  "timestamp": 1234567890,
  "is_final": true
}
```

### GET `/api/interview/questions`
Fetch interview questions by category.

**Query Params:**
- `category`: behavioral | technical
- `count`: number of questions

**Response:**
```json
{
  "questions": [
    {
      "id": 1,
      "category": "behavioral",
      "text": "Tell me about a time...",
      "difficulty": "medium"
    }
  ]
}
```

### POST `/api/interview/evaluate`
Evaluate interview response quality.

**Request Body:**
```json
{
  "question_id": 1,
  "transcript": "full answer transcript",
  "disfluencies": [...],
  "wpm": 145
}
```

**Response:**
```json
{
  "overall_score": 85,
  "scores": {
    "content": 90,
    "clarity": 80,
    "fluency": 85
  },
  "feedback": ["Consider providing more specific examples"]
}
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Run tests: `npm test`
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open pull request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- **Groq** for lightning-fast STT and LLM APIs
- **face-api.js** for facial expression recognition
- **Whisper** model by OpenAI

---

## 📧 Support

For issues, questions, or feature requests:
- **GitHub Issues**: [github.com/your-org/oratoriq/issues](https://github.com/your-org/oratoriq/issues)
- **Email**: support@oratoriq.com

---

**Built with ❤️ for better communication**
