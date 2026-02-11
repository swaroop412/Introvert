"""
Mock Providers for Development Mode
Provides mock implementations of STT, FER, and API services for testing without real dependencies
"""

import json
import time
import random
from typing import List, Dict, Any

class MockSTTProvider:
    """Mock Speech-to-Text provider for dev mode"""
    
    def __init__(self):
        self.demo_phrases = [
            "Hello everyone, um, today I want to talk about",
            "The main point is that, like, we need to focus on",
            "I think the the key issue here is",
            "You know, basically what we're looking at is",
            "So, well, let me explain this in more detail"
        ]
        self.current_index = 0
    
    def get_next_transcript(self, timestamp: float) -> Dict[str, Any]:
        """Get next mock transcript segment"""
        phrase = self.demo_phrases[self.current_index % len(self.demo_phrases)]
        self.current_index += 1
        
        return {
            'timestamp': timestamp,
            'text': phrase,
            'is_final': True,
            'confidence': round(random.uniform(0.85, 0.98), 2)
        }
    
    def stream_transcripts(self, duration_s: float = 10.0, interval_s: float = 2.0):
        """Stream mock transcripts for specified duration"""
        start_time = time.time()
        transcripts = []
        
        while (time.time() - start_time) < duration_s:
            current_time = time.time() - start_time
            transcript = self.get_next_transcript(current_time)
            transcripts.append(transcript)
            time.sleep(interval_s)
        
        return transcripts


class MockFERProvider:
    """Mock Facial Expression Recognition provider for dev mode"""
    
    def __init__(self):
        self.expressions = ['neutral', 'happy', 'surprised', 'focused', 'confused']
        self.current_expression = 'neutral'
    
    def get_expression_event(self, timestamp: float) -> Dict[str, Any]:
        """Get mock facial expression event"""
        # Occasionally change expression
        if random.random() < 0.3:
            self.current_expression = random.choice(self.expressions)
        
        # Generate expression confidences
        all_expressions = {}
        for expr in self.expressions:
            if expr == self.current_expression:
                all_expressions[expr] = round(random.uniform(0.65, 0.95), 2)
            else:
                all_expressions[expr] = round(random.uniform(0.01, 0.25), 2)
        
        # Normalize to sum to 1.0
        total = sum(all_expressions.values())
        all_expressions = {k: round(v/total, 2) for k, v in all_expressions.items()}
        
        return {
            'timestamp': timestamp,
            'expression': self.current_expression,
            'confidence': all_expressions[self.current_expression],
            'all_expressions': all_expressions,
            'attention_score': round(random.uniform(0.75, 0.95), 2)
        }
    
    def stream_expressions(self, duration_s: float = 10.0, interval_ms: float = 500):
        """Stream mock expression events"""
        start_time = time.time()
        expressions = []
        
        while (time.time() - start_time) < duration_s:
            current_time = time.time() - start_time
            expression = self.get_expression_event(current_time)
            expressions.append(expression)
            time.sleep(interval_ms / 1000.0)
        
        return expressions


class MockInterviewProvider:
    """Mock interview question provider for dev mode"""
    
    def __init__(self):
        self.questions = [
            {
                'id': 1,
                'category': 'behavioral',
                'text': 'Tell me about a time when you faced a challenging problem at work.',
                'difficulty': 'medium'
            },
            {
                'id': 2,
                'category': 'technical',
                'text': 'Explain how you would design a scalable web application.',
                'difficulty': 'hard'
            },
            {
                'id': 3,
                'category': 'behavioral',
                'text': 'Describe a situation where you had to work with a difficult team member.',
                'difficulty': 'medium'
            },
            {
                'id': 4,
                'category': 'technical',
                'text': 'What is your approach to debugging complex issues?',
                'difficulty': 'medium'
            },
            {
                'id': 5,
                'category': 'behavioral',
                'text': 'Give an example of when you showed leadership.',
                'difficulty': 'easy'
            }
        ]
    
    def get_questions(self, category: str = None, count: int = 3) -> List[Dict[str, Any]]:
        """Get mock interview questions"""
        if category:
            filtered = [q for q in self.questions if q['category'] == category]
        else:
            filtered = self.questions
        
        return filtered[:count]
    
    def evaluate_response(self, question_id: int, transcript: str) -> Dict[str, Any]:
        """Mock evaluation of interview response"""
        word_count = len(transcript.split())
        
        # Simple mock scoring
        content_score = min(100, (word_count / 50) * 100)
        clarity_score = random.randint(70, 95)
        relevance_score = random.randint(75, 90)
        
        overall_score = round((content_score + clarity_score + relevance_score) / 3, 1)
        
        feedback = []
        if word_count < 30:
            feedback.append("Consider providing more detailed examples")
        if word_count > 200:
            feedback.append("Try to be more concise in your responses")
        
        return {
            'question_id': question_id,
            'overall_score': overall_score,
            'scores': {
                'content': round(content_score, 1),
                'clarity': clarity_score,
                'relevance': relevance_score
            },
            'feedback': feedback,
            'word_count': word_count
        }


class MockDataGenerator:
    """Generate complete mock session data for testing"""
    
    @staticmethod
    def generate_session_data(duration_s: float = 30.0) -> Dict[str, Any]:
        """Generate complete mock session with all event types"""
        stt_provider = MockSTTProvider()
        fer_provider = MockFERProvider()
        
        session_data = {
            'session_id': f'mock_session_{int(time.time())}',
            'duration_s': duration_s,
            'transcripts': [],
            'expressions': [],
            'disfluencies': [],
            'wpm_events': []
        }
        
        # Generate transcript events (every 2 seconds)
        for t in range(0, int(duration_s), 2):
            transcript = stt_provider.get_next_transcript(float(t))
            session_data['transcripts'].append(transcript)
            
            # Add mock disfluency events for some transcripts
            if 'um' in transcript['text'].lower():
                session_data['disfluencies'].append({
                    'type': 'filler_word',
                    'timestamp': t,
                    'detail': {'word': 'um', 'text': transcript['text']}
                })
            
            if 'the the' in transcript['text'].lower():
                session_data['disfluencies'].append({
                    'type': 'repetition',
                    'timestamp': t,
                    'detail': {'word': 'the', 'count': 2}
                })
        
        # Generate expression events (every 500ms)
        for t_ms in range(0, int(duration_s * 1000), 500):
            t_s = t_ms / 1000.0
            expression = fer_provider.get_expression_event(t_s)
            session_data['expressions'].append(expression)
        
        # Generate WPM events (every 10 seconds)
        for t in range(10, int(duration_s) + 1, 10):
            wpm = random.randint(120, 160)
            session_data['wpm_events'].append({
                'timestamp': t,
                'wpm': wpm,
                'word_count': random.randint(20, 30),
                'duration_s': 10.0,
                'status': 'optimal' if 120 <= wpm <= 160 else 'too_fast'
            })
        
        return session_data


# Demo and Test
print("=" * 70)
print("MOCK PROVIDERS FOR DEV MODE")
print("=" * 70)

# Test STT Provider
print("\n📝 MOCK STT PROVIDER TEST")
print("-" * 70)
stt = MockSTTProvider()
for i in range(3):
    transcript = stt.get_next_transcript(float(i * 2))
    print(f"[{transcript['timestamp']}s] {transcript['text']}")
    print(f"  Confidence: {transcript['confidence']}")

# Test FER Provider
print("\n😊 MOCK FER PROVIDER TEST")
print("-" * 70)
fer = MockFERProvider()
for i in range(5):
    expr = fer.get_expression_event(float(i * 0.5))
    print(f"[{expr['timestamp']:.1f}s] {expr['expression']} (confidence: {expr['confidence']}, attention: {expr['attention_score']})")

# Test Interview Provider
print("\n💼 MOCK INTERVIEW PROVIDER TEST")
print("-" * 70)
interview = MockInterviewProvider()
questions = interview.get_questions(count=2)
for q in questions:
    print(f"Q{q['id']} [{q['category']}/{q['difficulty']}]: {q['text']}")

evaluation = interview.evaluate_response(1, "I faced a challenging problem when our system crashed. I debugged it systematically and fixed the issue.")
print(f"\nMock Evaluation:")
print(f"  Overall Score: {evaluation['overall_score']}/100")
print(f"  Scores: {evaluation['scores']}")

# Generate Full Session Data
print("\n📊 FULL SESSION DATA GENERATION")
print("-" * 70)
session_data = MockDataGenerator.generate_session_data(duration_s=10.0)
print(f"Generated session: {session_data['session_id']}")
print(f"  Duration: {session_data['duration_s']}s")
print(f"  Transcripts: {len(session_data['transcripts'])} events")
print(f"  Expressions: {len(session_data['expressions'])} events")
print(f"  Disfluencies: {len(session_data['disfluencies'])} events")
print(f"  WPM events: {len(session_data['wpm_events'])} events")

# Export sample data
sample_export = {
    'transcripts': session_data['transcripts'][:2],
    'expressions': session_data['expressions'][:3],
    'disfluencies': session_data['disfluencies'][:2]
}

print("\n📄 Sample JSON Output:")
print(json.dumps(sample_export, indent=2))

print("\n" + "=" * 70)
print("✅ ALL MOCK PROVIDERS READY FOR DEV MODE")
print("=" * 70)
print("\n🎯 Usage:")
print("  - Use MockSTTProvider for transcript testing")
print("  - Use MockFERProvider for expression testing")
print("  - Use MockInterviewProvider for interview mode")
print("  - Use MockDataGenerator for full session simulation")

# Export providers for downstream use
mock_stt_provider = stt
mock_fer_provider = fer
mock_interview_provider = interview
mock_data_generator = MockDataGenerator()
