"""
Simplified Modular Backend - No real-time updates needed
Run with: uvicorn backend:app --reload
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from datetime import datetime
from pathlib import Path

# Import your existing agents
from agents.curriculum_agent import CurriculumAgent
from agents.character_agent import CharacterAgent
from agents.script_agent import ScriptAgent
from agents.voice_agent import VoiceAgent
from agents.visual_agent import VisualAgent
from utils.db import init_db
from utils.qa import run_video_qa

# Initialize FastAPI

# ==================== Initialize on Startup ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize everything when server starts"""
    global curriculum_agent, character_agent, script_agent, voice_agent, visual_agent

    print("🚀 Starting Content Factory Backend...")
    init_db()

    try:
        curriculum_agent = CurriculumAgent()
        character_agent = CharacterAgent()
        script_agent = ScriptAgent()
        voice_agent = VoiceAgent()
        visual_agent = VisualAgent()
        print("✅ All agents initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing agents: {e}")

    yield  # Application runs here

app = FastAPI(title="Content Factory API", version="2.0.0", lifespan=lifespan)

# Allow Streamlit to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
curriculum_store = {}
character_store = {}
script_store = {}
voice_store = {}
video_store = {}
job_store = {}

# Agent instances
curriculum_agent = None
character_agent = None
script_agent = None
voice_agent = None
visual_agent = None

# ==================== Request Models ====================

class CurriculumRequest(BaseModel):
    topic: str
    num_lessons: int = 1

class CharacterRequest(BaseModel):
    name: str

class ScriptRequest(BaseModel):
    curriculum_id: str
    character_id: str

class VoiceRequest(BaseModel):
    script_id: str
    character_id: str

class VideoRequest(BaseModel):
    script_id: str
    character_id: str
    voice_id: str

class PipelineRequest(BaseModel):
    topic: str
    character_name: str = "Zara"
    num_lessons: int = 1

# ==================== Individual API Endpoints ====================
# Health Check
@app.get("/")
async def root():
    return {"message": "Content Factory API is running!", "status": "healthy"}

# Generate Curriculum 
@app.post("/api/curriculum/generate")
async def generate_curriculum(request: CurriculumRequest):
    """Generate curriculum for a topic"""
    curriculum_id = str(uuid.uuid4())
    
    print(f"📚 Generating curriculum for: {request.topic}")
    lessons = curriculum_agent.run(request.topic)
    lessons = lessons[:request.num_lessons]
    
    curriculum_store[curriculum_id] = {
        "id": curriculum_id,
        "topic": request.topic,
        "lessons": lessons
    }
    
    return {"curriculum_id": curriculum_id, "lessons": lessons}

# Create Character
@app.post("/api/character/create")
async def create_character(request: CharacterRequest):
    """Create or get character"""
    character_id = str(uuid.uuid4())
    
    print(f"🎭 Creating character: {request.name}")
    character = character_agent.run(request.name)
    
    character_store[character_id] = {
        "id": character_id,
        "data": character
    }
    
    return {"character_id": character_id, "character": character}

# Generate Script using curriculum_id and character_id
@app.post("/api/script/generate")
async def generate_script(request: ScriptRequest):
    """Generate scripts for lessons"""
    script_id = str(uuid.uuid4())
    
    curriculum = curriculum_store[request.curriculum_id]
    character = character_store[request.character_id]["data"]
    
    print(f"📝 Generating scripts...")
    scripts = script_agent.run({
        "character": character,
        "lessons": curriculum["lessons"]
    })
    
    script_store[script_id] = {
        "id": script_id,
        "scripts": scripts
    }
    
    return {"script_id": script_id, "scripts": scripts}

# Generate Voice using script_id and character_id
@app.post("/api/voice/generate")
async def generate_voice(request: VoiceRequest):
    """Generate voice for scripts"""
    voice_id = str(uuid.uuid4())
    
    script_data = script_store[request.script_id]
    character = character_store[request.character_id]["data"]
    
    print(f"🎤 Generating voice...")
    voice_results = []
    
    for script_item in script_data["scripts"]:
        voice_result = voice_agent.run({
            "character": character,
            "lesson_title": script_item["lesson"],
            "script": script_item["script"]
        })
        voice_results.append({
            "lesson": script_item["lesson"],
            "audio_path": voice_result["audio_path"],
            "timing_data": voice_result.get("timing", None)
        })
    
    voice_store[voice_id] = {"voice_data": voice_results}
    
    return {"voice_id": voice_id}

# Generate Video using script_id and character_id and voice_id
@app.post("/api/video/generate")
async def generate_video(request: VideoRequest):
    """Generate video from script and voice"""
    video_id = str(uuid.uuid4())
    
    script_data = script_store[request.script_id]
    character = character_store[request.character_id]["data"]
    voice_data = voice_store[request.voice_id]
    
    print(f"🎬 Generating video...")
    videos = []
    
    for script_item, voice_item in zip(script_data["scripts"], voice_data["voice_data"]):
        video_input = {
            "character": character,
            "lesson_title": script_item["lesson"],
            "script": script_item["script"],
            "voice_path": voice_item["audio_path"],
            "overlay_data": script_item.get("overlay_data", {})
        }
        
        if voice_item.get("timing_data"):
            video_input["timing"] = voice_item["timing_data"]
        
        video_path = visual_agent.run(video_input)
        
        videos.append({
            "lesson": script_item["lesson"],
            "video_path": video_path,
            "video_filename": Path(video_path).name,
            "audio_path": voice_item["audio_path"],
            "audio_filename": Path(voice_item["audio_path"]).name
        })
    
    video_store[video_id] = {"videos": videos}
    
    return {"video_id": video_id, "videos": videos}


# ==================== Pipeline Endpoint Start - Endpoint used in the frontend ====================

@app.post("/api/pipeline/start")
async def start_pipeline(request: PipelineRequest, background_tasks: BackgroundTasks):
    """Start the full pipeline"""
    job_id = str(uuid.uuid4())
    
    job_store[job_id] = {
        "id": job_id,
        "status": "processing",
        "topic": request.topic,
        "result": None,
        "error": None,
        "curriculum_info": None
    }
    
    background_tasks.add_task(
        run_pipeline,
        job_id,
        request.topic,
        request.character_name,
        request.num_lessons
    )
    
    return {"job_id": job_id}

async def run_pipeline(job_id: str, topic: str, character_name: str, num_lessons: int):
    """Run the full pipeline with comprehensive logging"""
    logs = []  # List to collect all logs to show at the end
    
    def add_log(message: str):
        logs.append({
            "timestamp": datetime.now().isoformat(),
            "message": message
        })
        print(message)
    
    try:
        add_log(f"🚀 Starting pipeline for topic: {topic}")
        
        # 1. Curriculum
        add_log(f"📚 Generating curriculum for: {topic}")
        curr_req = CurriculumRequest(topic=topic, num_lessons=num_lessons)
        curr_resp = await generate_curriculum(curr_req)
        curriculum_id = curr_resp["curriculum_id"]
        add_log(f"✅ Curriculum ready: {len(curr_resp['lessons'])} lesson(s)")
        
        # Store curriculum info for frontend
        job_store[job_id]["curriculum_info"] = {
            "lessons": [{"title": l["title"], "summary": l["summary"]} 
                       for l in curr_resp["lessons"]]
        }
        
        # 2. Character
        add_log(f"🎭 Configuring character: {character_name}")
        char_req = CharacterRequest(name=character_name)
        char_resp = await create_character(char_req)
        character_id = char_resp["character_id"]
        character = char_resp["character"]
        add_log(f"✅ Character configured: {character['name']} ({character['gender']})")
        
        # Store character info
        job_store[job_id]["character_info"] = {
            "name": character["name"],
            "gender": character["gender"],
            "voice_style": character["voice_style"]
        }
        
        # 3. Scripts
        add_log(f"📝 Generating scripts with emotions and overlays...")
        script_req = ScriptRequest(curriculum_id=curriculum_id, character_id=character_id)
        script_resp = await generate_script(script_req)
        script_id = script_resp["script_id"]
        add_log(f"✅ Scripts ready with overlay data")
        
        # 4. Voice
        add_log(f"🎤 Creating expressive voice narration...")
        voice_req = VoiceRequest(script_id=script_id, character_id=character_id)
        voice_resp = await generate_voice(voice_req)
        voice_id = voice_resp["voice_id"]
        add_log(f"✅ Voice synthesis complete with timing data")
        
        # 5. Video
        add_log(f"🎬 Generating video with synchronized overlays...")
        video_req = VideoRequest(script_id=script_id, character_id=character_id, voice_id=voice_id)
        video_resp = await generate_video(video_req)
        add_log(f"✅ Video generation complete")
        
        # 6. QA
        try:
            add_log(f"🔍 Running QA checks...")
            
            # Get all the data needed for QA
            script_data = script_store[script_id]
            voice_data = voice_store[voice_id]
            
            qa_warnings = []
            for idx, script_item in enumerate(script_data["scripts"]):
                # Prepare complete data for QA
                qa_script_item = {
                    "lesson": script_item["lesson"],
                    "script": script_item["script"],
                    "overlay_data": script_item.get("overlay_data", {}),
                    "character": character,  # Pass character data
                    "timing_data": voice_data["voice_data"][idx].get("timing_data") if idx < len(voice_data["voice_data"]) else None
                }
                
                # Parse slides for QA
                slides = None
                try:
                    from agents.visual_agent.script_parser import ScriptParser
                    parser = ScriptParser()
                    slides = parser.parse_script_to_slides(script_item["script"], character["name"])
                except:
                    slides = None
                
                # Run QA
                qa_report = run_video_qa(qa_script_item, slides=slides, output_dir="logs")
                
                # Count warnings
                warnings = [line for line in qa_report if "⚠️" in line]
                if warnings:
                    qa_warnings.extend(warnings)
            
            if qa_warnings:
                add_log(f"⚠️ QA found {len(qa_warnings)} warning(s)")
                add_log(f"✅ Overlay collisions are automatically handled in the renderer")
            else:
                add_log(f"✅ QA checks passed successfully")
                
        except Exception as qa_error:
            add_log(f"ℹ️ QA checks skipped: {str(qa_error)}")
        
        # Done
        add_log(f"🎉 Successfully generated {len(video_resp['videos'])} video(s)")
        
        job_store[job_id]["status"] = "completed"
        job_store[job_id]["result"] = video_resp["videos"]
        job_store[job_id]["logs"] = logs  # Add all logs to job data
        
        print(f"✅ Pipeline completed for job: {job_id}")
        
    except Exception as e:
        add_log(f"❌ Pipeline failed: {str(e)}")
        print(f"❌ Pipeline failed: {str(e)}")
        job_store[job_id]["status"] = "failed"
        job_store[job_id]["error"] = str(e)
        job_store[job_id]["logs"] = logs

# =============================== Pipeline End ===============================

@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    """Get job status - simplified"""
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_store[job_id]

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download file"""
    file_path = Path("output") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    media_type = "video/mp4" if filename.endswith('.mp4') else "audio/mpeg"
    
    return FileResponse(
        path=str(file_path), 
        media_type=media_type, 
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/stream/{filename}")
async def stream_video(filename: str):
    """Stream video file"""
    file_path = Path("output") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    def iterfile():
        with open(file_path, 'rb') as f:
            yield from f
    
    return StreamingResponse(iterfile(), media_type="video/mp4")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)