from agents.base_agent import Agent
from utils.db import get_connection
import openai
import os
import random
from dotenv import load_dotenv
import json

load_dotenv()

class CharacterAgent(Agent):
    def __init__(self):
        super().__init__("CharacterAgent")
        self.client = openai.AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_LLM_KEY"),
            api_version=os.getenv("AZURE_OPENAI_LLM_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_LLM_ENDPOINT"),
        )
        self.deployment = os.getenv("AZURE_OPENAI_LLM_DEPLOYMENT_NAME")
        
        # Avatar configuration
        self.avatar_count = 3  # 3 avatars per gender

    def run(self, name):
        # Step 1: Check if character exists
        character = self.fetch_character(name)
        if character:
            print(f"✅ Found existing character: {name}")
            return character

        # Step 2: Generate new character using o3-mini
        print(f"🎭 Creating new character: {name}")
        system_prompt = (
            "You are a creative assistant. Given a name, generate a unique educational video character. "
            "The character should be engaging and suitable for educational content. "
            "Include personality traits that will affect their speaking style. "
            "Return ONLY valid JSON in this exact format: "
            '{"name": "...", "gender": "male/female", '
            '"description": "A [personality traits] educator who [unique characteristics]. '
            'They are [emotional qualities like: enthusiastic, warm, friendly, calm, energetic, passionate, gentle, cheerful].", '
            '"voice_style": "[speaking characteristics like: clear and engaging, warm and encouraging, '
            'enthusiastic and energetic, calm and reassuring, friendly and approachable]"}'
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create an educational character named {name}. Make them interesting and engaging for learners."}
        ]

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
        )

        raw = response.choices[0].message.content.strip()
        try:
            character_data = json.loads(raw)
            
            # Ensure gender is included
            if 'gender' not in character_data:
                character_data['gender'] = 'female'
            
            # Ensure all required fields are present
            character_data['name'] = name  # Use the provided name
            
            # Assign a random avatar based on gender
            character_data['avatar_id'] = self.assign_random_avatar(character_data['gender'])
            
            self.save_character(character_data)
            return character_data
            
        except Exception as e:
            print("⚠️ Failed to parse character:", e)
            print("Raw response:", raw)
            
            # Fallback character creation with rich personality
            fallback_character = {
                'name': name,
                'gender': 'female',
                'description': f'A friendly and enthusiastic educator named {name} who loves making complex topics simple and engaging. They are warm, encouraging, and passionate about teaching.',
                'voice_style': 'clear, warm, and engaging with an enthusiastic and encouraging tone',
                'avatar_id': self.assign_random_avatar('female')
            }
            self.save_character(fallback_character)
            return fallback_character

    def assign_random_avatar(self, gender: str) -> int:
        """Assign a random avatar ID based on gender"""
        # Avatar IDs: 1-3 for each gender
        avatar_id = random.randint(1, self.avatar_count)
        print(f"🎨 Assigned avatar_{avatar_id}.png for {gender} character")
        return avatar_id

    def fetch_character(self, name):
        conn = get_connection()
        cursor = conn.cursor()
        
        # Try to fetch with avatar_id column
        try:
            cursor.execute("SELECT name, gender, description, voice_style, avatar_id FROM characters WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                return {
                    "name": row[0], 
                    "gender": row[1] or 'female',
                    "description": row[2], 
                    "voice_style": row[3],
                    "avatar_id": row[4] or 1
                }
        finally:
            conn.close()
        
        return None

    def save_character(self, character):
        conn = get_connection()
        cursor = conn.cursor()
        
        # Ensure gender and avatar_id have default values
        gender = character.get('gender', 'female')
        avatar_id = character.get('avatar_id', 1)
        
        cursor.execute(
            "INSERT INTO characters (name, gender, description, voice_style, avatar_id) VALUES (?, ?, ?, ?, ?)",
            (character['name'], gender, character['description'], character['voice_style'], avatar_id)
        )
        
        conn.commit()
        conn.close()
        print(f"💾 Character saved: {character['name']} with avatar_{avatar_id}.png")