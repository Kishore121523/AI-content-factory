"""
Simplified Streamlit Frontend - No polling needed
Run with: streamlit run streamlit_simplified.py
"""

import streamlit as st
import requests
import time

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
    .main { padding: 3rem; }
    
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
         
        color: #23272f;
        box-shadow: 0 1px 4px rgba(80,70,220,0.045);
    }
    .info-card .title { 
        font-size: 1.3rem;
        font-weight: 600;
        margin: 0.7rem 0 0.7rem 0; 

    }
    .info-card p {
        color: #222;
        font-size: 0.99rem;        
        margin: 0.18rem 0;
        line-height: 1.36;
    }
    .info-card strong {
        font-weight: 600;
        text-decoration:underline;
    }

    .download-btn {
        background: #fff !important;
        color: #111 !important;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        text-decoration: none !important;
        display: inline-block;
        margin: 1rem 0;
        text-align: center;
        font-weight: 600;
        border: 2px solid #111;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .download-btn:hover {
        background: #DDD !important;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'job_id' not in st.session_state:
    st.session_state.job_id = None
if 'job_result' not in st.session_state:
    st.session_state.job_result = None

# --- Main UI ---
st.title("Content Factory - AI Educational Video Generator")
st.markdown("#### Transform any topic into an Engaging Educational Video with AI")

# Sidebar
with st.sidebar:
    st.header("📋 Video Configuration")
    
    # Check API
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Error")
            st.stop()
    except:
        st.error("❌ API Not Running")
        st.stop()
    
    st.divider()
    
    topic = st.text_input(
        "Topic *",
        placeholder="e.g., Introduction to Machine Learning"
    )
    
    character_name = st.text_input(
        "Character Name",
        value="Zara"
    )
    
    num_lessons = st.number_input(
        "Number of Lessons",
        min_value=1,
        max_value=5,
        value=1
    )
    
    st.divider()
    
    generate_button = st.button(
        "🚀 Generate Video",
        type="primary",
        use_container_width=True,
        disabled=not topic
    )

# Start generation
if generate_button and topic:
    st.session_state.job_result = None
    
    # Start pipeline
    try:
        response = requests.post(
            f"{API_URL}/api/pipeline/start",
            json={
                "topic": topic,
                "character_name": character_name,
                "num_lessons": num_lessons
            }
        )
        job_id = response.json()["job_id"]
        st.session_state.job_id = job_id
        
        # Show spinner while processing
        with st.spinner("🎬 Generating video, please wait... (this may take a few minutes)"):
            # Wait for completion
            while True:
                response = requests.get(f"{API_URL}/api/job/{job_id}")
                job_data = response.json()
                
                if job_data["status"] == "completed":
                    st.session_state.job_result = job_data
                    st.success("✅ Video generated successfully!")
                    break
                elif job_data["status"] == "failed":
                    st.error(f"❌ Generation failed: {job_data.get('error', 'Unknown error')}")
                    break
                
                time.sleep(3)  # Check every 3 seconds
    
    except Exception as e:
        st.error(f"Error: {str(e)}")


# Display results
if st.session_state.job_result and st.session_state.job_result["status"] == "completed":
    result = st.session_state.job_result
    # Show success message
    st.markdown("""
    <div class="success-box">
        <h2>Content Generated Successfully!</h2>
    </div>
    """, unsafe_allow_html=True)

    # Show process logs in accordion
    if result.get("logs"):
        with st.expander("📋&nbsp;&nbsp;Generation Process", expanded=False):
            for log in result["logs"]:
                timestamp = log['timestamp'][:19].replace('T', ' ')
                st.markdown(f"<span style='color:#888;'>{timestamp}</span>&nbsp;&nbsp;&nbsp;&nbsp;{log['message']}", unsafe_allow_html=True)
    
    # Show lessons
    if result.get("curriculum_info"):
        lessons_html = "<div class='info-card'><p class='title'>📚 Generated Lessons</p>"
        for lesson in result["curriculum_info"]["lessons"]:
            lessons_html += f"<p>• <strong>{lesson['title']}</strong><br>"
            lessons_html += f"<span style='font-size: 0.9em; margin-left:8px; color: #666;'>{lesson['summary']}</span></p>"
        lessons_html += "</div>"
        st.markdown(lessons_html, unsafe_allow_html=True)
    
    st.divider()
    # Show videos
    videos = result.get("result", [])
    for idx, video in enumerate(videos):
        st.markdown(f"""
            <h3 style="margin-top:-1.7rem;">
                📹 Lesson {idx + 1}: {video['lesson']}
            </h3>
            <div style="
                display: flex;
                justify-content: center;
                align-items: center;
            ">
                <div style="display: flex; flex-wrap: wrap;">
                    <div style="flex:3;">
                        <video
                            src="{API_URL}/api/stream/{video['video_filename']}"
                            controls
                            style="width:100%; border-radius: 12px; background: #000;"
                        ></video>
                    </div>
                    <div style="
                        flex:1;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        text-align: center;
                        min-height: 260px;
                        margin-top: -1.2rem;
                    ">
                        <h4>📥 Downloads</h4>
                        <a href="{API_URL}/api/download/{video['video_filename']}" class="download-btn" download style="width: 85%;">
                            📹 Download Video (with Audio)
                        </a>
                        <a href="{API_URL}/api/download/{video['audio_filename']}" class="download-btn" download style="width: 85%;">
                            🎵 Download Audio Only
                        </a>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()

    # Reset button
    if st.button("🔄 Generate Another Video", use_container_width=True):
        st.session_state.job_id = None
        st.session_state.job_result = None
        st.rerun()

# Footer
st.divider()

st.markdown("""
<div style="text-align: center; color: #666; margin-top:-1rem;">
    <p>🎬 Content Factory - Powered by Azure AI</p>
    <p style="margin-top:-1rem;">Transform knowledge into engaging educational videos</p>
</div>
""", unsafe_allow_html=True)