# 🎬 Content Factory

An AI-powered educational content generation system that creates full educational videos with synchronized audio and visuals. The system uses a multi-agent architecture to generate curriculum, characters, scripts, voice narration, and videos from a simple topic input.

## 🌟 Features

- **Multi-Agent Architecture**: Modular design with specialized agents for each task
- **Automatic Curriculum Generation**: Creates 3-5 structured lessons from any topic
- **Dynamic Character Creation**: Generates educational characters with personalities and avatars
- **Emotion-Based Scripts**: Creates engaging dialogues with varied emotions
- **Expressive Voice Synthesis**: SSML-based TTS with emotion-driven voice styles
- **Professional Video Generation**: HD videos with large avatars and synchronized audio
- **Character Persistence**: Reuse characters across multiple videos
- **Robust Error Handling**: Retry logic and graceful fallbacks

## 🎥 Sample Output

The system generates professional educational videos with:
- Character avatars
- Speech bubbles with speaker indicators
- Smooth transitions between slides
- Progress tracking
- Synchronized audio with emotional expression

## 🏗️ Architecture

```
Content Factory Pipeline:

     User Input                    Coordinator
         │                        (Orchestrator)
         v                             │
    ┌─────────┐                        │
    │  Topic  │                        │
    └────┬────┘                        │
         │                             │
         v                             v
    ┌───────────────────────────────────────────┐
    │            Curriculum Agent               │
    │  Input: Topic                             │
    │  Output: Array of lessons                 │
    │          [{title, summary}, ...]          │
    └────────────────────┬──────────────────────┘
                         │
                         v
    ┌───────────────────────────────────────────┐
    │            Character Agent                │
    │  Input: Character name                    │
    │  Output: Character object                 │
    │          {name, gender, description,      │
    │           voice_style, avatar_id}         │
    └────────────────────┬──────────────────────┘
                         │
                         v
    ┌───────────────────────────────────────────┐
    │              Script Agent                 │
    │  Input: {character, lessons}              │
    │  Output: Array of scripts                 │
    │          [{lesson, script}, ...]          │
    └────────────────────┬──────────────────────┘
                         │
                         v
    ┌───────────────────────────────────────────┐
    │              Voice Agent                  │
    │  Input: {character, lesson_title, script} │
    │  Output: {audio_path, timing, duration}   │
    │          - MP3 audio file                 │
    │          - Timing JSON data               │
    └────────────────────┬──────────────────────┘
                         │
                         v
    ┌───────────────────────────────────────────┐
    │              Visual Agent                 │
    │  Input: {character, lesson_title,         │
    │          script, voice_path, timing}      │
    │  Output: MP4 video file                   │
    └────────────────────┬──────────────────────┘
                         │
                         v
                  ┌─────────────┐
                  │ Final Video │
                  │  Output/.mp4│
                  └─────────────┘

Notes:
- Coordinator manages all agents but doesn't appear in data flow
- Each agent receives specific inputs from previous stages
- All agents are independent and communicate only through the coordinator
```

## 📋 Prerequisites

### System Requirements
- Python 3.11.13
- macOS, Linux, or Windows
- 4GB+ RAM recommended
- 2GB+ free disk space

### External Dependencies
- **FFmpeg**: For video encoding
  ```bash
  # macOS
  brew install ffmpeg
  
  # Ubuntu/Debian
  sudo apt-get install ffmpeg
  
  # Windows
  # Download from https://ffmpeg.org/download.html
  ```

- **ImageMagick**: For advanced text rendering
  ```bash
  # macOS
  brew install imagemagick
  
  # Ubuntu/Debian
  sudo apt-get install imagemagick
  ```

### API Keys
You'll need Azure OpenAI API keys for:
- Language Model (for content generation)
- Speech Services (for voice synthesis)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/content-factory.git
   cd content-factory
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your API keys:
   ```env
   # Azure OpenAI LLM
   AZURE_OPENAI_LLM_KEY=your_key_here
   AZURE_OPENAI_LLM_ENDPOINT=your_endpoint_here
   AZURE_OPENAI_LLM_API_VERSION=2024-12-01-preview
   AZURE_OPENAI_LLM_DEPLOYMENT_NAME=your_deployment_name
   
   # Azure TTS
   AZURE_OPENAI_TTS_KEY=your_tts_key_here
   AZURE_OPENAI_TTS_REGION=eastus
   ```

## 💻 Usage

### Basic Usage

```bash
python main.py
```

Follow the prompts:
1. Enter your educational topic (e.g., "Water Cycle", "Photosynthesis")
2. Enter a character name or press Enter for default "Zara"
3. Wait for the video generation (typically 2-5 minutes)

### Output Files

Generated files are saved in the `output/` directory:
- `CharacterName_Lesson_Title.mp4` - Final video
- `CharacterName_Lesson_Title.mp3` - Audio narration
- `CharacterName_Lesson_Title_timing.json` - Synchronization data

### Test Mode

Test video generation without TTS API calls:
```bash
python test_video_gen.py
```

Test voice styles:
```bash
python debug_voice_styles.py
```

## 🧩 Project Structure

```
content-factory/                                        
├── agents/                                       # Core agent modules
│   ├── __pycache__/                              # Python bytecode cache
│   ├── base_agent.py                             # Base agent class (common logic for all agents)
│   ├── character_agent.py                        # Character creation/generation agent
│   ├── curriculum_agent.py                       # Lesson/curriculum planning agent
│   ├── script_agent.py                           # Script writing/generation agent
│   ├── voice_agent/                              # Voice synthesis and processing
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── audio_synthesizer.py                  # Voice audio synthesis logic
│   │   ├── constants.py                          # Voice agent configuration/constants
│   │   ├── script_processor.py                   # Processes scripts for TTS
│   │   ├── ssml_builder.py                       # Builds SSML for expressive speech
│   │   ├── style_manager.py                      # Handles voice styles/parameters
│   │   └── voice_agent.py                        # Main voice agent orchestration
│   └── visual_agent/                             # Video generation and overlays
│       ├── __pycache__/
│       ├── __init__.py
│       ├── avatar_manager.py                     # Avatar image handling/selection
│       ├── constants.py                          # Visual agent configuration/constants
│       ├── moviepy_overlay_manager.py            # Adds overlays (e.g., captions, graphics)
│       ├── script_parser.py                      # Parses scripts for visual rendering
│       ├── slide_renderer.py                     # Creates individual slides
│       ├── text_utils.py                         # Text formatting, splitting, utilities
│       ├── ui_components.py                      # Draws UI-like elements on slides
│       ├── video_composer.py                     # Assembles video from slides and audio
│       └── visual_agent.py                       # Main visual agent (video pipeline)
├── avatars/                                      # Character/avatar images
│   ├── female/
│   │   ├── avatar_1.gif                          # Female avatar (GIF animation)
│   │   ├── avatar_1.png
│   │   ├── avatar_2.png
│   │   └── avatar_3.png
│   └── male/
│       ├── avatar_1.gif                          # Male avatar (GIF animation)
│       ├── avatar_1.png
│       ├── avatar_2.png
│       └── avatar_3.png
├── databaseFunctions/                            # Scripts for managing the DB
│   ├── reset_db.py                               # Reset/initialize database
│   └── view_characters.py                        # Script to view character entries
├── logs/                                         # Stores the logs generated from QA check
├── output/                                       # Generated audio/video/output files
│   ├── David_Introduction_to_Retrieval-Augmented_Generation_(RAG).mp3      # Sample output (audio)
│   ├── David_Introduction_to_Retrieval-Augmented_Generation_(RAG).mp4      # Sample output (video)
│   └── David_Introduction_to_Retrieval-Augmented_Generation_(RAG)_timing.json # Output timings
├── utils/                                        # Utility/helper scripts
│   ├── __pycache__/
│   └── db.py                                     # DB connection/utilities
│   └── qa.py                                     # QA checks after each video generation
├── venv/                                         # Python virtual environment
│   └── [virtual environment files]
├── .gitignore                                    # Git ignore file
├── content_factory.db                            # SQLite database file
├── coordinator.py                                # Main agent orchestration logic
├── main.py                                       # Project entry point script
├── README.md                                     # Project documentation
├── requirements.txt                              # Python dependencies
├── test_voice_styles.py                          # Voice style test script
└── test_video_gen.py                             # Video generation test script

```

## 🎨 Customization

### Adding New Avatars
1. Add PNG images to `avatars/gender/avatar_X.png`
2. Images should be square, ideally 512x512px or larger
3. Transparent background recommended

### Modifying Visual Style
Edit constants in `agents/visual_agent/constants.py`:
- Colors, sizes, layouts
- Transition durations
- Font settings

### Changing Voice Styles
Modify emotion mappings in `agents/voice_agent.py`:
- `emotion_to_style` dictionary
- `get_style_degree()` for intensity

### Custom Characters
Characters are stored in SQLite database with:
- Name, gender, description
- Voice style preferences
- Avatar selection

## 🧪 Development

### Running Tests
```bash
# Test video generation with existing audio
python test_video_gen.py

# Test voice styles
python debug_voice_styles.py

# Generate single video for testing
python main.py 
```

### Adding New Agents
1. Create new agent class inheriting from `base_agent.py`
2. Implement `run()` method
3. Register with coordinator in `main.py`

### Debugging Tips
- Enable test mode for 30-second previews
- Use timing JSON files for synchronization debugging
- Check `output/` for intermediate files
- Review agent outputs at each pipeline stage

## 🐛 Troubleshooting

### Common Issues

1. **ImportError for MoviePy**
   - Install system dependencies (FFmpeg, ImageMagick)
   - Restart terminal after installation

2. **Azure TTS Errors**
   - Verify API keys in `.env`
   - Check region settings
   - Ensure voice names are correct

3. **Video Generation Fails**
   - Check available disk space
   - Verify all avatars exist
   - Review error traceback for details

4. **Poor Audio-Video Sync**
   - Ensure timing.json file is generated
   - Check PADDING_DURATION in constants
   - Verify audio file duration

### Performance Optimization
- Use test mode for development
- Pre-generate common characters
- Batch process multiple videos
- Adjust video quality settings in constants

## 📄 License

MIT License - feel free to use this project for educational purposes!

## 🙏 Acknowledgments

- Azure OpenAI for LLM and TTS services
- MoviePy for video processing
- The open-source community

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review agent-specific documentation in code comments

---