# ui_components.py - Reusable UI Component Rendering

from PIL import ImageDraw
from typing import List, Tuple
from .constants import *

class UIComponents:
    """Renders reusable UI components"""
    
    def __init__(self, text_manager):
        self.text_manager = text_manager
    
    def draw_header(self, draw: ImageDraw.Draw, lesson_title: str, video_size: Tuple[int, int]):
        """Draw header with lesson title"""
        draw.rectangle([0, 0, video_size[0], LAYOUT['header_height']], 
                      fill=COLORS['header_bg'])
        
        title_text = lesson_title[:TITLE_MAX_LENGTH] + "..." if len(lesson_title) > TITLE_MAX_LENGTH else lesson_title
        
        font = self.text_manager.get_font('speaker')
        bbox = draw.textbbox((0, 0), title_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (video_size[0] - text_width) // 2
        text_y = (LAYOUT['header_height'] - (bbox[3] - bbox[1])) // 2
        
        draw.text((text_x, text_y), title_text, font=font, fill=COLORS['title_text'])
    
    def draw_footer(self, draw: ImageDraw.Draw, slide_number: int, total_slides: int, video_size: Tuple[int, int]):
        """Draw footer with progress bar and page number"""
        footer_top = video_size[1] - LAYOUT['footer_height']
        
        # Progress bar
        progress_x = LAYOUT['margin']
        progress_y = footer_top + (LAYOUT['footer_height'] - PROGRESS_HEIGHT) // 2
        
        draw.rectangle([progress_x, progress_y, 
                       progress_x + PROGRESS_WIDTH, progress_y + PROGRESS_HEIGHT],
                      fill=(220, 220, 220))
        
        fill_width = int(PROGRESS_WIDTH * (slide_number / total_slides))
        draw.rectangle([progress_x, progress_y,
                       progress_x + fill_width, progress_y + PROGRESS_HEIGHT],
                      fill=COLORS['header_bg'])
        
        # Page number
        page_text = f"{slide_number}/{total_slides}"
        font = self.text_manager.get_font('progress')
        bbox = draw.textbbox((0, 0), page_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = video_size[0] - LAYOUT['margin'] - text_width
        text_y = footer_top + (LAYOUT['footer_height'] - (bbox[3] - bbox[1])) // 2
        
        draw.text((text_x, text_y), page_text, font=font, fill=COLORS['progress_text'])
    
    def draw_speech_tail(self, draw: ImageDraw.Draw, bubble_rect: List[int],
                         bubble_side: str, avatar_x: int, avatar_y: int, 
                         avatar_size: int, fill_color: tuple, outline_color: tuple):
        """Draw speech tail pointing to avatar"""
        x1, y1, x2, y2 = bubble_rect
        
        avatar_center_y = avatar_y + avatar_size // 2
        
        if bubble_side == 'left':
            tail_base_x = x2
            # tail_tip_x = avatar_x + TAIL_OFFSET
            tail_tip_x = avatar_x
        else:
            tail_base_x = x1
            tail_tip_x = avatar_x + avatar_size - TAIL_OFFSET
        
        bubble_center_y = (y1 + y2) // 2
        tail_base_y = bubble_center_y
        tail_tip_y = avatar_center_y
        
        tail_points = [
            (tail_base_x, tail_base_y - TAIL_WIDTH),
            (tail_tip_x, tail_tip_y),
            (tail_base_x, tail_base_y + TAIL_WIDTH)
        ]
        
        draw.polygon(tail_points, fill=fill_color, outline=outline_color, width=3)
    
    def draw_badge(self, draw: ImageDraw.Draw, text: str, position: Tuple[int, int], 
                   badge_type: str = 'character'):
        """Draw a text badge with background"""
        font = self.text_manager.get_font('speaker')
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x, y = position
        
        # Badge background
        badge_rect = [
            x - BADGE_PADDING,
            y - BADGE_PADDING // 2,
            x + text_width + BADGE_PADDING,
            y + text_height + BADGE_PADDING // 2
        ]
        
        if badge_type == 'character':
            fill_color = COLORS['character_bubble']
            outline_color = COLORS['character_border']
        else:
            fill_color = COLORS['narrator_bubble']
            outline_color = COLORS['narrator_border']
        
        draw.rectangle(badge_rect, fill=fill_color, outline=outline_color, width=2)
        draw.text((x, y), text, font=font, fill=COLORS['speaker_text'])
        
        return badge_rect
    
    def draw_speech_bubble(self, draw: ImageDraw.Draw, bubble_rect: List[int], 
                          text_lines: List[str], is_character: bool):
        """Draw speech bubble with text"""
        # Shadow
        shadow_rect = [bubble_rect[0] + 3, bubble_rect[1] + 3, 
                      bubble_rect[2] + 3, bubble_rect[3] + 3]
        draw.rectangle(shadow_rect, fill=COLORS['shadow'])
        
        # Bubble
        if is_character:
            fill_color = COLORS['character_bubble']
            outline_color = COLORS['character_border']
        else:
            fill_color = COLORS['narrator_bubble']
            outline_color = COLORS['narrator_border']
        
        draw.rectangle(bubble_rect, fill=fill_color, outline=outline_color, width=3)
        
        # Text
        font = self.text_manager.get_font('body')
        line_height = font.size * LAYOUT['line_spacing']
        text_x = bubble_rect[0] + LAYOUT['bubble_padding']
        text_y = bubble_rect[1] + LAYOUT['bubble_padding']
        
        for i, line in enumerate(text_lines):
            line_y = text_y + i * line_height
            draw.text((text_x, line_y), line, font=font, fill=COLORS['body_text'])