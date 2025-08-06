# voice_agent/script_processor.py - Script Processing Utilities

import re
from typing import List, Dict

class ScriptProcessor:
    """Handles script parsing and text processing"""
    
    @staticmethod
    def parse_script_with_emotions(script: str, character_name: str) -> List[Dict]:
        """Parse script into segments with speaker, text, and emotion"""
        segments = []
        
        # Clean script first - remove section headers
        script = re.sub(r'^(Introduction|Body|Summary/Call to Action|Summary):?\s*$', '', 
                       script, flags=re.MULTILINE)
        
        current_speaker = None
        current_emotion = 'neutral'
        buffer = []

        for line in script.splitlines():
            line = line.strip()
            if not line:
                continue

            # Match speaker pattern with emotion
            pattern = rf"({re.escape(character_name)}|Narrator)\s*\(([^)]+)\):\s*(.*)"
            match = re.match(pattern, line)
            
            if match:
                # Save previous segment
                if current_speaker and buffer:
                    combined_text = " ".join(buffer).strip()
                    if combined_text:
                        segments.append({
                            'speaker': current_speaker,
                            'text': combined_text,
                            'emotion': current_emotion
                        })
                
                # Start new segment
                current_speaker = match.group(1)
                current_emotion = match.group(2).strip()
                remaining_text = match.group(3).strip()
                buffer = [remaining_text] if remaining_text else []
            else:
                # Continue current speaker's text
                if current_speaker and line:
                    buffer.append(line)

        # Don't forget the last segment
        if current_speaker and buffer:
            combined_text = " ".join(buffer).strip()
            if combined_text:
                segments.append({
                    'speaker': current_speaker,
                    'text': combined_text,
                    'emotion': current_emotion
                })

        return segments
    
    @staticmethod
    def escape_xml_text(text: str) -> str:
        """Escape text for XML/SSML"""
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&apos;')
        return text