"""
Simple FastAPI backend for Content Factory with real-time status updates
Run with: - uvicorn backend:app --reload
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid
from datetime import datetime
from pathlib import Path

# Import your existing agents
from agents.curriculum_agent import CurriculumAgent
from agents.character_agent import CharacterAgent
from agents.script_agent import ScriptAgent
from agents.voice_agent import VoiceAgent
from agents.visual_agent import VisualAgent
from coordinator import CoordinatorAgent
from utils.db import init_db
from utils.qa import run_video_qa

# Initialize FastAPI
app = FastAPI(title="Content Factory API", version="1.0.0")

# Allow Streamlit to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage for jobs
jobs_store = {}

# Initialize your existing coordinator
coordinator = CoordinatorAgent()

# ==================== Request Models ====================

class GenerateVideoRequest(BaseModel):
    topic: str
    character_name: str = "Zara"
    num_lessons: int = 1
    character_gender: Optional[str] = None
    character_description: Optional[str] = None
    voice_style: Optional[str] = None

# ==================== Initialize on Startup ====================

@app.on_event("startup")
async def startup():
    """Initialize everything when server starts"""
    print("🚀 Starting Content Factory Backend...")
    
    # Initialize database
    init_db()
    
    # Register all agents with coordinator
    try:
        coordinator.register_agent("curriculum", CurriculumAgent())
        coordinator.register_agent("character", CharacterAgent())
        coordinator.register_agent("script", ScriptAgent())
        coordinator.register_agent("voice", VoiceAgent())
        coordinator.register_agent("visual", VisualAgent())
        print("✅ All agents registered successfully!")
    except Exception as e:
        print(f"❌ Error registering agents: {e}")

# ==================== Main Endpoints ====================

@app.get("/")
async def root():
    """Test endpoint"""
    return {"message": "Content Factory API is running!", "status": "healthy"}

@app.post("/api/generate")
async def generate_video(request: GenerateVideoRequest, background_tasks: BackgroundTasks):
    """
    Main endpoint - generates video from topic
    """
    job_id = str(uuid.uuid4())
    
    # Store initial job status with detailed progress tracking
    jobs_store[job_id] = {
        "id": job_id,
        "status": "initializing",
        "current_step": "Starting pipeline...",
        "progress": 0,
        "topic": request.topic,
        "character_name": request.character_name,
        "num_lessons": request.num_lessons,
        "created_at": datetime.now().isoformat(),
        "logs": [],
        "result": None,
        "error": None,
        "character_info": None,
        "curriculum_info": None,
        "script_preview": None
    }
    
    # Run pipeline in background
    background_tasks.add_task(
        run_pipeline,
        job_id,
        request.topic,
        request.character_name,
        request.num_lessons,
    )
    
    return {"job_id": job_id, "message": "Video generation started!"}

def update_job_status(job_id: str, status: str, step: str, progress: int, log_entry: str = None):
    """Helper function to update job status with logging"""
    jobs_store[job_id]["status"] = status
    jobs_store[job_id]["current_step"] = step
    jobs_store[job_id]["progress"] = progress
    jobs_store[job_id]["updated_at"] = datetime.now().isoformat()
    
    if log_entry:
        jobs_store[job_id]["logs"].append({
            "timestamp": datetime.now().isoformat(),
            "message": log_entry,
            "step": status
        })

async def run_pipeline(job_id: str, topic: str, character_name: str, num_lessons: int):
    """
    Pipeline with detailed status updates for frontend
    """
    try:
        # 1. Generate Curriculum
        update_job_status(job_id, "generating_curriculum", 
                         "Creating lesson plan...", 10,
                         f"📚 Generating curriculum for topic: {topic}")
        
        print(f"\n📚 Generating curriculum for: {topic}")
        curriculum = coordinator.run_agent("curriculum", topic)
        curriculum = curriculum[:num_lessons]
        
        # Store curriculum info for frontend
        jobs_store[job_id]["curriculum_info"] = {
            "lessons": [{"title": lesson["title"], "summary": lesson["summary"]} 
                       for lesson in curriculum]
        }
        
        update_job_status(job_id, "curriculum_ready", 
                         f"Created {len(curriculum)} lesson(s)", 20,
                         f"✅ Curriculum ready: {len(curriculum)} lesson(s)")
        
        # 2. Create/Get Character
        update_job_status(job_id, "creating_character", 
                         f"Setting up character: {character_name}", 25,
                         f"🎭 Creating character: {character_name}")
        
        print(f"\n🎭 Creating character: {character_name}")
        character = coordinator.run_agent("character", character_name)
        
        # Store character info for frontend
        jobs_store[job_id]["character_info"] = {
            "name": character["name"],
            "gender": character["gender"],
            "voice_style": character["voice_style"],
            "avatar_id": character.get("avatar_id", 1)
        }
        
        update_job_status(job_id, "character_ready", 
                         f"Character ready: {character['name']}", 30,
                         f"✅ Character configured: {character['name']} ({character['gender']})")
        
        # 3. Generate Scripts
        update_job_status(job_id, "generating_scripts", 
                         "Writing educational scripts...", 35,
                         f"📝 Generating scripts with emotions and overlays...")
        
        print(f"\n📝 Generating scripts...")
        scripts = coordinator.run_agent("script", {
            "character": character,
            "lessons": curriculum
        })
        
        # Store script preview
        if scripts and len(scripts) > 0:
            script_text = scripts[0]["script"]
            jobs_store[job_id]["script_preview"] = script_text[:500] + "..." if len(script_text) > 500 else script_text
        
        update_job_status(job_id, "scripts_ready", 
                         f"Scripts generated for {len(scripts)} lesson(s)", 50,
                         f"✅ Scripts ready with overlay data")
        
        # 4. Generate Voice
        update_job_status(job_id, "generating_voice", 
                         "Synthesizing voice narration...", 55,
                         f"🎤 Creating expressive voice narration...")
        
        for idx, script_item in enumerate(scripts):
            progress = 55 + (15 * (idx + 1) / len(scripts))
            update_job_status(job_id, "generating_voice", 
                            f"Voice synthesis: Lesson {idx+1}/{len(scripts)}", int(progress))
            
            print(f"\n🎤 Generating voice for lesson {idx+1}...")
            voice_result = coordinator.run_agent("voice", {
                "character": character,
                "lesson_title": script_item["lesson"],
                "script": script_item["script"]
            })
            script_item["voice_path"] = voice_result["audio_path"]
            script_item["timing_data"] = voice_result.get("timing", None)
        
        update_job_status(job_id, "voice_ready", 
                         "Voice narration complete", 70,
                         f"✅ Voice synthesis complete with timing data")
        
        # 5. Generate Video
        update_job_status(job_id, "generating_video", 
                         "Creating video with overlays...", 75,
                         f"🎬 Generating video with synchronized overlays...")
        
        videos = []
        for idx, script_item in enumerate(scripts):
            progress = 75 + (20 * (idx + 1) / len(scripts))
            update_job_status(job_id, "generating_video", 
                            f"Video generation: Lesson {idx+1}/{len(scripts)}", int(progress))
            
            print(f"\n🎬 Generating video for lesson {idx+1}...")
            video_input = {
                "character": character,
                "lesson_title": script_item["lesson"],
                "script": script_item["script"],
                "voice_path": script_item["voice_path"],
                "overlay_data": script_item.get("overlay_data", {})
            }
            
            if script_item.get("timing_data"):
                video_input["timing"] = script_item["timing_data"]
            
            video_path = coordinator.run_agent("visual", video_input)
            
            # The video_path already has audio included from your visual_agent
            # Get just the filename for the API
            video_filename = Path(video_path).name
            audio_filename = Path(script_item["voice_path"]).name
            
            videos.append({
                "lesson": script_item["lesson"],
                "video_path": video_path,
                "video_filename": video_filename,
                "audio_path": script_item["voice_path"],
                "audio_filename": audio_filename,
                "has_audio": True  # Confirm video has audio
            })
            
            # Run QA
            try:
                run_video_qa(script_item, output_dir="logs")
            except:
                pass
        
        # Update job with results
        update_job_status(job_id, "completed", 
                         "Video generation complete!", 100,
                         f"🎉 Successfully generated {len(videos)} video(s)")
        
        jobs_store[job_id]["result"] = videos
        print(f"\n✅ Job {job_id} completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Job {job_id} failed: {str(e)}")
        update_job_status(job_id, "failed", 
                         f"Error: {str(e)}", 0,
                         f"❌ Pipeline failed: {str(e)}")
        jobs_store[job_id]["error"] = str(e)

@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    """Check the status of a video generation job with detailed progress"""
    if job_id not in jobs_store:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs_store[job_id]

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download generated video or audio file"""
    file_path = Path("output") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type
    if filename.endswith('.mp4'):
        media_type = "video/mp4"
    elif filename.endswith('.mp3'):
        media_type = "audio/mpeg"
    else:
        media_type = "application/octet-stream"
    
    return FileResponse(
        path=str(file_path), 
        media_type=media_type, 
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/stream/{filename}")
async def stream_video(filename: str):
    """Stream video file for web player"""
    file_path = Path("output") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    def iterfile():
        with open(file_path, 'rb') as f:
            yield from f
    
    return StreamingResponse(iterfile(), media_type="video/mp4")

# ==================== Run the Server ====================

if __name__ == "__main__":
    import uvicorn
    
    print("""
    ====================================
    🎬 CONTENT FACTORY BACKEND 🎬
    ====================================
    
    Starting server...
    API will be available at: http://localhost:8000
    
    Test endpoints:
    - http://localhost:8000/ (health check)
    - http://localhost:8000/docs (API documentation)
    
    To generate a video, send a POST request to:
    http://localhost:8000/api/generate
    
    Press Ctrl+C to stop the server.
    ====================================
    """)
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)