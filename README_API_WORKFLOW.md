📬 Example API Workflow (Postman Step-by-Step)
----------------------------------------------

Below is a full example of using each REST API endpoint in sequence with sample requests and actual responses.
At the end of this file, you will find `Automated Pipeline` and `View Logs` which is used by the frontend application

**MAKE SURE TO START YOUR FastAPI SERVER (backend.py)**
```bash
uvicorn backend:app --reload
```

**HEALTH CHECK**

**GET** `http://localhost:8000/`

**Response:**
```json
{
    "message": "Content Factory API is running!",
    "status": "healthy"
}
```
* * * * *

### **1\. Generate Curriculum**

**POST** `http://localhost:8000/api/curriculum/generate`\
**Body:**
```json
{
  "topic": "Machine Learning Basics",
  "num_lessons": 1
}
```

**Response:**
```json
{
  "curriculum_id": "9a680a82-0830-48d7-b801-21860f19193e",
  "lessons": [
    {
      "title": "Introduction to Machine Learning",
      "summary": "This lesson explains what machine learning is and how it differs from traditional programming by enabling systems to learn from data."
    }
  ]
}
```

**Copy:** curriculum_id: `9a680a82-0830-48d7-b801-21860f19193e`
* * * * *

### **2\. Create Character**

**POST** `http://localhost:8000/api/character/create`\
**Body:**

```json
{
  "name": "Kishore"
}
```

**Response:**

```json
{
  "character_id": "873becf7-6bf9-4c0b-9d40-6f3d745523ef",
  "character": {
    "name": "Kishore",
    "gender": "male",
    "description": "A creative, inquisitive educator who seamlessly blends historical anecdotes with practical examples to spark curiosity and make learning relatable. They are enthusiastic, warm, and friendly.",
    "voice_style": "clear and engaging",
    "avatar_id": 3
  }
}
```

**Copy:** character_id: `873becf7-6bf9-4c0b-9d40-6f3d745523ef`
* * * * *

### **3\. Generate Script**

**POST** `http://localhost:8000/api/script/generate`\
**Body:**

```json
{
  "curriculum_id": "9a680a82-0830-48d7-b801-21860f19193e",
  "character_id": "873becf7-6bf9-4c0b-9d40-6f3d745523ef"
}
```

**Response:**

```json
{
  "script_id": "43db573c-3993-461d-8a40-c71c2f527d56",
  "scripts": [
    {
      "lesson": "Introduction to Machine Learning",
      "script": "Introduction:\nKishore (enthusiastic): Hello everyone! Welcome to our exciting journey into the fascinating world of machine learning...",
      "overlay_data": {
        "highlight_keywords": [
          "machine learning",
          "data",
          "algorithms",
          "models",
          "patterns"
        ],
        "caption_phrases": [
          { "trigger": "learn from data", "text": "Systems adapt using data" },
          { "trigger": "traditional programming", "text": "Coding by explicit instructions" },
          { "trigger": "data-driven algorithms", "text": "Algorithms evolve automatically" }
        ],
        "emphasis_points": [
          { "type": "definition", "text": "Machine Learning: Systems that self-improve through experience." },
          { "type": "key_fact", "text": "ML surpasses manual coding with data-driven growth." }
        ]
      }
    }
  ]
}
```

**Copy:** script_id: `43db573c-3993-461d-8a40-c71c2f527d56`
* * * * *

### **4\. Generate Voice**

**POST** `http://localhost:8000/api/voice/generate`\
**Body:**

```json
{
  "script_id": "43db573c-3993-461d-8a40-c71c2f527d56",
  "character_id": "873becf7-6bf9-4c0b-9d40-6f3d745523ef"
}
```

**Response:**

```json
{
  "voice_id": "9869a7a8-ddf1-4826-93a1-aee280621fab"
}
```

**Copy:** voice_id: `9869a7a8-ddf1-4826-93a1-aee280621fab`
* * * * *

### **5\. Generate Video**

**POST** `http://localhost:8000/api/video/generate`\
**Body:**

```json
{
  "script_id": "43db573c-3993-461d-8a40-c71c2f527d56",
  "character_id": "873becf7-6bf9-4c0b-9d40-6f3d745523ef",
  "voice_id": "9869a7a8-ddf1-4826-93a1-aee280621fab"
}
```

**Response:**

```json
{
  "video_id": "a57dfea5-e0a7-4c86-b90b-33c175e80a89",
  "videos": [
    {
      "lesson": "Introduction to Machine Learning",
      "video_path": "output/Kishore_Introduction_to_Machine_Learning.mp4",
      "video_filename": "Kishore_Introduction_to_Machine_Learning.mp4",
      "audio_path": "output/Kishore_Introduction_to_Machine_Learning.mp3",
      "audio_filename": "Kishore_Introduction_to_Machine_Learning.mp3"
    }
  ]
}
```

**Copy:** Video and audio filenames for use with download/stream endpoints.
* * * * *

### **6\. Download/Stream Your Files**

-   **Download:**\
    `GET http://localhost:8000/api/download/Kishore_Introduction_to_Machine_Learning.mp4`

-   **Stream:**\
    `GET http://localhost:8000/api/stream/Kishore_Introduction_to_Machine_Learning.mp4`

# Automated Pipeline:

**POST** `http://localhost:8000/api/pipeline/start`

**Body:**
```json
{
    "topic": "Machine Coding",
    "character_name": "Kishore",
    "num_lessons": 1
 }
```
**Response:**
```json
{
    "job_id": "ae90d678-c5f6-4e4b-9d8e-3dae06330928"
}
```
**Copy:** Job_id: `ae90d678-c5f6-4e4b-9d8e-3dae06330928`

# View Logs:
**GET** `http://localhost:8000/api/job/{job_id}`

**Response:**
```json
{
    "id": "ae90d678-c5f6-4e4b-9d8e-3dae06330928",
    "status": "completed",
    "topic": "Machine Coding",
    "result": [
        {
            "lesson": "Introduction to Machine Coding",
            "video_path": "output/Kishore_Introduction_to_Machine_Coding.mp4",
            "video_filename": "Kishore_Introduction_to_Machine_Coding.mp4",
            "audio_path": "output/Kishore_Introduction_to_Machine_Coding.mp3",
            "audio_filename": "Kishore_Introduction_to_Machine_Coding.mp3"
        }
    ],
    "error": null,
    "curriculum_info": {
        "lessons": [
            {
                "title": "Introduction to Machine Coding",
                "summary": "Explore the fundamentals of machine coding as the process of translating high-level programming languages into binary instructions executed by computer hardware."
            }
        ]
    },
    "character_info": {
        "name": "Kishore",
        "gender": "male",
        "voice_style": "clear and engaging"
    },
    "logs": [
        {
            "timestamp": "2025-08-07T12:06:00.192327",
            "message": "🚀 Starting pipeline for topic: Machine Coding"
        },
        {
            "timestamp": "2025-08-07T12:06:00.192351",
            "message": "📚 Generating curriculum for: Machine Coding"
        },
        {
            "timestamp": "2025-08-07T12:06:04.413525",
            "message": "✅ Curriculum ready: 1 lesson(s)"
        },
        {
            "timestamp": "2025-08-07T12:06:04.413555",
            "message": "🎭 Cnfiguring character: Kishore"
        },
        {
            "timestamp": "2025-08-07T12:06:04.414993",
            "message": "✅ Character configured: Kishore (male)"
        },
        {
            "timestamp": "2025-08-07T12:06:04.414997",
            "message": "📝 Generating scripts with emotions and overlays..."
        },
        {
            "timestamp": "2025-08-07T12:06:24.557337",
            "message": "✅ Scripts ready with overlay data"
        },
        {
            "timestamp": "2025-08-07T12:06:24.557353",
            "message": "🎤 Creating expressive voice narration..."
        },
        {
            "timestamp": "2025-08-07T12:06:34.606870",
            "message": "✅ Voice synthesis complete with timing data"
        },
        {
            "timestamp": "2025-08-07T12:06:34.606898",
            "message": "🎬 Generating video with synchronized overlays..."
        },
        {
            "timestamp": "2025-08-07T12:07:41.026982",
            "message": "✅ Video generation complete"
        },
        {
            "timestamp": "2025-08-07T12:07:41.026993",
            "message": "🔍 Running QA checks..."
        },
        {
            "timestamp": "2025-08-07T12:07:41.027445",
            "message": "⚠️ QA found 2 warning(s)"
        },
        {
            "timestamp": "2025-08-07T12:07:41.027450",
            "message": "🎉 Successfully generated 1 video(s)"
        }
    ]
}
```

