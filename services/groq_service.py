import os
import json
from groq import Groq

client = None

def get_client():
    global client
    if not client:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Warning: GROQ_API_KEY not found")
            return None
        client = Groq(api_key=api_key)
    return client

async def transcribe_audio(file_path):
    client = get_client()
    if not client:
        return None
    
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(file_path), file.read()),
            model="whisper-large-v3",
            response_format="verbose_json",
        )
    return transcription

async def evaluate_interview(transcript_data, face_logs, stutter_analysis):
    client = get_client()
    if not client:
        return {"error": "Groq API key missing"}

    # Construct prompt
    prompt = f"""Analyze this interview session.

TRANSCRIPT:
{transcript_data.text}

BEHAVIORAL DATA:
- Stuttering/Repetitions detected: {stutter_analysis.get('repetition_count', 0)}
- Long Pauses (>1s): {stutter_analysis.get('long_pauses', 0)}
- Face Visibility: {face_logs.get('visibility_percentage', 0)}% of time
- Dominant Emotion: {face_logs.get('dominant_emotion', 'N/A')}

Provide a coaching evaluation in JSON format:
{{
  "feedback": {{
    "communication_style": "...",
    "body_language_note": "...",
    "improvements": ["..."]
  }},
  "scores": {{
    "clarity": <0-100>,
    "confidence": <0-100>
  }}
}}"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an interview coach. Respond in JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    return json.loads(completion.choices[0].message.content)