"""
Interview Mode Interface Implementation
Features: domain selector, question bank, Next/Prev navigation, 
per-question timer, answer capture with 4s silence auto-completion
"""

import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Question bank structure (from existing questions API)
interview_questions = {
    "DSA": [
        {"id": "dsa_1", "question": "Implement a function to reverse a linked list. Analyze time and space complexity.", "difficulty": "medium"},
        {"id": "dsa_2", "question": "Design and implement a LRU cache with O(1) operations.", "difficulty": "hard"},
        {"id": "dsa_3", "question": "Find the kth largest element in an unsorted array efficiently.", "difficulty": "medium"},
        {"id": "dsa_4", "question": "Implement a binary search tree with insert, delete, and search operations.", "difficulty": "medium"},
        {"id": "dsa_5", "question": "Detect a cycle in a directed graph using appropriate algorithms.", "difficulty": "medium"}
    ],
    "Web": [
        {"id": "web_1", "question": "Explain the difference between var, let, and const in JavaScript.", "difficulty": "easy"},
        {"id": "web_2", "question": "What is the event loop in JavaScript? Explain async operations.", "difficulty": "medium"},
        {"id": "web_3", "question": "Implement a debounce function that delays execution.", "difficulty": "medium"},
        {"id": "web_4", "question": "Explain CORS and how to handle it. Provide examples.", "difficulty": "medium"},
        {"id": "web_5", "question": "What are React hooks? Implement a custom hook for form validation.", "difficulty": "medium"}
    ],
    "Python": [
        {"id": "python_1", "question": "Explain Python's GIL and its effect on multithreading.", "difficulty": "medium"},
        {"id": "python_2", "question": "What are decorators? Implement a caching decorator.", "difficulty": "medium"},
        {"id": "python_3", "question": "Explain generators and yield. Implement a data pipeline.", "difficulty": "medium"},
        {"id": "python_4", "question": "Implement async/await for concurrent API calls.", "difficulty": "medium"},
        {"id": "python_5", "question": "Explain context managers and implement one.", "difficulty": "medium"}
    ]
}

# Interview session state
interview_session = {
    "domain": None,
    "current_question_index": 0,
    "questions": [],
    "answers": [],
    "start_time": None,
    "question_start_time": None,
    "completed": False
}

print("=" * 80)
print("INTERVIEW MODE INTERFACE - CORE FUNCTIONALITY")
print("=" * 80)

# Domain selector function
def select_domain(domain: str) -> Dict:
    """Initialize interview session with selected domain"""
    if domain not in interview_questions:
        return {"success": False, "error": f"Invalid domain. Choose from: {list(interview_questions.keys())}"}
    
    interview_session["domain"] = domain
    interview_session["questions"] = interview_questions[domain]
    interview_session["current_question_index"] = 0
    interview_session["answers"] = []
    interview_session["start_time"] = datetime.now().isoformat()
    interview_session["question_start_time"] = datetime.now().isoformat()
    interview_session["completed"] = False
    
    return {
        "success": True,
        "domain": domain,
        "total_questions": len(interview_questions[domain]),
        "first_question": interview_questions[domain][0]
    }

# Get current question
def get_current_question() -> Dict:
    """Retrieve current question with metadata"""
    if not interview_session["domain"]:
        return {"success": False, "error": "No domain selected"}
    
    idx = interview_session["current_question_index"]
    questions = interview_session["questions"]
    
    if idx >= len(questions):
        return {"success": False, "error": "No more questions", "completed": True}
    
    question = questions[idx]
    time_elapsed = (datetime.now() - datetime.fromisoformat(interview_session["question_start_time"])).total_seconds()
    
    return {
        "success": True,
        "question": question,
        "question_number": idx + 1,
        "total_questions": len(questions),
        "time_elapsed": round(time_elapsed, 1),
        "has_previous": idx > 0,
        "has_next": idx < len(questions) - 1
    }

# Navigation functions
def navigate_next() -> Dict:
    """Move to next question"""
    if not interview_session["domain"]:
        return {"success": False, "error": "No domain selected"}
    
    idx = interview_session["current_question_index"]
    questions = interview_session["questions"]
    
    if idx >= len(questions) - 1:
        interview_session["completed"] = True
        return {"success": False, "error": "Already at last question", "completed": True}
    
    interview_session["current_question_index"] += 1
    interview_session["question_start_time"] = datetime.now().isoformat()
    
    return {**get_current_question(), "navigated": "next"}

def navigate_previous() -> Dict:
    """Move to previous question"""
    if not interview_session["domain"]:
        return {"success": False, "error": "No domain selected"}
    
    idx = interview_session["current_question_index"]
    
    if idx <= 0:
        return {"success": False, "error": "Already at first question"}
    
    interview_session["current_question_index"] -= 1
    interview_session["question_start_time"] = datetime.now().isoformat()
    
    return {**get_current_question(), "navigated": "previous"}

# Answer capture with silence detection
def capture_answer(transcript: str, silence_duration: float = 0.0, auto_completed: bool = False) -> Dict:
    """Capture answer for current question"""
    if not interview_session["domain"]:
        return {"success": False, "error": "No domain selected"}
    
    idx = interview_session["current_question_index"]
    question = interview_session["questions"][idx]
    time_spent = (datetime.now() - datetime.fromisoformat(interview_session["question_start_time"])).total_seconds()
    
    answer_record = {
        "question_id": question["id"],
        "question_text": question["question"],
        "answer_transcript": transcript,
        "time_spent_seconds": round(time_spent, 1),
        "auto_completed": auto_completed,
        "silence_duration": silence_duration,
        "timestamp": datetime.now().isoformat()
    }
    
    # Update or append answer
    existing_idx = next((i for i, a in enumerate(interview_session["answers"]) if a["question_id"] == question["id"]), None)
    if existing_idx is not None:
        interview_session["answers"][existing_idx] = answer_record
    else:
        interview_session["answers"].append(answer_record)
    
    return {
        "success": True,
        "answer_captured": True,
        "question_id": question["id"],
        "auto_completed": auto_completed,
        "time_spent": round(time_spent, 1)
    }

# Silence detection trigger
def check_silence_trigger(last_speech_time: datetime, threshold_seconds: float = 4.0) -> bool:
    """Check if silence duration exceeds threshold for auto-completion"""
    silence_duration = (datetime.now() - last_speech_time).total_seconds()
    return silence_duration >= threshold_seconds

# LLM evaluation placeholder
def evaluate_answer(question_id: str, answer_text: str) -> Dict:
    """Send answer to LLM for evaluation (placeholder for Groq integration)"""
    # Find the question and answer
    answer_record = next((a for a in interview_session["answers"] if a["question_id"] == question_id), None)
    if not answer_record:
        return {"success": False, "error": "Answer not found"}
    
    question_text = answer_record["question_text"]
    
    # Placeholder for LLM call - will integrate with Groq
    evaluation_prompt = f"""
    Evaluate the following interview answer:
    
    Question: {question_text}
    
    Answer: {answer_text}
    
    Provide:
    1. Correctness score (0-100)
    2. Completeness score (0-100) 
    3. Clarity score (0-100)
    4. Key strengths
    5. Areas for improvement
    6. Overall feedback
    """
    
    # Mock evaluation result
    evaluation = {
        "question_id": question_id,
        "scores": {
            "correctness": 85,
            "completeness": 78,
            "clarity": 90,
            "overall": 84
        },
        "feedback": {
            "strengths": ["Clear explanation", "Good examples", "Correct approach"],
            "improvements": ["Could mention edge cases", "More depth on time complexity"],
            "overall": "Strong answer demonstrating good understanding of the concept."
        },
        "evaluation_timestamp": datetime.now().isoformat(),
        "llm_model": "groq/llama3-70b (placeholder)"
    }
    
    return {
        "success": True,
        "evaluation": evaluation
    }

# Session summary
def get_session_summary() -> Dict:
    """Get complete interview session summary"""
    if not interview_session["domain"]:
        return {"success": False, "error": "No active session"}
    
    total_time = 0
    if interview_session["start_time"]:
        total_time = (datetime.now() - datetime.fromisoformat(interview_session["start_time"])).total_seconds()
    
    return {
        "success": True,
        "session": {
            "domain": interview_session["domain"],
            "total_questions": len(interview_session["questions"]),
            "answered_questions": len(interview_session["answers"]),
            "current_index": interview_session["current_question_index"],
            "completed": interview_session["completed"],
            "total_time_seconds": round(total_time, 1),
            "answers": interview_session["answers"]
        }
    }

print("\n✅ CORE FUNCTIONS IMPLEMENTED:\n")
print("1. select_domain(domain) - Initialize interview with domain")
print("2. get_current_question() - Get current question with timer")
print("3. navigate_next() - Move to next question")
print("4. navigate_previous() - Move to previous question")
print("5. capture_answer(transcript, silence_duration, auto_completed) - Save answer")
print("6. check_silence_trigger(last_speech_time, threshold) - Detect 4s silence")
print("7. evaluate_answer(question_id, answer_text) - LLM evaluation call")
print("8. get_session_summary() - Full session data")

# Demo workflow
print("\n" + "=" * 80)
print("DEMO WORKFLOW")
print("=" * 80)

# Step 1: Select domain
print("\n1. Selecting domain: DSA")
result = select_domain("DSA")
print(f"   ✓ Domain selected: {result['domain']}")
print(f"   ✓ Total questions: {result['total_questions']}")
print(f"   ✓ First question: {result['first_question']['question'][:60]}...")

# Step 2: Get current question
print("\n2. Getting current question")
current = get_current_question()
print(f"   ✓ Question {current['question_number']}/{current['total_questions']}")
print(f"   ✓ Question: {current['question']['question'][:60]}...")
print(f"   ✓ Difficulty: {current['question']['difficulty']}")

# Step 3: Simulate answer capture
print("\n3. Capturing answer (simulating 4s silence auto-complete)")
import time
time.sleep(0.1)  # Simulate some time passing
answer_result = capture_answer(
    transcript="A linked list can be reversed iteratively by maintaining three pointers...",
    silence_duration=4.2,
    auto_completed=True
)
print(f"   ✓ Answer captured: {answer_result['success']}")
print(f"   ✓ Auto-completed: {answer_result['auto_completed']}")
print(f"   ✓ Time spent: {answer_result['time_spent']}s")

# Step 4: Evaluate answer
print("\n4. Evaluating answer with LLM")
eval_result = evaluate_answer("dsa_1", answer_result.get("answer_transcript", ""))
print(f"   ✓ Evaluation complete")
print(f"   ✓ Overall score: {eval_result['evaluation']['scores']['overall']}/100")
print(f"   ✓ Feedback: {eval_result['evaluation']['feedback']['overall'][:60]}...")

# Step 5: Navigate to next question
print("\n5. Navigating to next question")
next_result = navigate_next()
print(f"   ✓ Moved to question {next_result['question_number']}/{next_result['total_questions']}")
print(f"   ✓ Question: {next_result['question']['question'][:60]}...")

# Step 6: Session summary
print("\n6. Session summary")
summary = get_session_summary()
print(f"   ✓ Domain: {summary['session']['domain']}")
print(f"   ✓ Progress: {summary['session']['answered_questions']}/{summary['session']['total_questions']}")
print(f"   ✓ Total time: {summary['session']['total_time_seconds']}s")

print("\n" + "=" * 80)
print("INTERVIEW MODE INTERFACE - READY FOR INTEGRATION")
print("=" * 80)

print("\n🎯 NEXT STEPS FOR FULL IMPLEMENTATION:")
print("1. Integrate with Groq Whisper STT for real-time transcription")
print("2. Implement WebSocket for streaming audio → transcript pipeline")
print("3. Add silence detection in audio stream (4s threshold)")
print("4. Connect evaluate_answer() to Groq LLM API")
print("5. Build React frontend with these functions via API endpoints")
print("6. Add timer display component with per-question tracking")
print("7. Implement question bank UI panel with Next/Prev buttons")
print("8. Add evaluation results display after each question")

interview_mode_ready = True
