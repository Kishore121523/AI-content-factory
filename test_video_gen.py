#!/usr/bin/env python3
"""
test_video_generation.py - Test video generation with existing audio and overlays
This allows you to test visual improvements without calling TTS or LLM API repeatedly.
"""

from agents.visual_agent import VisualAgent
import json
import os

def test_video_with_existing_audio():
    """Test video generation using existing audio, timing, and pre-extracted overlays"""

    print("🎬 Testing Video Generation with Existing Audio & Overlays\n")

    # Character data for David
    character = {
        "name": "David",
        "gender": "male",
        "description": (
            "A curious and inventive educator who uses interactive experiments and storytelling to illuminate complex topics with simple analogies. "
            "They are enthusiastic, warm, and energetic."
        ),
        "voice_style": "clear and engaging",
        "avatar_id": 1
    }

    # Script and lesson info for Agentic RAG
    script = """Introduction:
David (enthusiastic): Hey everyone! Welcome to our deep dive on Retrieval-Augmented Generation. Get ready to uncover how combining data retrieval with text generation sparks new possibilities!
Narrator (friendly): Today, we explore RAG – a framework that enriches language models by uniting precise data lookup with creative language output.

Body:
David (curious): Have you ever wondered how language models become supercharged by integrating retrieval of real-world data with on-the-fly text generation?
Narrator (informative): Retrieval-Augmented Generation, or RAG, unites document retrieval and natural language generation to build more knowledgeable, context-aware responses.
David (enthusiastic): Imagine a system that fetches key information from huge databases and then crafts thoughtful, engaging answers – like having an expert right there with you!
Narrator (thoughtful): This approach transforms models into dynamic research partners, blending precise facts with articulate storytelling.
David (curious): What makes RAG truly special is its dual power to search for accurate data and instantly weave it into coherent narratives.
Narrator (informative): By retrieving data first and then generating text, RAG bridges the gap between static information and dynamic conversation, enhancing both correctness and creativity.
David (excited): Check this out: using RAG can boost tasks like question answering, summarization, and content creation by delivering rich, precise, and engaging responses!
Narrator (thoughtful): RAG smartly balances factual information with creative output, ensuring every answer is both informative and captivating.
David (cheerful): Isn’t that amazing? It’s like pairing a data detective with a creative writer – the best of both worlds in one innovative model!
David (curious): But how do we handle massive data? Doesn’t RAG need huge computing power to scan all those documents?
Narrator (reassuring): Great question! RAG uses efficient indexing and advanced search algorithms to quickly narrow down the most relevant documents, saving time and resources.
David (enthusiastic): This means even with vast data volumes, the system remains both practical and powerful – a real game changer for modern AI!
Narrator (informative): Exactly. It organizes retrieval and generation steps smartly, ensuring precision and speed are maintained at every stage.

Summary/Call to Action:
David (encouraging): Today, we unlocked the basics of RAG. Dive deeper, experiment with these ideas, and start transforming your projects with this powerful, innovative framework!
"""

    lesson_title = "Introduction_to_Retrieval-Augmented_Generation_(RAG)"
    audio_file = f"output/David_{lesson_title.replace(' ', '_')}.mp3"
    timing_file = f"output/David_{lesson_title.replace(' ', '_')}_timing.json"

    # Check if files exist
    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        print("Please ensure you have the audio file from previous generation")
        return

    # Load timing data if it exists
    timing_data = None
    if os.path.exists(timing_file):
        print(f"✅ Found timing file: {timing_file}")
        with open(timing_file, 'r') as f:
            timing_data = json.load(f)
        print(f"📊 Loaded {len(timing_data)} timing segments")
        print("\n📋 Timing Information:")
        for i, segment in enumerate(timing_data[:10]):  # Show first 10
            if 'speaker' in segment:
                print(f"  {i+1}. {segment['speaker']} ({segment.get('emotion', 'unknown')}): "
                      f"{segment['start_time']:.2f}s - {segment['end_time']:.2f}s "
                      f"(duration: {segment['duration']:.2f}s)")
    else:
        print(f"⚠️ No timing file found, video will use estimated timing")

    # --------
    # 🟡 SET OVERLAY DATA HERE
    overlay_data = {
        "highlight_keywords": [
            "RAG",
            "retrieval",
            "generation",
            "language models",
            "indexing",
            "algorithms",
        ],
        "caption_phrases": [
            {"trigger": "document retrieval and natural language generation", "text": "Merging search with smart writing"},
            {"trigger": "efficient indexing", "text": "Fast, smart data lookup"},
            {"trigger": "real game changer", "text": "A breakthrough in AI performance"},
        ],
        "emphasis_points": [
            {
                "type": "definition",
                "text": "RAG: Combines retrieval with generation for context-aware output."
            },
            {
                "type": "key_fact",
                "text": "Enhances factual accuracy while fueling creative responses."
            }
        ]
    }
    # --------

    # Overlay Data Preview (colored preview in terminal)
    print("\n🟡 Overlay Data Preview:")
    print(f"  🎯 Highlight keywords ({len(overlay_data['highlight_keywords'])}): " +
          ', '.join(overlay_data['highlight_keywords']))
    print(f"  💬 Captions ({len(overlay_data['caption_phrases'])}):")
    for idx, cap in enumerate(overlay_data['caption_phrases'], 1):
        print(f"    {idx}. \"{cap['text']}\" (trigger: \"{cap['trigger']}\")")
    print(f"  📌 Emphasis points ({len(overlay_data.get('emphasis_points', []))}):")
    for idx, ep in enumerate(overlay_data.get('emphasis_points', []), 1):
        typ = ep.get('type', '')
        print(f"    {idx}. [{typ}] {ep.get('text', '')}")

    # Initialize VisualAgent
    print("\n🎨 Initializing Visual Agent...")
    visual_agent = VisualAgent()

    # Prepare input data (pass overlay_data)
    input_data = {
        "character": character,
        "lesson_title": lesson_title,
        "script": script,
        "voice_path": audio_file,
        "overlay_data": overlay_data,
    }
    if timing_data:
        input_data["timing"] = timing_data

    # Test mode options
    print("\n🔧 Test Options:")
    print("1. Generate full video")
    print("2. Generate test video (first 30 seconds)")
    print("3. Test slide parsing only")

    choice = input("Select option (1/2/3): ").strip()

    if choice == "3":
        print("\n📝 Testing slide parsing...")
        slides = visual_agent.parse_script_to_slides(script, character['name'])
        print(f"\n📑 Parsed {len(slides)} slides:")
        for i, slide in enumerate(slides):
            print(f"  {i+1}. Type: {slide['type']}, "
                  f"Speaker: {slide.get('speaker_name', 'N/A')}, "
                  f"Text length: {len(slide['text'])} chars")
        return

    test_mode = (choice == "2")

    try:
        print(f"\n🎬 Generating {'test' if test_mode else 'full'} video...")
        print("This may take a few minutes...")

        output_path = visual_agent.run(input_data, test_mode=test_mode)

        print(f"\n✅ Video generated successfully!")
        print(f"📹 Output: {output_path}")

    except Exception as e:
        print(f"\n❌ Error generating video: {e}")
        import traceback
        traceback.print_exc()

def test_visual_improvements():
    """Test specific visual improvements"""
    print("\n🎨 Visual Improvement Test Options:\n")
    print("1. Test different color schemes")
    print("2. Test bubble styles")
    print("3. Test text sizing and positioning")
    print("4. Test transition timing")

if __name__ == "__main__":
    print("🎬 Content Factory - Video Generation Test Suite")
    print("=" * 50)

    print("\nThis test uses existing audio files to test video generation")
    print("without calling the TTS API or LLM pipeline repeatedly.\n")

    print("Test Options:")
    print("1. Test video generation with existing audio")
    print("2. Test visual improvements (coming soon)")

    choice = input("\nSelect test (1/2): ").strip()

    if choice == "1":
        test_video_with_existing_audio()
    elif choice == "2":
        print("\n⚠️ Visual improvement tests coming soon...")
        print("For now, use option 1 and modify visual_agent.py directly")
    else:
        print("Invalid choice")

    print("\n✅ Test complete!")
