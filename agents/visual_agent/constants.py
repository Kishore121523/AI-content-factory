# Video settings
VIDEO_SIZE = (1280, 720)  # HD
FPS = 24
VIDEO_CODEC = 'libx264'
AUDIO_CODEC = 'aac'
VIDEO_PRESET = 'faster'
VIDEO_THREADS = 8
VIDEO_BITRATE = "2000k"

# Avatar settings
AVATAR_SIZE = 300  # Large avatar size
AVATAR_SIZE_TITLE = 250  # Avatar size for title slide
NARRATOR_AVATAR_ID = 1  # Fixed avatar for narrator (female)

# Professional educational color scheme
COLORS = {
    "background": (250, 250, 250),
    "header_bg": (74, 144, 226),
    "footer_bg": (245, 247, 250),
    "character_bubble": (232, 244, 253),
    "character_border": (74, 144, 226),
    "narrator_bubble": (232, 249, 233),
    "narrator_border": (76, 175, 80),
    "title_text": (255, 255, 255),
    "body_text": (44, 62, 80),
    "speaker_text": (52, 73, 94),
    "progress_text": (127, 140, 141),
    "shadow": (220, 220, 220),
}

# Layout settings
LAYOUT = {
    "margin": 60,
    "header_height": 80,
    "footer_height": 50,
    "bubble_padding": 35,
    "line_spacing": 1.4,
    "avatar_size": AVATAR_SIZE,
}

# Font settings
FONT_SIZES = {
    'title': 40,
    'body': 28,
    'speaker': 24,
    'progress': 18
}

FONT_PATHS = {
    'title': [
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ],
    'body': [
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
}

# Timing settings
MIN_DURATIONS = {
    'title': 3.0,
    'end': 2.5,
    'character': 2.0,
    'narrator': 2.0
}

# Transition settings
FADE_DURATION = 0.2
CROSSFADE_DURATION = 0.5
PADDING_DURATION = 0.7  # Audio padding to prevent early transitions

# Header settings
HEADER_HEIGHT_TITLE = 280
TITLE_MAX_LENGTH = 50

# Progress bar settings
PROGRESS_WIDTH = 250
PROGRESS_HEIGHT = 6

# Speech tail settings
TAIL_WIDTH = 20
TAIL_OFFSET = 40

# Badge settings
BADGE_PADDING = 25
NAME_BG_PADDING = 15

# Default durations
DEFAULT_SLIDE_DURATION = 3.5
END_SLIDE_DURATION = 3.0