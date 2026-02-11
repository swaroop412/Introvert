"""
Sample Data Files Generation
Creates demo transcript and facial events JSON files for testing
"""

import json

# Demo Transcript Sample
demo_transcript = [
    {
        "timestamp": 0.0,
        "text": "Hello everyone, um, thank you for joining today's presentation",
        "is_final": True,
        "confidence": 0.95
    },
    {
        "timestamp": 3.5,
        "text": "Today I want to talk about, like, the main challenges we face",
        "is_final": True,
        "confidence": 0.92
    },
    {
        "timestamp": 7.2,
        "text": "The the key issue here is scalability and performance",
        "is_final": True,
        "confidence": 0.89
    },
    {
        "timestamp": 11.0,
        "text": "You know, basically what we need to focus on is optimization",
        "is_final": True,
        "confidence": 0.94
    },
    {
        "timestamp": 15.5,
        "text": "So, well, let me explain this approach in more detail",
        "is_final": True,
        "confidence": 0.91
    },
    {
        "timestamp": 19.8,
        "text": "We implemented a solution that significantly improved throughput",
        "is_final": True,
        "confidence": 0.96
    },
    {
        "timestamp": 24.3,
        "text": "The results show, um, a fifty percent increase in efficiency",
        "is_final": True,
        "confidence": 0.93
    },
    {
        "timestamp": 28.7,
        "text": "I think this demonstrates the value of our approach clearly",
        "is_final": True,
        "confidence": 0.97
    }
]

# Demo Facial Events Sample
demo_facial_events = [
    {
        "timestamp": 0.0,
        "expression": "neutral",
        "confidence": 0.82,
        "all_expressions": {
            "neutral": 0.82,
            "happy": 0.10,
            "surprised": 0.05,
            "focused": 0.02,
            "confused": 0.01
        },
        "attention_score": 0.88
    },
    {
        "timestamp": 0.5,
        "expression": "neutral",
        "confidence": 0.85,
        "all_expressions": {
            "neutral": 0.85,
            "happy": 0.08,
            "surprised": 0.04,
            "focused": 0.02,
            "confused": 0.01
        },
        "attention_score": 0.90
    },
    {
        "timestamp": 1.0,
        "expression": "happy",
        "confidence": 0.78,
        "all_expressions": {
            "neutral": 0.15,
            "happy": 0.78,
            "surprised": 0.04,
            "focused": 0.02,
            "confused": 0.01
        },
        "attention_score": 0.92
    },
    {
        "timestamp": 1.5,
        "expression": "happy",
        "confidence": 0.81,
        "all_expressions": {
            "neutral": 0.12,
            "happy": 0.81,
            "surprised": 0.04,
            "focused": 0.02,
            "confused": 0.01
        },
        "attention_score": 0.89
    },
    {
        "timestamp": 2.0,
        "expression": "focused",
        "confidence": 0.75,
        "all_expressions": {
            "neutral": 0.18,
            "happy": 0.05,
            "surprised": 0.01,
            "focused": 0.75,
            "confused": 0.01
        },
        "attention_score": 0.95
    },
    {
        "timestamp": 2.5,
        "expression": "focused",
        "confidence": 0.79,
        "all_expressions": {
            "neutral": 0.15,
            "happy": 0.03,
            "surprised": 0.02,
            "focused": 0.79,
            "confused": 0.01
        },
        "attention_score": 0.94
    },
    {
        "timestamp": 3.0,
        "expression": "confused",
        "confidence": 0.68,
        "all_expressions": {
            "neutral": 0.20,
            "happy": 0.05,
            "surprised": 0.05,
            "focused": 0.02,
            "confused": 0.68
        },
        "attention_score": 0.82
    },
    {
        "timestamp": 3.5,
        "expression": "neutral",
        "confidence": 0.83,
        "all_expressions": {
            "neutral": 0.83,
            "happy": 0.10,
            "surprised": 0.04,
            "focused": 0.02,
            "confused": 0.01
        },
        "attention_score": 0.87
    }
]

# Demo Disfluency Events
demo_disfluency_events = [
    {
        "type": "filler_word",
        "timestamp": 0.5,
        "detail": {
            "word": "um",
            "text": "Hello everyone, um, thank you for joining today's presentation"
        }
    },
    {
        "type": "filler_word",
        "timestamp": 3.5,
        "detail": {
            "word": "like",
            "text": "Today I want to talk about, like, the main challenges we face"
        }
    },
    {
        "type": "repetition",
        "timestamp": 7.2,
        "detail": {
            "word": "the",
            "count": 2,
            "window_s": 2.0
        }
    },
    {
        "type": "filler_word",
        "timestamp": 11.0,
        "detail": {
            "word": "you know",
            "text": "You know, basically what we need to focus on is optimization"
        }
    },
    {
        "type": "filler_word",
        "timestamp": 11.0,
        "detail": {
            "word": "basically",
            "text": "You know, basically what we need to focus on is optimization"
        }
    },
    {
        "type": "pause",
        "timestamp": 14.0,
        "detail": {
            "duration_ms": 850.0,
            "end_timestamp": 14.85
        }
    },
    {
        "type": "filler_word",
        "timestamp": 15.5,
        "detail": {
            "word": "so",
            "text": "So, well, let me explain this approach in more detail"
        }
    },
    {
        "type": "filler_word",
        "timestamp": 15.5,
        "detail": {
            "word": "well",
            "text": "So, well, let me explain this approach in more detail"
        }
    },
    {
        "type": "filler_word",
        "timestamp": 24.3,
        "detail": {
            "word": "um",
            "text": "The results show, um, a fifty percent increase in efficiency"
        }
    }
]

# Demo WPM Events
demo_wpm_events = [
    {
        "timestamp": 10.0,
        "wpm": 145.0,
        "word_count": 24,
        "duration_s": 10.0,
        "target_range": "120-160",
        "status": "optimal",
        "in_target_range": True
    },
    {
        "timestamp": 20.0,
        "wpm": 138.0,
        "word_count": 23,
        "duration_s": 10.0,
        "target_range": "120-160",
        "status": "optimal",
        "in_target_range": True
    },
    {
        "timestamp": 30.0,
        "wpm": 152.0,
        "word_count": 25,
        "duration_s": 10.0,
        "target_range": "120-160",
        "status": "optimal",
        "in_target_range": True
    }
]

# Complete Session Export
complete_session = {
    "session_metadata": {
        "session_id": "demo_session_001",
        "session_start_time": 1700000000000,
        "duration_ms": 30000,
        "total_events": len(demo_transcript) + len(demo_facial_events) + len(demo_disfluency_events) + len(demo_wpm_events),
        "event_counts": {
            "transcript": len(demo_transcript),
            "expression": len(demo_facial_events),
            "filler": len([e for e in demo_disfluency_events if e['type'] == 'filler_word']),
            "pause": len([e for e in demo_disfluency_events if e['type'] == 'pause']),
            "repetition": len([e for e in demo_disfluency_events if e['type'] == 'repetition']),
            "wpm": len(demo_wpm_events)
        }
    },
    "transcripts": demo_transcript,
    "facial_events": demo_facial_events,
    "disfluency_events": demo_disfluency_events,
    "wpm_events": demo_wpm_events
}

# Print samples
print("=" * 70)
print("SAMPLE DATA FILES FOR ORATORIQ")
print("=" * 70)

print("\n📝 DEMO TRANSCRIPT SAMPLE")
print("-" * 70)
print(json.dumps(demo_transcript[:3], indent=2))
print(f"\nTotal transcript segments: {len(demo_transcript)}")

print("\n\n😊 DEMO FACIAL EVENTS SAMPLE")
print("-" * 70)
print(json.dumps(demo_facial_events[:3], indent=2))
print(f"\nTotal facial events: {len(demo_facial_events)}")

print("\n\n⚠️ DEMO DISFLUENCY EVENTS SAMPLE")
print("-" * 70)
print(json.dumps(demo_disfluency_events[:3], indent=2))
print(f"\nTotal disfluency events: {len(demo_disfluency_events)}")
print(f"  - Filler words: {len([e for e in demo_disfluency_events if e['type'] == 'filler_word'])}")
print(f"  - Repetitions: {len([e for e in demo_disfluency_events if e['type'] == 'repetition'])}")
print(f"  - Pauses: {len([e for e in demo_disfluency_events if e['type'] == 'pause'])}")

print("\n\n📊 DEMO WPM EVENTS SAMPLE")
print("-" * 70)
print(json.dumps(demo_wpm_events, indent=2))

print("\n\n📦 COMPLETE SESSION EXPORT")
print("-" * 70)
print(json.dumps(complete_session['session_metadata'], indent=2))
print(f"\nTotal events in session: {complete_session['session_metadata']['total_events']}")

print("\n" + "=" * 70)
print("✅ SAMPLE DATA FILES GENERATED")
print("=" * 70)
print("\n📁 Files to create:")
print("  1. demo_transcript.json - Sample transcript data")
print("  2. demo_facial_events.json - Sample facial expression data")
print("  3. demo_disfluency_events.json - Sample disfluency data")
print("  4. demo_wpm_events.json - Sample WPM data")
print("  5. complete_session.json - Full session export")

print("\n🎯 Usage:")
print("  - Load these files in dev mode for testing")
print("  - Use with mock providers to simulate real sessions")
print("  - Test timeline alignment and event processing")

# Export data for downstream use
sample_transcript_data = demo_transcript
sample_facial_events_data = demo_facial_events
sample_disfluency_events_data = demo_disfluency_events
sample_wpm_events_data = demo_wpm_events
sample_complete_session_data = complete_session
