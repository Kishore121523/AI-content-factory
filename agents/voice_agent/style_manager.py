from typing import Dict
from .constants import (
    EMOTION_TO_STYLE, DESCRIPTION_KEYWORDS, EMOTION_DEGREES,
    VOICE_SUPPORTED_STYLES, NARRATOR_VOICE, MALE_CHARACTER_VOICE, 
    FEMALE_CHARACTER_VOICE
)

#Manages voice styles, emotions, and voice selection
class StyleManager:
    
    def get_base_style(self, description: str, voice_style: str) -> str:
        """Determine base style from character description"""
        description_lower = (description + " " + voice_style).lower()
        
        # Check for keywords in description
        for keyword, style in DESCRIPTION_KEYWORDS.items():
            if keyword in description_lower:
                return style
        
        # Default to assistant style for educational content
        return 'assistant'
    
    def get_style_degree(self, emotion: str) -> float:
        """Get style intensity based on emotion"""
        emotion_lower = emotion.lower()
        return EMOTION_DEGREES.get(emotion_lower, 1.0)  # Default to 1.0
    
    def get_style_for_emotion(self, emotion: str, base_style: str, 
                            speaker: str, voice_name: str) -> str:
        """Get appropriate SSML style for the given emotion and voice"""
        emotion_lower = emotion.lower()
        
        # Get voice's supported styles
        voice_styles = VOICE_SUPPORTED_STYLES.get(voice_name, ["assistant", "friendly", "cheerful"])
        
        # Check emotion mapping
        desired_style = EMOTION_TO_STYLE.get(emotion_lower, base_style)
        
        # Ensure style is supported by the voice
        if desired_style in voice_styles:
            return desired_style
        
        # Fallback to a supported style
        if "friendly" in voice_styles:
            return "friendly"
        elif "assistant" in voice_styles:
            return "assistant"
        else:
            return voice_styles[0] if voice_styles else "cheerful"
    
    #Get appropriate voice with better variety
    def get_voice_for_speaker(self, speaker: str, character_name: str, gender: str) -> str:
        if speaker.lower() == "narrator":
            return NARRATOR_VOICE
        
        if gender == "male":
            return MALE_CHARACTER_VOICE
        else:
            return FEMALE_CHARACTER_VOICE