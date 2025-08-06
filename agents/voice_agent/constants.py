# voice_agent/constants.py - Voice Agent Constants

# Timing constants
TITLE_SILENCE_MS = 3000  # 3 seconds for title slide
SEGMENT_PADDING_MS = 700  # 0.7 seconds between segments
END_SILENCE_MS = 2500    # 2.5 seconds for end slide
DEFAULT_SEGMENT_DURATION = 3.0  # Default duration when audio fails

# Emotion to SSML style mapping
EMOTION_TO_STYLE = {
    # Positive emotions
    'enthusiastic': 'cheerful',
    'excited': 'excited',
    'cheerful': 'cheerful',
    'happy': 'cheerful',
    'friendly': 'friendly',
    'warm': 'friendly',
    'encouraging': 'hopeful',
    'joking': 'cheerful',
    'playful': 'cheerful',
    
    # Neutral/Professional
    'curious': 'chat',
    'thoughtful': 'chat',
    'educational': 'assistant',
    'informative': 'assistant',
    'engaging': 'assistant',
    'illustrative': 'assistant',
    'reassuring': 'assistant',
    
    # Serious/Calm
    'serious': 'sad',  # Using sad as it's more serious
    'calm': 'assistant',
    'gentle': 'friendly',
    'professional': 'assistant',
    
    # Emphatic
    'emphatic': 'excited',
    'empathetic': 'friendly',
    'caring': 'friendly',
    
    # Default
    'neutral': 'assistant'
}

# Character description keywords to base style mapping
DESCRIPTION_KEYWORDS = {
    'friendly': 'friendly',
    'cheerful': 'cheerful',
    'warm': 'friendly',
    'professional': 'assistant',
    'scientist': 'assistant',
    'teacher': 'assistant',
    'enthusiastic': 'excited',
    'calm': 'assistant',
    'gentle': 'friendly',
    'energetic': 'excited',
    'passionate': 'excited',
    'wise': 'assistant',
    'approachable': 'friendly'
}

# Emotion intensity degrees
EMOTION_DEGREES = {
    'excited': 1.2,       # Reduced from default 1.5 to be less intense
    'enthusiastic': 1.3,  # Slightly enthusiastic
    'cheerful': 1.1,      # Slightly above normal
    'happy': 1.1,
    'friendly': 1.0,      # Normal intensity
    'encouraging': 1.1,   # Slightly enthusiastic
    'joking': 1.2,        # Playful but not too much
    'playful': 1.2,
    
    # Narrator tones - more subdued for professional feel
    'informative': 0.9,   # Slightly subdued for clear information delivery
    'thoughtful': 0.8,    # Calm and contemplative
    'reassuring': 0.85,   # Gentle and calming
    'educational': 0.95,  # Clear and measured
    
    # Calm emotions
    'gentle': 0.7,
    'calm': 0.6,
    'serious': 0.75,
    'professional': 0.9,
    
    # Curious/Engaging
    'curious': 0.95,
    'engaging': 1.0,
    'illustrative': 0.95,
    
    # Emphatic
    'emphatic': 1.15,
    'empathetic': 0.9,
    'caring': 0.85,
}

# Supported styles per voice
VOICE_SUPPORTED_STYLES = {
    "en-US-JennyNeural": [
        "assistant", "chat", "customerservice", "newscast", 
        "angry", "cheerful", "sad", "excited", "friendly", 
        "terrified", "shouting", "unfriendly", "whispering", "hopeful"
    ],
    "en-US-GuyNeural": [
        "newscast", "angry", "cheerful", "sad", "excited", "friendly", 
        "terrified", "shouting", "unfriendly", "whispering", "hopeful"
    ],
    "en-US-AriaNeural": [
        "cheerful", "excited", "friendly", "hopeful", "sad", 
        "angry", "terrified", "shouting", "unfriendly", "whispering"
    ]
}

# Voice selection
NARRATOR_VOICE = "en-US-JennyNeural"
MALE_CHARACTER_VOICE = "en-US-GuyNeural"
FEMALE_CHARACTER_VOICE = "en-US-AriaNeural"