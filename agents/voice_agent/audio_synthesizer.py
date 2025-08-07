import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment
from typing import List, Tuple
import os
from .constants import (
    TITLE_SILENCE_MS, SEGMENT_PADDING_MS, END_SILENCE_MS,
    DEFAULT_SEGMENT_DURATION
)

class AudioSynthesizer:
    """Handles audio synthesis and combination"""
    
    def __init__(self, speech_config):
        self.speech_config = speech_config
    
    def synthesize_ssml(self, ssml: str, output_path: str) -> bool:
        """Synthesize SSML to audio file with error handling"""
        try:
            audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # Use SSML synthesis
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print(f"✅ SSML audio segment saved")
                return True

            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print(f"❌ Speech synthesis canceled: {cancellation_details.reason}")
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print(f"❌ Error details: {cancellation_details.error_details}")
                return False
            else:
                print(f"❌ Speech synthesis failed: {result.reason}")
                return False
                
        except Exception as e:
            print(f"❌ Exception in SSML synthesis: {e}")
            return False
    
    def combine_audio_segments(self, segment_infos: List[Tuple[str, float]], 
                             output_path: str) -> AudioSegment:
        combined_audio = AudioSegment.silent(duration=0)
        
        # Add initial silence for title slide
        title_silence = AudioSegment.silent(duration=TITLE_SILENCE_MS)
        combined_audio += title_silence
        
        # Add each segment with padding
        for temp_path, _ in segment_infos:
            try:
                segment_audio = AudioSegment.from_file(temp_path)
                silence_padding = AudioSegment.silent(duration=SEGMENT_PADDING_MS)
                combined_audio += segment_audio + silence_padding
            except Exception as e:
                print(f"⚠️ Could not load audio segment {temp_path}: {e}")
                # Add silence for failed segment
                combined_audio += AudioSegment.silent(duration=int(DEFAULT_SEGMENT_DURATION * 1000))
        
        # Add end slide silence
        end_silence = AudioSegment.silent(duration=END_SILENCE_MS)
        combined_audio += end_silence
        
        # Export combined audio
        combined_audio.export(output_path, format="mp3")
        return combined_audio
    
    def cleanup_temp_files(self, temp_paths: List[str]):
        """Clean up temporary audio files"""
        for path in temp_paths:
            try:
                os.remove(path)
            except Exception as e:
                print(f"⚠️ Could not delete {path}: {e}")
    
    def measure_segment_duration(self, audio_path: str) -> float:
        """Measure duration of an audio segment"""
        try:
            segment_audio = AudioSegment.from_file(audio_path)
            return len(segment_audio) / 1000.0  # Convert to seconds
        except Exception as e:
            print(f"⚠️ Could not measure audio duration: {e}")
            return DEFAULT_SEGMENT_DURATION