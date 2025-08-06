# script_parser.py - Script Parsing Utilities

import re
from typing import List, Dict

class ScriptParser:
    """Parses scripts into slides"""
    
    @staticmethod
    def parse_script_to_slides(script: str, character_name: str) -> List[Dict]:
        """Parse script into individual slides with improved detection"""
        slides = []
        
        # Add title slide
        slides.append({
            'type': 'title',
            'text': '',
            'speaker_name': '',
            'duration_weight': 0.08
        })
        
        # Clean the script
        script = script.strip()
        
        # Remove section headers
        section_headers = ['Introduction:', 'Body:', 'Summary/Call to Action:', 'Summary:']
        for header in section_headers:
            script = script.replace(header, '')
        
        # Split into lines and process
        lines = script.split('\n')
        current_speaker = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Improved pattern to match speakers with emotions
            speaker_pattern = rf'({re.escape(character_name)}|Narrator)\s*\([^)]+\):\s*(.*)'
            match = re.match(speaker_pattern, line)
            
            if match:
                # Save previous slide if exists
                if current_speaker and current_text:
                    text = ' '.join(current_text).strip()
                    if text:
                        slides.append({
                            'type': 'character' if current_speaker == character_name else 'narrator',
                            'text': text,
                            'speaker_name': current_speaker,
                            'duration_weight': min(len(text) / 80, 0.15)
                        })
                
                # Start new slide
                current_speaker = match.group(1)
                remaining_text = match.group(2).strip()
                current_text = [remaining_text] if remaining_text else []
            else:
                # Continue current speaker's text
                if current_speaker and line:
                    current_text.append(line)
        
        # Don't forget the last slide
        if current_speaker and current_text:
            text = ' '.join(current_text).strip()
            if text:
                slides.append({
                    'type': 'character' if current_speaker == character_name else 'narrator',
                    'text': text,
                    'speaker_name': current_speaker,
                    'duration_weight': min(len(text) / 80, 0.15)
                })
        
        # Add end slide
        slides.append({
            'type': 'end',
            'text': 'Thank you for learning with us!',
            'speaker_name': '',
            'duration_weight': 0.05
        })
        
        return slides
    
    @staticmethod
    def clean_script(script: str) -> str:
        """Clean script text"""
        # Remove extra whitespace
        script = ' '.join(script.split())
        
        # Remove common artifacts
        script = script.replace('\n\n', '\n')
        script = script.strip()
        
        return script