from utils.db import init_db
from coordinator import CoordinatorAgent

from agents.curriculum_agent import CurriculumAgent
from agents.character_agent import CharacterAgent
from agents.script_agent import ScriptAgent
from agents.voice_agent import VoiceAgent
from agents.visual_agent import VisualAgent

def main():
    print("🎬 Welcome to Content Factory")
    init_db()

    # Step 1: Get topic from user
    topic = input("Enter your topic: ").strip()
    if not topic:
        print("❌ Topic cannot be empty!")
        return

    coordinator = CoordinatorAgent()
    try:
        curriculum_agent = CurriculumAgent()
        character_agent = CharacterAgent()
        script_agent = ScriptAgent()
        voice_agent = VoiceAgent()
        visual_agent = VisualAgent()
    except Exception as e:
        print(f"❌ Error initializing agents: {e}")
        return

    coordinator.register_agent("curriculum", curriculum_agent)
    coordinator.register_agent("character", character_agent)
    coordinator.register_agent("script", script_agent)
    coordinator.register_agent("voice", voice_agent)
    coordinator.register_agent("visual", visual_agent)

    print("\n📚 Generating curriculum...")
    max_retries = 3
    curriculum = None
    for attempt in range(max_retries):
        try:
            curriculum = coordinator.run_agent("curriculum", topic)
            if curriculum and len(curriculum) > 0:
                break
            else:
                print(f"⚠️  Empty curriculum returned, retrying... ({attempt + 1}/{max_retries})")
        except Exception as e:
            print(f"⚠️  Error generating curriculum: {e}")
            if attempt < max_retries - 1:
                print("Retrying...")

    if not curriculum or len(curriculum) == 0:
        print("❌ Failed to generate curriculum after multiple attempts.")
        return

    # Set number of lessons to process:
    N = int(input("How many lessons to generate? (default 1): ") or "1")
    curriculum = curriculum[:N]

    print("\n📚 Curriculum Generated (All Lessons):")
    for i, lesson in enumerate(curriculum, 1):
        print(f"{i}. {lesson['title']} - {lesson['summary']}")

    char_name = input("\nEnter a character name: ").strip()
    if not char_name:
        char_name = "Zara"
        print(f"Using default character: {char_name}")

    try:
        character = coordinator.run_agent("character", char_name)
        print("\n🎭 Character Info:")
        print(f"Name: {character['name']}")
        print(f"Gender: {character['gender']}")
        print(f"Description: {character['description']}")
        print(f"Voice Style: {character['voice_style']}")
        print(f"Avatar ID: {character['avatar_id']}")
    except Exception as e:
        print(f"❌ Error creating character: {e}")
        return

    try:
        scripts = coordinator.run_agent("script", {
            "character": character,
            "lessons": curriculum
        })
        if not scripts or len(scripts) == 0:
            print("❌ No scripts generated!")
            return

        print("\n📝 Script Previews for All Lessons:")
        for idx, item in enumerate(scripts, 1):
            print(f"\n--- Script for Lesson {idx}: {item['lesson']} ---")
            print(item["script"])

    except Exception as e:
        print(f"❌ Error generating scripts: {e}")
        return

    # Voice for ALL lessons:
    for idx, script_item in enumerate(scripts, 1):
        try:
            print(f"\n🎤 Generating expressive voice for Lesson {idx}: {script_item['lesson']} with SSML and timing synchronization...")
            print(f"🎭 Character personality: {character.get('description', 'engaging educator')[:100]}...")

            voice_result = coordinator.run_agent("voice", {
                "character": character,
                "lesson_title": script_item["lesson"],
                "script": script_item["script"]
            })

            voice_path = voice_result["audio_path"]
            timing_data = voice_result.get("timing", None)

            print(f"🔊 Voice generated: {voice_path}")
            if timing_data:
                print(f"📊 Timing data captured: {len(timing_data)} segments")
            
            script_item["voice_path"] = voice_path
            script_item["timing_data"] = timing_data

        except Exception as e:
            print(f"❌ Error generating voice for Lesson {idx}: {e}")
            continue

    # Video for ALL lessons:
    for idx, script_item in enumerate(scripts, 1):
        try:
            print(f"\n🎬 Generating video for Lesson {idx}: {script_item['lesson']} with synchronized audio (this may take a few minutes)...")

            video_input = {
                "character": character,
                "lesson_title": script_item["lesson"],
                "script": script_item["script"],
                "voice_path": script_item.get("voice_path")
            }

            if script_item.get("timing_data"):
                video_input["timing"] = script_item["timing_data"]
                print("✅ Using synchronized timing for video generation")
            else:
                print("⚠️ No timing data available, using estimated timing")

            video_path = coordinator.run_agent("visual", video_input)
            print(f"\n✅ Success! Video saved at: {video_path}")

        except Exception as e:
            print(f"❌ Error generating video for Lesson {idx}: {e}")
            import traceback
            traceback.print_exc()
            continue

    print("\n🎉 Content generation complete with synchronized audio!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
