# agents/script_agent.py

import difflib
import json
from agents.base_agent import Agent
import openai
import os
from dotenv import load_dotenv

load_dotenv()

class ScriptAgent(Agent):
    def __init__(self):
        super().__init__("ScriptAgent")
        self.client = openai.AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_LLM_KEY"),
            api_version=os.getenv("AZURE_OPENAI_LLM_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_LLM_ENDPOINT"),
        )
        self.deployment = os.getenv("AZURE_OPENAI_LLM_DEPLOYMENT_NAME")

    def run(self, input_data):
        character = input_data["character"]
        lessons = input_data["lessons"]

        all_scripts = []
        for i, lesson in enumerate(lessons, 1):
            print(f"📘 Generating expressive script for Lesson {i}: {lesson['title']}...")

            script = self.generate_script(character, lesson, i)

            # Extract key concepts and overlay points
            print(f"🔍 Extracting key concepts for dynamic overlays...")
            overlay_data = self.extract_overlay_data(lesson, script)

            all_scripts.append({
                "lesson": lesson["title"],
                "script": script,
                "overlay_data": overlay_data
            })
        return all_scripts

    def generate_script(self, character, lesson, lesson_number):
        # Extract character personality for better emotion matching
        personality_traits = self.extract_personality(character)
        
        system_prompt = (
            "You are a scriptwriter creating educational video dialogues with dynamic emotions. "
            "Generate a fun, engaging script for a character introducing and teaching a lesson topic. "
            "The script should be 300-400 words long, vivid, and expressive.\n\n"
            
            "IMPORTANT EMOTION GUIDELINES:\n"
            "- Use VARIED emotions that match the content and character personality\n"
            "- Available emotions for educational content: enthusiastic, cheerful, curious, thoughtful, "
            "friendly, warm, encouraging, calm, gentle, excited, engaging, illustrative, "
            "reassuring, emphatic, serious, professional, informative, joking, playful\n"
            "- Start with enthusiasm or curiosity to hook attention\n"
            "- Use 'thoughtful' or 'informative' when explaining concepts\n"
            "- Use 'excited' or 'cheerful' for interesting discoveries\n"
            "- Use 'encouraging' or 'reassuring' for complex topics\n"
            "- Use 'joking' or 'playful' sparingly for light moments\n"
            "- End with 'encouraging' or 'enthusiastic' for the call to action\n\n"
            
            "FORMAT YOUR SCRIPT EXACTLY LIKE THIS:\n"
            "Introduction:\n"
            f"{character['name']} (enthusiastic): Opening hook that grabs attention!\n"
            "Narrator (friendly): Context setting...\n\n"
            
            "Body:\n"
            f"{character['name']} (curious): Question or observation...\n"
            "Narrator (informative): Explanation...\n"
            f"{character['name']} (enthusiastic): Exciting discovery or example!\n"
            "Narrator (thoughtful): Deeper insight...\n\n"
            
            "Summary/Call to Action:\n"
            f"{character['name']} (encouraging): Summary and motivation to learn more!\n\n"
            
            f"Make sure EVERY line has a speaker with an emotion in parentheses and Make sure EVERY SEGMENT BY NARRATOR OR {character['name']} has NOT MROE THAN 50 WORDS!"
        )

        user_prompt = (
            f"Character Name: {character['name']}\n"
            f"Character Personality: {personality_traits}\n"
            f"Character Style: {character['voice_style']}\n"
            f"Lesson Title: {lesson['title']}\n"
            f"Lesson Summary: {lesson['summary']}\n\n"
            f"Generate an expressive educational script with varied emotions that match "
            f"both the content and the character's personality. "
            f"Remember to use only {character['name']} and Narrator as speakers."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            max_completion_tokens=5000  # (5000 gave good results) Increased for more expressive content
        )

        script = response.choices[0].message.content.strip()
        
        # Validate that emotions are included
        if not self.validate_emotions(script):
            print("⚠️ Script missing emotions, adding defaults...")
            script = self.add_default_emotions(script, character['name'])
        
        return script

    def extract_overlay_data(self, lesson, script):
        """Use LLM to extract key concepts and overlay points from the script"""
        system_prompt = (
            "You are an educational content analyzer. Given a lesson script, extract:\n"
            "1. Key terms/concepts that should be highlighted (technical terms, important vocabulary)\n"
            "2. Important phrases that should appear as captions\n"
            "- For each caption in caption_phrases:\n"
            "    - The 'trigger' field must be an exact phrase (verbatim substring) found in the script. Do not invent or paraphrase trigger phrases. Only use phrases that actually appear in the script text.\n"
            "    - The 'text' field should be a short, punchy, or summarizing caption related to the trigger, but NOT a verbatim repeat. Paraphrase or clarify the meaning in a concise way (under 10 words).\n"
            "\n"
            "3. Section markers where visual emphasis would help (as 'emphasis_points').\n"
            "- For emphasis_points: Always include at least one definition (in the form 'Term: definition') and at least one key_fact (the single most important takeaway or summary statement, even if you must reword the script). \n"
            "Respond ONLY with valid JSON in this format:\n"
            "{\n"
            '  "highlight_keywords": ["term1", "term2", ...],\n'
            '  "caption_phrases": [\n'
            '    {"text": "Important phrase", "trigger": "when this is said"},\n'
            '    ...\n'
            '  ],\n'
            '  "emphasis_points": [\n'
            '    {"type": "definition", "text": "Term: definition"},\n'
            '    {"type": "key_fact", "text": "Important fact"},\n'
            '    ...\n'
            '  ]\n'
            "}\n"
            "Example output:\n"
            "{\n"
            '  "highlight_keywords": ["transformer", "self-attention"],\n'
            '  "caption_phrases": [{"text": "Revolutionized AI", "trigger": "revolutionizing AI"}],\n'
            '  "emphasis_points": [\n'
            '    {"type": "definition", "text": "Transformer: An AI model that uses self-attention."},\n'
            '    {"type": "key_fact", "text": "Transformers enable parallel training on large datasets."}\n'
            '  ]\n'
            "}"
        )

        
        user_prompt = (
            f"Lesson Title: {lesson['title']}\n"
            f"Lesson Summary: {lesson['summary']}\n\n"
            f"Script:\n{script}\n\n"
            "Extract key concepts, important phrases for captions, and emphasis points."
            "Focus on educational value and clarity. Keywords should be single words or short phrases."
            "Caption phrases should be concise (under 10 words)."
            "For each caption, the 'trigger' must be a short, exact phrase from the script, while the 'text' must be a punchy, summarizing, or paraphrased caption related to the trigger—never just a copy of the trigger."
            "There must always be at least one definition and one key_fact in emphasis_points, even if you must rewrite or infer from the script."
            "Never leave the emphasis_points array empty."
            "Limit to 5-7 keywords, 3-4 captions, and 2-3 emphasis points."
            "When choosing triggers for caption_phrases, always select a short phrase (up to ~8 words) that appears verbatim in the script. Never make up or paraphrase trigger phrases."
            "Do NOT include common stopwords or filler words—such as prepositions, pronouns, conjunctions, and articles. "
            "Avoid capturing stopwords like a, an, the, in, on, was, were, had, has etc - ADD COMMON STOPWORDS TO THE LIST from Prepositions, Pronouns, Conjunctions."
        )

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                max_completion_tokens=3000,
            )
            
            overlay_json = response.choices[0].message.content.strip()
            overlay_data = json.loads(overlay_json)
            overlay_data = fix_or_validate_caption_triggers(overlay_data, script)

            print(f"✅ Extracted {len(overlay_data.get('highlight_keywords', []))} keywords")
            print(f"✅ Extracted {len(overlay_data.get('caption_phrases', []))} caption phrases")
            print(f"✅ Extracted {len(overlay_data.get('emphasis_points', []))} emphasis points")
            
            return overlay_data
            
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse overlay JSON: {e}")
            # Return default structure
            return {
                "highlight_keywords": [],
                "caption_phrases": [],
                "emphasis_points": []
            }
        except Exception as e:
            print(f"⚠️ Error extracting overlay data: {e}")
            return {
                "highlight_keywords": [],
                "caption_phrases": [],
                "emphasis_points": []
            }

    
    def extract_personality(self, character):
        """Extract personality traits from character description"""
        description = character.get('description', '')
        voice_style = character.get('voice_style', '')
        
        # Combine description and voice style
        full_description = f"{description} {voice_style}"
        
        # Extract key personality words
        personality_keywords = ['friendly', 'enthusiastic', 'warm', 'calm', 'energetic', 
                               'passionate', 'gentle', 'cheerful', 'professional', 'caring',
                               'engaging', 'encouraging', 'clear', 'approachable']
        
        found_traits = []
        for keyword in personality_keywords:
            if keyword in full_description.lower():
                found_traits.append(keyword)
        
        if found_traits:
            return f"A {', '.join(found_traits)} educator"
        else:
            return "An engaging and enthusiastic educator"
    
    def validate_emotions(self, script):
        """Check if script has proper emotion tags"""
        import re
        # Check for pattern: Speaker (emotion):
        pattern = r'\w+\s*\([^)]+\):'
        matches = re.findall(pattern, script)
        return len(matches) >= 4  # Should have at least 4 emotion tags
    
    def add_default_emotions(self, script, character_name):
        """Add default emotions if missing"""
        import re
        
        # Common patterns to add emotions to
        replacements = [
            (f'{character_name}:', f'{character_name} (enthusiastic):'),
            ('Narrator:', 'Narrator (informative):'),
        ]
        
        for old, new in replacements:
            # Only replace if emotion not already present
            if f'{old}' in script and '(' not in script.split(old)[0][-10:]:
                script = script.replace(old, new, 1)
        
        return script

@staticmethod
def fix_or_validate_caption_triggers(overlay_data, script, min_ratio=0.6):
    """
    Ensure each caption trigger is a substring of the script. If not, replace it
    with the closest match found in the script using fuzzy matching.
    """
    script_lower = script.lower()
    words = script_lower.split()
    valid_captions = []

    for c in overlay_data.get('caption_phrases', []):
        trigger = c['trigger'].strip().lower()

        if trigger in script_lower:
            valid_captions.append(c)
            continue

        best_match = None
        best_ratio = 0

        trigger_len = len(trigger.split())
        for i in range(len(words) - trigger_len + 1):
            window = ' '.join(words[i:i + trigger_len])
            ratio = difflib.SequenceMatcher(None, trigger, window).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = window

        if best_ratio >= min_ratio and best_match:
            print(f"🔄 Replacing trigger '{trigger}' with closest match in script: '{best_match}' (ratio={best_ratio:.2f})")
            c['trigger'] = best_match
            valid_captions.append(c)
        else:
            print(f"⚠️ WARNING: Could not find suitable match for caption trigger: '{trigger}'. Removing this caption.")

    overlay_data['caption_phrases'] = valid_captions
    return overlay_data