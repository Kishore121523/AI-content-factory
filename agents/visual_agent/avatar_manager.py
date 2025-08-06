# avatar_manager.py - Avatar Loading and Management

import os
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Dict
from .constants import AVATAR_SIZE, COLORS

class AvatarManager:
    """Manages avatar loading, caching, and creation"""
    
    def __init__(self, avatar_dir: str = "avatars"):
        self.avatar_dir = avatar_dir
        self.avatar_cache: Dict[str, Image.Image] = {}
    
    def load_avatar(self, gender: str, avatar_id: int, size: int = AVATAR_SIZE) -> Optional[Image.Image]:
        """Load and cache avatar image"""
        cache_key = f"{gender}_{avatar_id}_{size}"
        
        if cache_key in self.avatar_cache:
            return self.avatar_cache[cache_key]
        
        avatar_path = os.path.join(self.avatar_dir, gender, f"avatar_{avatar_id}.png")
        
        try:
            avatar = Image.open(avatar_path).convert("RGBA")
            avatar = avatar.resize((size, size), Image.Resampling.LANCZOS)
            self.avatar_cache[cache_key] = avatar
            print(f"✅ Loaded avatar: {avatar_path}")
            return avatar
        except Exception as e:
            print(f"⚠️ Could not load avatar {avatar_path}: {e}")
            return None
    
    def create_default_avatar(self, initial: str, is_character: bool, size: int = AVATAR_SIZE) -> Image.Image:
        """Create a default avatar if image not found"""
        avatar = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(avatar)
        
        # Choose color based on speaker type
        bg_color = COLORS['character_border'] if is_character else COLORS['narrator_border']
        
        # Draw circle
        draw.ellipse([0, 0, size-1, size-1], fill=bg_color)
        
        # Draw initial
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(size * 0.4))
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), initial, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (size - text_width) // 2
        text_y = (size - text_height) // 2
        
        draw.text((text_x, text_y), initial, font=font, fill=(255, 255, 255))
        
        return avatar
    
    def get_avatar(self, character: Dict, is_narrator: bool = False, 
                   narrator_avatar_id: int = 1, size: int = AVATAR_SIZE) -> Image.Image:
        """Get avatar for character or narrator, with fallback to default"""
        if is_narrator:
            avatar = self.load_avatar('female', narrator_avatar_id, size)
            initial = 'N'
            is_character = False
        else:
            avatar = self.load_avatar(character['gender'], character.get('avatar_id', 1), size)
            initial = character['name'][0].upper()
            is_character = True
        
        if avatar is None:
            avatar = self.create_default_avatar(initial, is_character, size)
        
        return avatar
    
    def clear_cache(self):
        """Clear avatar cache"""
        self.avatar_cache.clear()