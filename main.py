import os
import shutil
from fastapi import FastAPI, WebSocket, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from services.cv_service import VideoAnalyzer
from services.groq_service import transcribe_audio, evaluate_interview
from dotenv import load_dotenv
import json

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

video_analyzer = VideoAnalyzer()

# Store session data in memory (simple version)
session_face_logs = []

@app.websocket("/ws/video")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Analyze frame
            result = video_analyzer.analyze_frame(data)
            # Log result
            session_face_logs.append(result)
            
            await websocket.send_json(result)
    except Exception as e:
        print(f"WS Error: {e}")

@app.post("/api/analyze")
async def analyze_session(audio: UploadFile = File(...)):
    # Save audio
    file_location = f"uploads/{audio.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(audio.file, file_object)
    
    # 1. Transcribe
    transcript = await transcribe_audio(file_location)
    if not transcript:
        return {"error": "Transcription failed"}
    
    # 2. Analyze Stuttering/Pauses from transcript segments
    segments = transcript.segments
    long_pauses = 0
    repetitions = 0
    
    for i in range(len(segments) - 1):
        gap = segments[i+1]['start'] - segments[i]['end']
        if gap > 1.0:
            long_pauses += 1
            
    # Simple repetition check (consecutive identical words)
    words = transcript.text.split()
    for i in range(len(words) - 1):
        if words[i].lower() == words[i+1].lower():
            repetitions += 1

    # 3. Face Stats
    face_detected_count = sum(1 for log in session_face_logs if log.get('face_detected'))
    total_frames = len(session_face_logs) if len(session_face_logs) > 0 else 1
    visibility = round((face_detected_count / total_frames) * 100, 1)
    
    # Aggregate emotions
    emotions_list = [log.get('dominant_emotion') for log in session_face_logs if log.get('dominant_emotion')]
    dominant_session_emotion = max(set(emotions_list), key=emotions_list.count) if emotions_list else "neutral"
    
    # 4. LLM Evaluation
    stutter_analysis = {"repetition_count": repetitions, "long_pauses": long_pauses}
    face_stats = {"visibility_percentage": visibility, "dominant_emotion": dominant_session_emotion}
    
    evaluation = await evaluate_interview(transcript, face_stats, stutter_analysis)
    
    # Cleanup logs for next session (simple demo logic)
    session_face_logs.clear()
    
    return {
        "transcript": transcript.text,
        "analysis": stutter_analysis,
        "face_stats": face_stats,
        "evaluation": evaluation
    }

@app.get("/")
def read_root():
    return {"message": "Go to /static/index.html"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)