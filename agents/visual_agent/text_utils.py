# text_utils.py - Text and Font Management Utilities

from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Optional, Tuple
from .constants import FONT_PATHS, FONT_SIZES

class TextManager:
    """Manages font loading and text operations"""
    
    def __init__(self):
        self.fonts = self._load_fonts()
        self._temp_img = Image.new('RGB', (1, 1))
        self._temp_draw = ImageDraw.Draw(self._temp_img)
    
    def _load_fonts(self) -> Dict[str, Optional[ImageFont.FreeTypeFont]]:
        """Load fonts with fallbacks"""
        fonts = {}
        
        for font_type, paths in FONT_PATHS.items():
            loaded = False
            for path in paths:
                try:
                    if font_type == 'title':
                        fonts['title'] = ImageFont.truetype(path, FONT_SIZES['title'], 
                                                           index=1 if 'Helvetica' in path else 0)
                        fonts['speaker'] = ImageFont.truetype(path, FONT_SIZES['speaker'], 
                                                             index=1 if 'Helvetica' in path else 0)
                    else:
                        fonts['body'] = ImageFont.truetype(path, FONT_SIZES['body'])
                        fonts['progress'] = ImageFont.truetype(path, FONT_SIZES['progress'])
                    loaded = True
                    break
                except:
                    continue
            
            if not loaded:
                print(f"⚠️ Using default font for {font_type}")
                fonts['title'] = ImageFont.load_default()
                fonts['body'] = ImageFont.load_default()
                fonts['speaker'] = ImageFont.load_default()
                fonts['progress'] = ImageFont.load_default()
                
        return fonts
    
    def get_font(self, font_type: str) -> ImageFont.FreeTypeFont:
        """Get font by type"""
        return self.fonts.get(font_type, self.fonts['body'])
    
    def wrap_text(self, text: str, font_type: str, max_width: int) -> List[str]:
        """Wrap text to fit within max_width"""
        font = self.get_font(font_type)
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = self._temp_draw.textbbox((0, 0), test_line, font=font)
            test_width = bbox[2] - bbox[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def get_text_dimensions(self, text: str, font_type: str) -> Tuple[int, int]:
        """Get width and height of text"""
        font = self.get_font(font_type)
        bbox = self._temp_draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    def get_multiline_dimensions(self, lines: List[str], font_type: str, line_spacing: float) -> Tuple[int, int]:
        """Get dimensions of multiline text"""
        font = self.get_font(font_type)
        
        # Calculate text width (max line width)
        text_width = 0
        for line in lines:
            bbox = self._temp_draw.textbbox((0, 0), line, font=font)
            text_width = max(text_width, bbox[2] - bbox[0])
        
        # Calculate text height
        line_height = font.size * line_spacing
        text_height = len(lines) * line_height
        
        return text_width, text_height