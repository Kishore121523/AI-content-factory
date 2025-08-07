from PIL import Image, ImageDraw
from typing import Dict, Tuple
from .constants import *
from .avatar_manager import AvatarManager
from .text_utils import TextManager
from .ui_components import UIComponents
from .moviepy_overlay_manager import MoviePyOverlayManager

class SlideRenderer:
    """Renders different types of slides"""
    
    def __init__(self, video_size: Tuple[int, int], avatar_manager: AvatarManager, 
                 text_manager: TextManager):
        self.video_size = video_size
        self.avatar_manager = avatar_manager
        self.text_manager = text_manager
        self.ui_components = UIComponents(text_manager)
        self.overlay_manager = MoviePyOverlayManager(VIDEO_SIZE)

    def render_title_slide(self, lesson_title: str, character: Dict) -> Image.Image:
        """Render title slide with avatar"""
        img = Image.new('RGB', self.video_size, COLORS['background'])
        draw = ImageDraw.Draw(img)
        
        # Header
        draw.rectangle([0, 0, self.video_size[0], HEADER_HEIGHT_TITLE], fill=COLORS['header_bg'])
        
        # Title
        title_lines = self.text_manager.wrap_text(lesson_title, 'title', self.video_size[0] - 160)
        title_text = '\n'.join(title_lines)
        
        title_width, title_height = self.text_manager.get_text_dimensions(title_text, 'title')
        title_x = (self.video_size[0] - title_width) // 2
        title_y = (HEADER_HEIGHT_TITLE - title_height) // 2
        
        font = self.text_manager.get_font('title')
        draw.text((title_x, title_y), title_text, font=font, 
                 fill=COLORS['title_text'], align='center')
        
        # Avatar
        avatar = self.avatar_manager.get_avatar(character, size=AVATAR_SIZE_TITLE)
        avatar_x = (self.video_size[0] - AVATAR_SIZE_TITLE) // 2
        avatar_y = HEADER_HEIGHT_TITLE + 40
        
        img_rgba = img.convert('RGBA')
        img_rgba.paste(avatar, (avatar_x, avatar_y), avatar)
        img = img_rgba.convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # Presenter info
        presenter_text = f"YOUR GUIDE: {character['name'].upper()}"
        text_width, text_height = self.text_manager.get_text_dimensions(presenter_text, 'speaker')
        text_x = (self.video_size[0] - text_width) // 2
        text_y = avatar_y + AVATAR_SIZE_TITLE + 30
        
        self.ui_components.draw_badge(draw, presenter_text, (text_x, text_y), 'character')
        
        return img
    
    def render_content_slide(self, text: str, speaker_type: str, speaker_name: str,
                            character: Dict, lesson_title: str, slide_number: int, 
                            total_slides: int,
                            highlight_words: list = None,
                            ) -> Image.Image:
        """Render content slide with large avatar taking half screen and in-bubble highlights."""
        img = Image.new('RGB', self.video_size, COLORS['background'])
        draw = ImageDraw.Draw(img)

        highlight_words = highlight_words or []

        # Header
        self.ui_components.draw_header(draw, lesson_title, self.video_size)
        content_top = LAYOUT['header_height'] + 20
        content_bottom = self.video_size[1] - LAYOUT['footer_height'] - 20
        content_height = content_bottom - content_top

        # Side
        is_character = speaker_type == 'character'
        screen_mid = self.video_size[0] // 2
        if is_character:
            avatar_x = screen_mid // 2 - LAYOUT['avatar_size'] // 2
            bubble_side = 'right'
        else:
            avatar_x = screen_mid + screen_mid // 2 - LAYOUT['avatar_size'] // 2
            bubble_side = 'left'
        avatar_y = content_top + (content_height - LAYOUT['avatar_size']) // 2 - 40
        avatar = self.avatar_manager.get_avatar(character, is_narrator=(not is_character),
                                            narrator_avatar_id=NARRATOR_AVATAR_ID)
        img_rgba = img.convert('RGBA')
        img_rgba.paste(avatar, (avatar_x, avatar_y), avatar)
        img = img_rgba.convert('RGB')
        draw = ImageDraw.Draw(img)

        # Bubble
        if bubble_side == 'right':
            bubble_area_start = screen_mid + 20
            bubble_area_end = self.video_size[0] - LAYOUT['margin']
        else:
            bubble_area_start = LAYOUT['margin']
            bubble_area_end = screen_mid - 30
        bubble_area_width = bubble_area_end - bubble_area_start
        max_text_width = bubble_area_width - LAYOUT['bubble_padding'] * 2 - 40
        wrapped_lines = self.text_manager.wrap_text(text, 'body', max_text_width)
        text_width, text_height = self.text_manager.get_multiline_dimensions(
            wrapped_lines, 'body', LAYOUT['line_spacing'])
        bubble_width = min(text_width + LAYOUT['bubble_padding'] * 2, bubble_area_width - 20)
        bubble_height = text_height + LAYOUT['bubble_padding'] * 2
        bubble_x = bubble_area_start + (bubble_area_width - bubble_width) // 2
        bubble_y = avatar_y + (LAYOUT['avatar_size'] - bubble_height) // 2
        if bubble_y < content_top + 20:
            bubble_y = content_top + 20
        if bubble_y + bubble_height > content_bottom - 20:
            bubble_y = content_bottom - bubble_height - 20
        bubble_rect = [bubble_x, bubble_y, bubble_x + bubble_width, bubble_y + bubble_height]

        # Draw bubble with text (no highlights yet)
        self.ui_components.draw_speech_bubble(draw, bubble_rect, is_character)

        font = self.text_manager.get_font('body')
        self.ui_components.draw_highlighted_text_with_phrases(
            img, bubble_rect, wrapped_lines, highlight_words, font
        )

        bubble_fill = COLORS['character_bubble'] if is_character else COLORS['narrator_bubble']
        bubble_outline = COLORS['character_border'] if is_character else COLORS['narrator_border']
        self.ui_components.draw_speech_tail(draw, bubble_rect, bubble_side, 
                                        avatar_x, avatar_y, LAYOUT['avatar_size'],
                                        bubble_fill, bubble_outline)

        # Speaker badge
        name_text = speaker_name if is_character else "Narrator"
        name_width, name_height = self.text_manager.get_text_dimensions(name_text, 'speaker')
        name_x = avatar_x + (LAYOUT['avatar_size'] - name_width) // 2
        name_y = avatar_y + LAYOUT['avatar_size'] + 15
        self.ui_components.draw_badge(draw, name_text, (name_x, name_y), 
                                    'character' if is_character else 'narrator')

        # Footer
        self.ui_components.draw_footer(draw, slide_number, total_slides, self.video_size)
        return img

    def render_end_slide(self, lesson_title: str) -> Image.Image:
        """Render end slide"""
        img = Image.new('RGB', self.video_size, COLORS['background'])
        draw = ImageDraw.Draw(img)
        
        # Thank you text
        thank_you_text = "Thank you for learning with us!"
        text_width, text_height = self.text_manager.get_text_dimensions(thank_you_text, 'title')
        text_x = (self.video_size[0] - text_width) // 2
        text_y = self.video_size[1] // 2 - 80
        
        font = self.text_manager.get_font('title')
        draw.text((text_x, text_y), thank_you_text, font=font, fill=COLORS['header_bg'])
        
        # Lesson completed badge
        badge_text = f"Lesson Completed: {lesson_title}"
        badge_width, badge_height = self.text_manager.get_text_dimensions(badge_text, 'speaker')
        badge_x = (self.video_size[0] - badge_width) // 2
        badge_y = text_y + text_height + 60
        
        self.ui_components.draw_badge(draw, badge_text, (badge_x, badge_y), 'character')
        
        return img