# agents/script_agent.py

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
            all_scripts.append({
                "lesson": lesson["title"],
                "script": script
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