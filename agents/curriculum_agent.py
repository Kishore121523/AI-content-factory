from agents.base_agent import Agent
import openai
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

class CurriculumAgent(Agent):
    def __init__(self):
        super().__init__("CurriculumAgent")
        self.client = openai.AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_LLM_KEY"),
            api_version=os.getenv("AZURE_OPENAI_LLM_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_LLM_ENDPOINT"),
        )
        self.deployment = os.getenv("AZURE_OPENAI_LLM_DEPLOYMENT_NAME")

    
    def run(self, topic):
        system_prompt = (
            "You are an expert educator creating short educational videos. "
            "Given a topic, break it into 3–5 concise lessons. Each lesson should have a title and a 1-sentence summary. "
            "Respond ONLY with valid JSON array, no other text. Format: [{\"title\": \"...\", \"summary\": \"...\"}, ...]"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Topic: {topic}"}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                max_completion_tokens=3000,
            
            )

            raw = response.choices[0].message.content.strip()
            
            # Try to parse as JSON first
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                # Try to fix common JSON issues
                fixed = self.fix_json(raw)
                return json.loads(fixed)
                
        except Exception as e:
            print(f"⚠️ Error generating curriculum: {e}")
            # Return default curriculum as fallback
            return self.get_default_curriculum(topic)

    def fix_json(self, raw_json):
        """Attempt to fix common JSON formatting issues"""
        # Remove any text before the first [
        match = re.search(r'\[', raw_json)
        if match:
            raw_json = raw_json[match.start():]
        
        # Handle incomplete JSON by closing it properly
        if raw_json.count('[') > raw_json.count(']'):
            # Find the last complete object
            last_complete = raw_json.rfind('}')
            if last_complete != -1:
                # Check if we need a comma before closing
                if raw_json[last_complete+1:].strip() and raw_json[last_complete+1:].strip()[0] == ',':
                    raw_json = raw_json[:last_complete+1] + ']'
                else:
                    raw_json = raw_json[:last_complete+1] + ']'
        
        # Fix unclosed strings by finding the last complete quote pair
        if raw_json.count('"') % 2 != 0:
            # Find position of last complete key-value pair
            last_good_pos = max(
                raw_json.rfind('"},'),
                raw_json.rfind('"}')
            )
            if last_good_pos > 0:
                raw_json = raw_json[:last_good_pos+2] + ']'
        
        # Remove any trailing commas before closing brackets
        raw_json = re.sub(r',\s*]', ']', raw_json)
        raw_json = re.sub(r',\s*}', '}', raw_json)
        
        return raw_json

    def get_default_curriculum(self, topic):
        """Return a default curriculum structure when parsing fails"""
        return [
            {
                "title": f"Introduction to {topic}",
                "summary": f"Learn the fundamental concepts and importance of {topic}."
            },
            {
                "title": f"Key Components of {topic}",
                "summary": f"Explore the main elements and how they work together in {topic}."
            },
            {
                "title": f"Real-World Applications",
                "summary": f"Discover how {topic} impacts our daily lives and the environment."
            }
        ]