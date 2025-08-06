# visual_agent.py - Educational Video Generator

from agents.base_agent import Agent
from moviepy.editor import AudioFileClip, ImageClip
import numpy as np
import os
import traceback

# Import modular components
from .constants import VIDEO_SIZE, FPS
from .avatar_manager import AvatarManager
from .text_utils import TextManager
from .script_parser import ScriptParser
from .slide_renderer import SlideRenderer
from .video_composer import VideoComposer

class VisualAgent(Agent):
    """Main Visual Agent for educational video generation"""
    
    def __init__(self):
        super().__init__("VisualAgent")
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize components
        self.avatar_manager = AvatarManager()
        self.text_manager = TextManager()
        self.slide_renderer = SlideRenderer(VIDEO_SIZE, self.avatar_manager, self.text_manager)
        self.video_composer = VideoComposer(FPS)
        self.script_parser = ScriptParser()
    
    def run(self, input_data, test_mode=False, **kwargs):
        """Generate educational video with large avatars"""
        try:
            # Extract input data
            character = input_data["character"]
            lesson_title = input_data["lesson_title"]
            script = input_data["script"]
            voice_path = input_data["voice_path"]
            timing_data = input_data.get("timing", None)

            print(f"\n🎬 Creating educational video for: {lesson_title}")
            print(f"🎨 Using large avatars for {character['name']}")

            # Load and prepare audio
            audio_clip = self._load_audio(voice_path, test_mode)
            total_duration = audio_clip.duration
            print(f"📊 Audio duration: {total_duration:.2f} seconds")

            # Parse script
            slides = self.script_parser.parse_script_to_slides(script, character['name'])
            print(f"📑 Created {len(slides)} slides")

            # Calculate timings
            timings = self._calculate_timings(slides, timing_data, total_duration)

            # Render slides
            rendered_clips = self._render_slides(slides, timings, character, lesson_title)

            # Compose final video
            output_filename = f"{character['name']}_{lesson_title.replace(' ', '_')}.mp4"
            output_path = os.path.join(self.output_dir, output_filename)
            
            final_video = self.video_composer.compose_video(
                rendered_clips, audio_clip, output_path
            )

            # Cleanup
            self._cleanup(audio_clip, final_video)
            
            print(f"✅ Video created successfully: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            traceback.print_exc()
            raise
    
    def _load_audio(self, voice_path: str, test_mode: bool) -> AudioFileClip:
        """Load and prepare audio clip"""
        full_audio = AudioFileClip(voice_path)
        
        if test_mode:
            print("🧪 Test mode: Trimming audio to first 30s")
            return full_audio.subclip(0, min(30, full_audio.duration))
        
        return full_audio
    
    def _calculate_timings(self, slides: list, timing_data: list, total_duration: float) -> list:
        """Calculate slide timings"""
        if timing_data:
            print("📊 Using timing data from voice synthesis")
            return self.video_composer.calculate_slide_timings_from_voice(
                slides, timing_data, total_duration
            )
        else:
            print("⚠️ No timing data provided, estimating from text length")
            return self.video_composer.calculate_slide_timings(slides, total_duration)
    
    def _render_slides(self, slides: list, timings: list, character: dict, 
                      lesson_title: str) -> list:
        """Pre-render all slides"""
        print("🎨 Pre-rendering all slides with large avatars...")
        rendered_clips = []
        
        for i, (slide, timing) in enumerate(zip(slides, timings)):
            print(f"  Rendering slide {i+1}/{len(slides)}: {slide['type']}")
            
            # Render appropriate slide type
            if slide['type'] == 'title':
                pil_image = self.slide_renderer.render_title_slide(lesson_title, character)
            elif slide['type'] == 'end':
                pil_image = self.slide_renderer.render_end_slide(lesson_title)
            else:
                pil_image = self.slide_renderer.render_content_slide(
                    text=slide['text'],
                    speaker_type=slide['type'],
                    speaker_name=slide.get('speaker_name', ''),
                    character=character,
                    lesson_title=lesson_title,
                    slide_number=i,
                    total_slides=len(slides)
                )
            
            # Convert PIL to MoviePy ImageClip
            img_array = np.array(pil_image)
            clip = ImageClip(img_array).set_duration(timing['duration'])
            rendered_clips.append(clip)
        
        return rendered_clips
    
    def _cleanup(self, audio_clip, video_clip):
        """Clean up resources"""
        audio_clip.close()
        video_clip.close()
        self.avatar_manager.clear_cache()