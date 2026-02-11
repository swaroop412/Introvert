"""
Interview Mode API Endpoints
REST API for interview session management, navigation, answer capture
"""

import json
from typing import Dict

# API Endpoint Specifications for Interview Mode
api_spec = {
    "base_url": "/api/interview",
    "endpoints": [
        {
            "path": "/session/start",
            "method": "POST",
            "description": "Start new interview session with domain selection",
            "request_body": {
                "domain": "DSA | Web | Python | Java | System Design"
            },
            "response": {
                "success": True,
                "session_id": "uuid",
                "domain": "DSA",
                "total_questions": 5,
                "first_question": {
                    "id": "dsa_1",
                    "question": "text",
                    "difficulty": "medium"
                }
            }
        },
        {
            "path": "/session/:id/question/current",
            "method": "GET",
            "description": "Get current question with timer and navigation state",
            "response": {
                "success": True,
                "question": {
                    "id": "dsa_1",
                    "question": "text",
                    "difficulty": "medium"
                },
                "question_number": 1,
                "total_questions": 5,
                "time_elapsed": 12.5,
                "has_previous": False,
                "has_next": True
            }
        },
        {
            "path": "/session/:id/navigate/next",
            "method": "POST",
            "description": "Navigate to next question",
            "response": {
                "success": True,
                "navigated": "next",
                "question": "...",
                "question_number": 2
            }
        },
        {
            "path": "/session/:id/navigate/previous",
            "method": "POST",
            "description": "Navigate to previous question",
            "response": {
                "success": True,
                "navigated": "previous",
                "question": "...",
                "question_number": 1
            }
        },
        {
            "path": "/session/:id/answer",
            "method": "POST",
            "description": "Submit answer for current question",
            "request_body": {
                "transcript": "answer text",
                "silence_duration": 4.2,
                "auto_completed": True
            },
            "response": {
                "success": True,
                "answer_captured": True,
                "question_id": "dsa_1",
                "time_spent": 45.3
            }
        },
        {
            "path": "/session/:id/evaluate/:question_id",
            "method": "POST",
            "description": "Evaluate answer using LLM",
            "response": {
                "success": True,
                "evaluation": {
                    "question_id": "dsa_1",
                    "scores": {
                        "correctness": 85,
                        "completeness": 78,
                        "clarity": 90,
                        "overall": 84
                    },
                    "feedback": {
                        "strengths": ["list"],
                        "improvements": ["list"],
                        "overall": "text"
                    }
                }
            }
        },
        {
            "path": "/session/:id/summary",
            "method": "GET",
            "description": "Get complete session summary",
            "response": {
                "success": True,
                "session": {
                    "domain": "DSA",
                    "total_questions": 5,
                    "answered_questions": 3,
                    "current_index": 2,
                    "completed": False,
                    "total_time_seconds": 180.5,
                    "answers": ["array"]
                }
            }
        }
    ],
    "websocket_endpoints": [
        {
            "path": "/ws/interview/:session_id/audio",
            "description": "WebSocket for streaming audio with silence detection",
            "client_messages": {
                "audio_chunk": "binary audio data",
                "speech_detected": True,
                "speech_ended": True
            },
            "server_messages": {
                "transcript_chunk": {"text": "partial transcript", "is_final": False},
                "silence_detected": {"duration": 4.1, "trigger_auto_complete": True},
                "transcription_complete": {"full_text": "complete answer"}
            }
        }
    ]
}

print("=" * 80)
print("INTERVIEW MODE API ENDPOINTS")
print("=" * 80)

print("\n📡 REST API ENDPOINTS:\n")
for endpoint in api_spec["endpoints"]:
    print(f"{endpoint['method']} {endpoint['path']}")
    print(f"   {endpoint['description']}")
    print()

print("\n🔌 WEBSOCKET ENDPOINTS:\n")
for ws_endpoint in api_spec["websocket_endpoints"]:
    print(f"WS {ws_endpoint['path']}")
    print(f"   {ws_endpoint['description']}")
    print()

# Save API specification
with open("interview_api_spec.json", "w") as f:
    json.dump(api_spec, f, indent=2)

print("✅ API specification saved to: interview_api_spec.json")

# Express.js route implementation template
express_routes = '''
// Interview Mode Routes (Express.js + TypeScript)
import express from 'express';
import { interviewService } from '../services/interviewService';

const router = express.Router();

// Start new interview session
router.post('/session/start', async (req, res) => {
  const { domain } = req.body;
  const result = await interviewService.startSession(domain);
  res.json(result);
});

// Get current question
router.get('/session/:id/question/current', async (req, res) => {
  const { id } = req.params;
  const result = await interviewService.getCurrentQuestion(id);
  res.json(result);
});

// Navigate to next question
router.post('/session/:id/navigate/next', async (req, res) => {
  const { id } = req.params;
  const result = await interviewService.navigateNext(id);
  res.json(result);
});

// Navigate to previous question
router.post('/session/:id/navigate/previous', async (req, res) => {
  const { id } = req.params;
  const result = await interviewService.navigatePrevious(id);
  res.json(result);
});

// Submit answer
router.post('/session/:id/answer', async (req, res) => {
  const { id } = req.params;
  const { transcript, silence_duration, auto_completed } = req.body;
  const result = await interviewService.captureAnswer(id, transcript, silence_duration, auto_completed);
  res.json(result);
});

// Evaluate answer with LLM
router.post('/session/:id/evaluate/:question_id', async (req, res) => {
  const { id, question_id } = req.params;
  const result = await interviewService.evaluateAnswer(id, question_id);
  res.json(result);
});

// Get session summary
router.get('/session/:id/summary', async (req, res) => {
  const { id } = req.params;
  const result = await interviewService.getSessionSummary(id);
  res.json(result);
});

export default router;
'''

print("\n" + "=" * 80)
print("EXPRESS.JS ROUTE TEMPLATE")
print("=" * 80)
print(express_routes)

print("\n✅ Interview API endpoints defined")
print("✅ Ready for Express.js integration")

api_endpoints_defined = True
