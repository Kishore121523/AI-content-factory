# voice_agent/voice_agent.py - Main Voice Agent

from agents.base_agent import Agent
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment
import os
import json
from dotenv import load_dotenv
from typing import Dict, List, Tuple

# Import modular components
from .style_manager import StyleManager
from .script_processor import ScriptProcessor
from .ssml_builder import SSMLBuilder
from .audio_synthesizer import AudioSynthesizer
from .constants import TITLE_SILENCE_MS, SEGMENT_PADDING_MS, END_SILENCE_MS

load_dotenv()

class VoiceAgent(Agent):
    """Main Voice Agent for text-to-speech synthesis with emotions"""
    
    def __init__(self):
        super().__init__("VoiceAgent")
        
        # Azure TTS configuration
        self.speech_key = os.getenv("AZURE_OPENAI_TTS_KEY")
        self.speech_region = os.getenv("AZURE_OPENAI_TTS_REGION")
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key,
            region=self.speech_region
        )
        
        # Initialize components
        self.style_manager = StyleManager()
        self.script_processor = ScriptProcessor()
        self.ssml_builder = SSMLBuilder(self.style_manager, self.script_processor)
        self.audio_synthesizer = AudioSynthesizer(self.speech_config)

    def run(self, input_data: Dict, **kwargs) -> Dict:
        """
        Generate voice with SSML and dynamic styles
        Always returns dict with audio_path, timing, and total_duration
        """
        # Extract input data
        character = input_data["character"]
        lesson_title = input_data["lesson_title"]
        full_script = input_data["script"]
        
        # Setup output paths
        output_file, timing_file = self._setup_output_paths(character["name"], lesson_title)
        
        print(f"\n🔊 Generating expressive voice with SSML...")
        
        # Process script and generate audio
        base_style = self._determine_base_style(character)
        segments = self.script_processor.parse_script_with_emotions(full_script, character["name"])
        
        # Synthesize segments and collect timing
        segment_infos, timing_data = self._synthesize_segments(
            segments, character, base_style
        )
        
        # Add end slide timing
        total_duration = self._calculate_total_duration(timing_data)
        timing_data.append(self._create_end_slide_timing(total_duration))
        
        # Combine audio segments
        self.audio_synthesizer.combine_audio_segments(segment_infos, output_file)
        print(f"✅ Expressive audio saved to {output_file}")
        
        # Save timing data
        self._save_timing_data(timing_file, timing_data)
        
        # Cleanup
        temp_paths = [path for path, _ in segment_infos]
        self.audio_synthesizer.cleanup_temp_files(temp_paths)
        
        # Return result
        return {
            "audio_path": output_file,
            "timing": timing_data,
            "total_duration": total_duration + (END_SILENCE_MS / 1000.0)
        }
    
    def _setup_output_paths(self, character_name: str, lesson_title: str) -> Tuple[str, str]:
        """Setup output file paths"""
        safe_title = lesson_title.replace(' ', '_')
        output_file = f"output/{character_name}_{safe_title}.mp3"
        timing_file = f"output/{character_name}_{safe_title}_timing.json"
        return output_file, timing_file
    
    def _determine_base_style(self, character: Dict) -> str:
        """Determine base style from character"""
        description = character.get("description", "")
        voice_style = character.get("voice_style", "")
        base_style = self.style_manager.get_base_style(description, voice_style)
        print(f"🎭 Base character style: {base_style}")
        return base_style
    
    def _synthesize_segments(self, segments: List[Dict], character: Dict, 
                           base_style: str) -> Tuple[List[Tuple[str, float]], List[Dict]]:
        """Synthesize all segments and return segment info and timing data"""
        segment_infos = []
        timing_data = []
        current_time = TITLE_SILENCE_MS / 1000.0  # Start after title slide
        
        for i, segment in enumerate(segments):
            # Extract segment data
            speaker = segment['speaker']
            text = segment['text']
            emotion = segment.get('emotion', 'neutral')
            
            # Determine voice and style
            voice_name = self.style_manager.get_voice_for_speaker(
                speaker, character["name"], character.get("gender", "female").lower()
            )
            style = self.style_manager.get_style_for_emotion(
                emotion, base_style, speaker, voice_name
            )
            style_degree = self.style_manager.get_style_degree(emotion)
            
            print(f"🎙️ Synthesizing [{speaker}] with emotion '{emotion}' → style '{style}' (degree: {style_degree})")
            
            # Create SSML and synthesize
            ssml = self.ssml_builder.create_ssml(text, voice_name, style, emotion)
            temp_path = f"output/temp_segment_{i}.mp3"
            
            success = self.audio_synthesizer.synthesize_ssml(ssml, temp_path)
            if not success:
                print(f"❌ SSML synthesis failed for segment {i}. Skipping this segment.")
                continue
            
            # Measure duration
            duration = self.audio_synthesizer.measure_segment_duration(temp_path)
            segment_infos.append((temp_path, duration))
            
            # Create timing entry
            timing_entry = {
                "speaker": speaker,
                "text": text,
                "emotion": emotion,
                "style": style,
                "style_degree": style_degree,
                "start_time": current_time,
                "duration": duration,
                "end_time": current_time + duration
            }
            timing_data.append(timing_entry)
            
            # Update current time (including padding)
            current_time += duration + (SEGMENT_PADDING_MS / 1000.0)
        
        return segment_infos, timing_data
    
    def _calculate_total_duration(self, timing_data: List[Dict]) -> float:
        """Calculate total duration from timing data"""
        if timing_data:
            last_segment = timing_data[-1]
            # Add padding after last segment
            return last_segment["end_time"] + (SEGMENT_PADDING_MS / 1000.0)
        return TITLE_SILENCE_MS / 1000.0
    
    def _create_end_slide_timing(self, start_time: float) -> Dict:
        """Create timing entry for end slide"""
        return {
            "speaker": "end",
            "text": "Thank you for learning with us!",
            "emotion": "cheerful",
            "style": "cheerful",
            "style_degree": 1.1,
            "start_time": start_time,
            "duration": END_SILENCE_MS / 1000.0,
            "end_time": start_time + (END_SILENCE_MS / 1000.0)
        }
    
    def _save_timing_data(self, timing_file: str, timing_data: List[Dict]):
        """Save timing data to JSON file"""
        with open(timing_file, 'w') as f:
            json.dump(timing_data, f, indent=2)
        print(f"📊 Timing data saved to {timing_file}")