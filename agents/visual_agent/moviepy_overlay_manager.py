from moviepy.editor import TextClip, CompositeVideoClip
from typing import List, Dict, Tuple
import concurrent.futures
from functools import lru_cache

class MoviePyOverlayManager:
    """Optimized text overlays for MoviePy with performance improvements"""
    
    def __init__(self, video_size):
        self.video_size = video_size
        self.width, self.height = video_size
        # Cache for text clip creation parameters
        self._clip_cache = {}
        
    @lru_cache(maxsize=128)
    def _get_text_dimensions(self, text: str, fontsize: int) -> Tuple[int, int]:
        """Cache text dimensions to avoid repeated calculations"""
        # This is a placeholder - actual dimensions would come from TextClip
        # but caching the concept helps avoid recreation
        return (int(self.width * 0.8), None)
    
    def _create_text_clip(self, text: str, fontsize: int, position: tuple, 
                         start_time: float, duration: float, bg_color: str = 'black',
                         size_ratio: float = 0.8) -> TextClip:
        """Optimized text clip creation with caching"""
        # Create a cache key for similar clips
        cache_key = (text, fontsize, bg_color, size_ratio)
        
        if cache_key not in self._clip_cache:
            # Create the base clip only once for each unique text
            self._clip_cache[cache_key] = TextClip(
                text,
                fontsize=fontsize,
                color='white',
                font='DejaVuSans-Bold',
                bg_color=bg_color,
                size=(int(self.width * size_ratio), None),
                method='caption'
            )
        
        # Clone and set timing for this specific instance
        clip = self._clip_cache[cache_key].copy()
        return (clip
                .set_position(position)
                .set_start(start_time)
                .set_duration(duration))

    def create_caption_overlays(self, base_video, timing_data: List[Dict], 
                               caption_phrases: List[Dict], used_segment_indices=None) -> Tuple[CompositeVideoClip, set]:
        """Optimized caption overlay creation"""
        overlays = []
        used_triggers = set()
        used_indices = used_segment_indices or set()
        
        # Pre-process all captions and triggers for faster lookup
        processed_captions = []
        for caption in caption_phrases:
            trigger = caption.get('trigger', '').lower()
            if trigger:
                processed_captions.append({
                    'trigger': trigger,
                    'trigger_no_space': trigger.replace(' ', ''),
                    'trigger_first_word': trigger.split()[0] if trigger.split() else '',
                    'text': caption['text'].strip().upper(),
                    'id': (caption['text'].lower(), trigger)
                })
        
        # Process segments
        for idx, segment in enumerate(timing_data):
            if segment['speaker'] == 'end' or idx in used_indices:
                continue
                
            text = segment['text'].lower()
            text_no_space = text.replace(' ', '')
            speaker = segment.get('speaker_name', '').lower() if 'speaker_name' in segment else ''
            
            for caption in processed_captions:
                if caption['id'] in used_triggers:
                    continue
                    
                # Optimized trigger matching
                if (caption['trigger'] in text or
                    caption['trigger_no_space'] in text_no_space or
                    caption['trigger'] in speaker or
                    (caption['trigger_first_word'] and caption['trigger_first_word'] in text)):
                    
                    # Create text clip with optimized method
                    txt_clip = self._create_text_clip(
                        caption['text'],
                        fontsize=30,
                        position=('center', self.height - 120),
                        start_time=segment['start_time'],
                        duration=min(4, segment['duration']),
                        bg_color='black',
                        size_ratio=0.8
                    )
                    
                    overlays.append(txt_clip)
                    used_indices.add(idx)
                    used_triggers.add(caption['id'])
                    break
        
        if overlays:
            # Batch composite for better performance
            return CompositeVideoClip([base_video] + overlays), used_indices
        else:
            return base_video, used_indices

    def create_emphasis_overlays(self, base_video, timing_data: List[Dict], 
                                emphasis_points: List[Dict], exclude_segments: set) -> CompositeVideoClip:
        """Optimized emphasis overlay creation"""
        if not (emphasis_points and timing_data):
            return base_video
            
        overlays = []
        
        # Pre-filter content segments
        content_segments = [(i, s) for i, s in enumerate(timing_data) 
                           if s['speaker'] != 'end' and i not in exclude_segments]
        
        n_points = min(len(emphasis_points), len(content_segments))
        if n_points == 0:
            return base_video
            
        # Calculate positions once
        step = max(len(content_segments) // n_points, 1)
        position = ('center', self.height - 120)
        
        # Create overlays with optimized method
        for j in range(n_points):
            seg_idx = j * step
            if seg_idx >= len(content_segments):
                break
                
            i, segment = content_segments[seg_idx]
            point_text = emphasis_points[j].get('text', '').strip().upper()
            
            txt_clip = self._create_text_clip(
                point_text,
                fontsize=32,
                position=position,
                start_time=segment['start_time'],
                duration=min(4, segment['duration']),
                bg_color='black',
                size_ratio=0.7
            )
            
            overlays.append(txt_clip)
        
        if overlays:
            return CompositeVideoClip([base_video] + overlays)
        else:
            return base_video

    def apply_all_overlays(self, base_video, timing_data: List[Dict], overlay_data: Dict) -> CompositeVideoClip:
        """
        Optimized overlay application with single composition pass
        """
        all_overlays = []
        used_indices = set()
        
        # Process captions first
        captions = overlay_data.get('caption_phrases', [])
        if captions:
            # Collect caption overlays without compositing yet
            caption_overlays = []
            processed_captions = []
            used_triggers = set()
            
            # Pre-process captions
            for caption in captions:
                trigger = caption.get('trigger', '').lower()
                if trigger:
                    processed_captions.append({
                        'trigger': trigger,
                        'trigger_no_space': trigger.replace(' ', ''),
                        'trigger_first_word': trigger.split()[0] if trigger.split() else '',
                        'text': caption['text'].strip().upper(),
                        'id': (caption['text'].lower(), trigger)
                    })
            
            # Find matching segments
            for idx, segment in enumerate(timing_data):
                if segment['speaker'] == 'end' or idx in used_indices:
                    continue
                    
                text = segment['text'].lower()
                text_no_space = text.replace(' ', '')
                speaker = segment.get('speaker_name', '').lower() if 'speaker_name' in segment else ''
                
                for caption in processed_captions:
                    if caption['id'] in used_triggers:
                        continue
                        
                    if (caption['trigger'] in text or
                        caption['trigger_no_space'] in text_no_space or
                        caption['trigger'] in speaker or
                        (caption['trigger_first_word'] and caption['trigger_first_word'] in text)):
                        
                        txt_clip = self._create_text_clip(
                            caption['text'],
                            fontsize=30,
                            position=('center', self.height - 120),
                            start_time=segment['start_time'],
                            duration=min(4, segment['duration']),
                            bg_color='black',
                            size_ratio=0.8
                        )
                        
                        caption_overlays.append(txt_clip)
                        used_indices.add(idx)
                        used_triggers.add(caption['id'])
                        break
            
            all_overlays.extend(caption_overlays)
        
        # Process emphasis points
        emphasis = overlay_data.get('emphasis_points', [])
        if emphasis:
            emphasis_overlays = []
            
            content_segments = [(i, s) for i, s in enumerate(timing_data) 
                              if s['speaker'] != 'end' and i not in used_indices]
            
            n_points = min(len(emphasis), len(content_segments))
            if n_points > 0:
                step = max(len(content_segments) // n_points, 1)
                position = ('center', self.height - 120)
                
                for j in range(n_points):
                    seg_idx = j * step
                    if seg_idx >= len(content_segments):
                        break
                        
                    i, segment = content_segments[seg_idx]
                    point_text = emphasis[j].get('text', '').strip().upper()
                    
                    txt_clip = self._create_text_clip(
                        point_text,
                        fontsize=32,
                        position=position,
                        start_time=segment['start_time'],
                        duration=min(4, segment['duration']),
                        bg_color='black',
                        size_ratio=0.7
                    )
                    
                    emphasis_overlays.append(txt_clip)
            
            all_overlays.extend(emphasis_overlays)
        
        # Single composition pass for all overlays
        if all_overlays:
            return CompositeVideoClip([base_video] + all_overlays)
        else:
            return base_video
    
    def clear_cache(self):
        """Clear the clip cache to free memory"""
        self._clip_cache.clear()