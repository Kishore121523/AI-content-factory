# video_composer.py - Video Composition and Timing Logic

from moviepy.editor import *
import numpy as np
from typing import List, Dict
from .constants import *

class VideoComposer:
    """Handles video composition and timing calculations"""
    
    def __init__(self, fps: int = FPS):
        self.fps = fps
    
    def compose_video(self, rendered_clips: List, audio_clip, output_path: str):
        """Compose final video from clips and audio"""
        print("🔗 Compositing final video...")
        
        # Add transitions
        clips_with_transitions = []
        for i, clip in enumerate(rendered_clips):
            if i > 0 and i < len(rendered_clips) - 1:
                clip = clip.fadein(FADE_DURATION)
            clips_with_transitions.append(clip)
        
        # Concatenate clips
        final_video = concatenate_videoclips(clips_with_transitions, method="compose")
        final_video = final_video.set_duration(audio_clip.duration)
        final_video = final_video.set_audio(audio_clip)
        
        # Save video
        print(f"💾 Rendering video to: {output_path}")
        final_video.write_videofile(
            output_path,
            codec=VIDEO_CODEC,
            audio_codec=AUDIO_CODEC,
            fps=self.fps,
            preset=VIDEO_PRESET,
            threads=VIDEO_THREADS,
            bitrate=VIDEO_BITRATE
        )
        
        return final_video
    
    def calculate_slide_timings_from_voice(self, slides: List[Dict], timing_data: List[Dict], 
                                          total_duration: float) -> List[Dict]:
        """Calculate slide timings based on actual voice synthesis timing"""
        timings = []
        
        # Filter out the 'end' timing from voice data
        voice_segments = [t for t in timing_data if t['speaker'] != 'end']
        
        # Title slide
        timings.append({
            'start': 0,
            'duration': END_SLIDE_DURATION
        })
        
        # Match content slides to voice timing
        slide_idx = 1
        voice_idx = 0
        
        while slide_idx < len(slides) - 1 and voice_idx < len(voice_segments):
            slide = slides[slide_idx]
            voice_segment = voice_segments[voice_idx]
            
            if ((slide['type'] == 'character' and voice_segment['speaker'] == slide['speaker_name']) or
                (slide['type'] == 'narrator' and voice_segment['speaker'] == 'Narrator')):
                
                # Add padding to ensure audio completes
                timings.append({
                    'start': voice_segment['start_time'],
                    'duration': voice_segment['duration'] + PADDING_DURATION
                })
                slide_idx += 1
                voice_idx += 1
            else:
                voice_idx += 1
        
        # Handle remaining slides
        while slide_idx < len(slides) - 1:
            last_timing = timings[-1]
            timings.append({
                'start': last_timing['start'] + last_timing['duration'],
                'duration': DEFAULT_SLIDE_DURATION
            })
            slide_idx += 1
        
        # End slide
        last_content_end = timings[-1]['start'] + timings[-1]['duration'] if timings else total_duration - END_SLIDE_DURATION
        timings.append({
            'start': last_content_end,
            'duration': total_duration - last_content_end
        })
        
        # Adjust timings if needed
        self._adjust_timings(timings, total_duration)
        
        print(f"📊 Synchronized {len(timings)} slides with audio segments")
        for i, timing in enumerate(timings):
            print(f"   Slide {i+1}: {timing['start']:.2f}s - {timing['start'] + timing['duration']:.2f}s")
        
        return timings
    
    def calculate_slide_timings(self, slides: List[Dict], total_duration: float) -> List[Dict]:
        """Calculate timing for each slide with improved distribution"""
        # Calculate total weight
        total_weight = sum(slide['duration_weight'] for slide in slides)
        
        timings = []
        current_time = 0
        
        # First pass: calculate proportional durations
        for slide in slides:
            # Calculate proportional duration
            if total_weight > 0:
                duration = (slide['duration_weight'] / total_weight) * total_duration
            else:
                duration = total_duration / len(slides)
            
            # Apply minimum duration
            min_dur = MIN_DURATIONS.get(slide['type'], 2.0)
            duration = max(duration, min_dur)
            
            timings.append({
                'start': current_time,
                'duration': duration
            })
            
            current_time += duration
        
        # Adjust timings if needed
        self._adjust_timings(timings, total_duration)
        
        return timings
    
    def _adjust_timings(self, timings: List[Dict], total_duration: float):
        """Adjust timings to fit within total duration"""
        current_total = sum(t['duration'] for t in timings)
        
        if current_total > total_duration:
            # Scale down proportionally
            scale_factor = total_duration / current_total
            for timing in timings:
                timing['duration'] = max(timing['duration'] * scale_factor, 2.0)
        
        # Recalculate start times
        current_time = 0
        for timing in timings:
            timing['start'] = current_time
            current_time += timing['duration']
        
        # Ensure last slide doesn't exceed total duration
        if timings:
            last_timing = timings[-1]
            if last_timing['start'] + last_timing['duration'] > total_duration:
                last_timing['duration'] = total_duration - last_timing['start']