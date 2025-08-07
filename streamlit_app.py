"""
Streamlit Frontend for Content Factory
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import requests
import time
from typing import Dict, Optional

# Configure page
st.set_page_config(
    page_title="Content Factory - AI Video Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_URL = "http://localhost:8000"

# --- Custom CSS ---
st.markdown("""
<style>
  /* Main container */
    .main {
        padding: 3rem;
    }
    
    /* Success message */
    .success-box {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
        color: #fff;
        padding: 0.5rem 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .info-card {
        background: #f7f8fa;
        border-left: 3px solid #7367f0;
        padding: 0.6rem 1rem;      
        border-radius: 8px;
        margin: 0.7rem 0 0.9rem 0;   
        color: #23272f;
        box-shadow: 0 1px 4px rgba(80,70,220,0.045);
        transition: box-shadow 0.2s;
    }
    .info-card:hover {
        box-shadow: 0 2px 8px rgba(80,70,220,0.11);
    }
    .info-card h4 {
        color: #7367f0;
        margin-bottom: 0.25rem;     
        font-size: 1.10rem;
        font-weight: 600;
        letter-spacing: 0.01em;
    }
    .info-card p {
        color: #222;
        font-size: 0.99rem;        
        margin: 0.18rem 0 0.18rem 0;
        line-height: 1.36;
    }
    .info-card strong {
        color: #393a77;
        font-weight: 600;
    }


    .download-btn {
        background: #fff !important;
        color: #111 !important;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        text-decoration: none !important;
        display: inline-block;
        margin: 1rem 0;
        transition: background 0.3s, color 0.3s;
        text-align: center;
        font-weight: 600;
        border: 2px solid #111;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .download-btn:hover, .download-btn:focus {
        background: #DDD !important;
        text-decoration: none !important;
    }
    .download-btn:active {
        background: #222 !important;
        color: #fff !important;
    }
    a.download-btn, a.download-btn:visited, a.download-btn:active {
        color: #111 !important;
        text-decoration: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Session state ---
if 'job_id' not in st.session_state:
    st.session_state.job_id = None
if 'job_status' not in st.session_state:
    st.session_state.job_status = None
if 'video_generated' not in st.session_state:
    st.session_state.video_generated = False

def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_URL}/")
        return response.status_code == 200
    except:
        return False

def start_video_generation(topic: str, character_name: str, num_lessons: int) -> Optional[str]:
    """Start video generation pipeline"""
    try:
        payload = {
            "topic": topic,
            "character_name": character_name,
            "num_lessons": num_lessons
        }
        
        response = requests.post(f"{API_URL}/api/generate", json=payload)
        response.raise_for_status()
        return response.json()["job_id"]
    except Exception as e:
        st.error(f"Failed to start generation: {str(e)}")
        return None

def get_job_status(job_id: str) -> Optional[Dict]:
    """Get current job status"""
    try:
        response = requests.get(f"{API_URL}/api/job/{job_id}")
        response.raise_for_status()
        return response.json()
    except:
        return None

# --- Main UI ---
st.title("Content Factory - AI Educational Video Generator")
st.markdown("#### Transform any topic into an engaging educational video with AI")

# Sidebar for inputs
with st.sidebar:
    st.header("📋 Video Configuration")
    
    api_status = check_api_health()
    if api_status:
        st.success("✅ API Connected")
    else:
        st.error("❌ API Not Running - Please start the server")
        st.stop()
    
    st.divider()
    
    # Input fields
    topic = st.text_input(
        "Topic *",
        placeholder="e.g., Introduction to Machine Learning",
        help="Enter the topic you want to create a video about"
    )
    
    character_name = st.text_input(
        "Character Name",
        value="Zara",
        help="Name of the character who will present the lesson"
    )
    
    num_lessons = st.number_input(
        "Number of Lessons",
        min_value=1,
        max_value=5,
        value=1,
        help="How many lessons to generate"
    )
    
    st.divider()
    
    generate_button = st.button(
        "🚀 Generate Video",
        type="primary",
        use_container_width=True,
        disabled=not topic.strip()
    )

# --- Start pipeline when button is clicked ---
if generate_button and topic.strip():
    with st.spinner("Starting video generation..."):
        job_id = start_video_generation(
            topic,
            character_name,
            num_lessons,
        )
        if job_id:
            st.session_state.job_id = job_id
            st.session_state.video_generated = False
            st.session_state.job_status = None
            st.success(f"✅ Job started! Topic: {topic}")

# --- Show spinner until video is generated ---
if st.session_state.job_id and not st.session_state.video_generated:
    st.header("🎬 Generation Progress")
    spinner_placeholder = st.empty()
    info_placeholder = st.empty()
    logs_placeholder = st.empty()

    status = None
    job_done = False
    while not job_done:
        with spinner_placeholder:
            st.markdown(
                "<div style='display: flex; justify-content: center; align-items: center; height: 80px;'>"
                "<span style='margin-left:10px;font-size:1.1em;'>Generating video, please wait...</span>"
                "</div>",
                unsafe_allow_html=True
            )
        
        status = get_job_status(st.session_state.job_id)
        if not status:
            st.error("Failed to get job status from backend.")
            break

        st.session_state.job_status = status

        if status["status"] == "completed":
            st.session_state.video_generated = True
            job_done = True
            break
        elif status["status"] == "failed":
            st.error(f"Generation failed: {status.get('error', 'Unknown error')}")
            job_done = True
            break
        time.sleep(2)

    # --- Display character details, lessons and logs ---
    # if status.get("character_info"):
    #     char_info = status["character_info"]
    #     st.markdown(f"""
    #     <div class="info-card">
    #         <h4>🎭 Character</h4>
    #         <p><strong>Name:</strong> {char_info['name']}</p>
    #         <p><strong>Gender:</strong> {char_info['gender']}</p>
    #         <p><strong>Voice:</strong> {char_info['voice_style']}</p>
    #     </div>
    #     """, unsafe_allow_html=True)
        
    if status.get("curriculum_info"):
        lessons_html = "<div class='info-card'><h4>📚 Lessons</h4>"
        for lesson in status["curriculum_info"]["lessons"]:
            lessons_html += f"<p>• <strong>{lesson['title']}</strong><br><span style='font-size: 0.9em; color: #666;'>{lesson['summary']}</span></p>"
        lessons_html += "</div>"
        st.markdown(lessons_html, unsafe_allow_html=True)
            
    spinner_placeholder.empty()
    if st.session_state.job_status and st.session_state.job_status.get("logs"):
        with logs_placeholder:
            st.subheader("📋 Progress Logs")
            with st.expander("Show Progress Logs", expanded=False):
                for log in st.session_state.job_status["logs"]:
                    timestamp = log['timestamp'][:19].replace('T', ' ')
                    st.markdown(f"<span style='color:#888;'>{timestamp}</span> {log['message']}", unsafe_allow_html=True)


# --- Display generated video and downloads ---
if st.session_state.video_generated and st.session_state.job_status:
    st.markdown("""
    <div class="success-box">
        <h2>🎉 Video Generated Successfully!</h2>
    </div>
    """, unsafe_allow_html=True)
    
    results = st.session_state.job_status.get("result", [])
    if results:
        for idx, video in enumerate(results):
            st.header(f"📹 Lesson {idx + 1}: {video['lesson']}")
            video_col, control_col = st.columns([3, 1])
            with video_col:
                try:
                    video_url = f"{API_URL}/api/stream/{video['video_filename']}"
                    st.video(video_url)
                except Exception as e:
                    st.error(f"Error loading video: {str(e)}")
                    st.info(f"Video file: {video['video_filename']}")
            with control_col:
                video_download_url = f"{API_URL}/api/download/{video['video_filename']}"
                audio_download_url = f"{API_URL}/api/download/{video['audio_filename']}"
                st.markdown("""
                    <div style="
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        min-height: 350px;
                    ">
                        <div style="width:100%;">
                            <h4 style="text-align: center;">📥 Downloads</h4>
                            <a href="{video_url}" class="download-btn" download>
                                📹 Download Video (with Audio)
                            </a><br>
                            <a href="{audio_url}" class="download-btn" download>
                                🎵 Download Audio Only
                            </a>
                        </div>
                    </div>
                    """.format(
                        video_url=video_download_url,
                        audio_url=audio_download_url
                    ), unsafe_allow_html=True)
                
            st.divider()

    # Reset button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Generate Another Video", use_container_width=True):
            st.session_state.job_id = None
            st.session_state.job_status = None
            st.session_state.video_generated = False
            st.rerun()
# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🎬 Content Factory - Powered by AI</p>
    <p>Transform knowledge into engaging educational videos</p>
</div>
""", unsafe_allow_html=True)
