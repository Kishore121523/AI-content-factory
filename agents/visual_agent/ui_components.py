import re
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

    @staticmethod
    def preprocess_phrases(phrases):
        # Tokenize phrases: 'rag agents' -> ['rag', 'agents']
        return [re.findall(r"\w+", phrase.lower()) for phrase in phrases if phrase]
    
    def draw_speech_bubble(self, draw: ImageDraw.Draw, bubble_rect, is_character):
        """Draw only the bubble (shape + shadow), no text."""
        # Shadow
        shadow_rect = [bubble_rect[0] + 3, bubble_rect[1] + 3, 
                    bubble_rect[2] + 3, bubble_rect[3] + 3]
        draw.rectangle(shadow_rect, fill=COLORS['shadow'])
        # Bubble main
        if is_character:
            fill_color = COLORS['character_bubble']
            outline_color = COLORS['character_border']
        else:
            fill_color = COLORS['narrator_bubble']
            outline_color = COLORS['narrator_border']
        draw.rectangle(bubble_rect, fill=fill_color, outline=outline_color, width=3)

    def draw_highlighted_text_with_phrases(self, img, bubble_rect, wrapped_lines, highlight_phrases, font):
        """
        Draw text with phrase/keyword highlighting inside a speech bubble, preserving original spacing and punctuation.
        """
        import re
        draw = ImageDraw.Draw(img)
        line_height = font.size * LAYOUT['line_spacing']
        text_x = bubble_rect[0] + LAYOUT['bubble_padding']
        text_y = bubble_rect[1] + LAYOUT['bubble_padding']

        # Prepare highlight phrases as list of lists, sorted longest first
        highlight_token_lists = self.preprocess_phrases(highlight_phrases)
        highlight_token_lists.sort(key=len, reverse=True)

        for line_idx, line in enumerate(wrapped_lines):
            current_x = text_x
            current_y = text_y + line_idx * line_height

            # Tokenize words + punctuation, but keep original positions
            tokens = re.findall(r'\w+|[^\w]', line)

            i = 0
            while i < len(tokens):
                matched = False
                # Attempt to match a phrase at current position
                for phrase_tokens in highlight_token_lists:
                    n = len(phrase_tokens)
                    # Extract a window of n tokens, skipping spaces and punctuation for matching
                    window = []
                    word_indices = []  # Track indices of actual words (not spaces/punctuation)
                    j = i
                    while len(window) < n and j < len(tokens):
                        if tokens[j].strip() and re.match(r'\w+', tokens[j]):  # is a word
                            window.append(tokens[j].lower())
                            word_indices.append(j)
                        j += 1
                    
                    if window == phrase_tokens:
                        # Draw any spaces/punctuation BEFORE the highlight
                        pre_highlight_idx = i
                        while pre_highlight_idx < len(tokens) and (pre_highlight_idx not in word_indices):
                            token = tokens[pre_highlight_idx]
                            bbox = draw.textbbox((0, 0), token, font=font)
                            token_width = bbox[2] - bbox[0]
                            draw.text((current_x, current_y), token, font=font, fill=COLORS['body_text'])
                            current_x += token_width
                            pre_highlight_idx += 1
                        
                        # Now highlight only the words (and spaces between them)
                        if word_indices:
                            first_word_idx = word_indices[0]
                            last_word_idx = word_indices[-1]
                            
                            # Build the phrase string from first word to last word (inclusive)
                            phrase_str = ''.join([tokens[k] for k in range(first_word_idx, last_word_idx + 1)])
                            
                            bbox = draw.textbbox((0, 0), phrase_str, font=font)
                            phrase_width = bbox[2] - bbox[0]
                            phrase_height = bbox[3] - bbox[1]
                            
                            # Draw highlight rectangle
                            draw.rectangle(
                                [current_x - 2, current_y - 2, current_x + phrase_width + 2, current_y + phrase_height + 2],
                                fill=(255, 235, 59)
                            )
                            # Draw highlighted text
                            draw.text((current_x, current_y), phrase_str, font=font, fill=(0, 0, 0))
                            current_x += phrase_width
                            
                            # Draw any trailing punctuation/spaces after the last word
                            for k in range(last_word_idx + 1, j):
                                token = tokens[k]
                                bbox = draw.textbbox((0, 0), token, font=font)
                                token_width = bbox[2] - bbox[0]
                                draw.text((current_x, current_y), token, font=font, fill=COLORS['body_text'])
                                current_x += token_width
                        
                        i = j  # move past the entire window
                        matched = True
                        break
                
                if not matched:
                    token = tokens[i]
                    bbox = draw.textbbox((0, 0), token, font=font)
                    token_width = bbox[2] - bbox[0]
                    # Default color for text
                    draw.text((current_x, current_y), token, font=font, fill=COLORS['body_text'])
                    current_x += token_width
                    i += 1
