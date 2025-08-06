#!/usr/bin/env python3
"""
test_video_generation.py - Test video generation with existing audio and timing
This allows you to test visual improvements without calling TTS API repeatedly
"""

from agents.visual_agent import VisualAgent
import json
import os

def test_video_with_existing_audio():
    """Test video generation using existing audio and timing files"""
    
    print("🎬 Testing Video Generation with Existing Audio\n")
    
    # Character data for David
    character = {
        "name": "David",
        "gender": "male",
        "description": "A curious and inventive educator who uses interactive experiments and storytelling to illuminate complex topics with simple analogies. They are enthusiastic, warm, and energetic.",
        "voice_style": "clear and engaging",
        "avatar_id": 1
    }
    
    # The script used for generation
    script = """Introduction:
David (enthusiastic): Hey everyone, welcome to our exciting journey into the world of the water cycle! Today, we're going to explore how water moves and transforms all around us in the most incredible natural process.
Narrator (friendly): The water cycle is nature’s way of recycling water, ensuring that our planet stays vibrant and full of life. Let's dive in and see how this fascinating cycle works!

Body:
David (curious): Have you ever wondered how a drop of water can travel from the deepest oceans all the way up into the clouds? It all starts with a process called evaporation!
Narrator (informative): Exactly, David. When the sun heats up water in oceans, lakes, or rivers, it turns into water vapor—a gas that rises into the atmosphere in a process known as evaporation. This step is vital because it transforms liquid water into a form that can travel long distances.
David (enthusiastic): And guess what? Once that water vapor is high in the sky, it cools down, and voilà—condensation occurs! Tiny droplets form clouds, which we enjoy watching as they drift by on a sunny day.
Narrator (thoughtful): That’s right, David. Condensation is when the air can no longer hold all the water vapor, so it clusters together to form clouds. Depending on atmospheric conditions, these clouds eventually release their stored water in the form of precipitation—rain, snow, sleet, or hail.
David (excited): Precipitation is the grand finale of the cycle, where water falls back to Earth and gathers in bodies of water, ready to start the cycle all over again!
Narrator (informative): And don’t forget collection, where water gathers in rivers, lakes, and oceans. This integral step not only replenishes our water sources but also supports life on Earth by nourishing plants, animals, and humans alike.
David (encouraging): The water cycle is truly a wonder of nature—a continuous, unsung hero that sustains all life. Understanding it helps us appreciate the delicate balance of our environment and inspires us to take care of our planet. So, keep exploring, ask questions, and remember, every raindrop has a story waiting to be discovered!"""
    
    # File paths
    lesson_title = "Introduction to the Water Cycle"
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
        
        # Display timing info
        print("\n📋 Timing Information:")
        for i, segment in enumerate(timing_data[:10]):  # Show first 10
            if 'speaker' in segment:
                print(f"  {i+1}. {segment['speaker']} ({segment.get('emotion', 'unknown')}): "
                      f"{segment['start_time']:.2f}s - {segment['end_time']:.2f}s "
                      f"(duration: {segment['duration']:.2f}s)")
    else:
        print(f"⚠️ No timing file found, video will use estimated timing")
    
    # Initialize VisualAgent
    print("\n🎨 Initializing Visual Agent...")
    visual_agent = VisualAgent()
    
    # Prepare input data
    input_data = {
        "character": character,
        "lesson_title": lesson_title,
        "script": script,
        "voice_path": audio_file
    }
    
    # Add timing data if available
    if timing_data:
        input_data["timing"] = timing_data
    
    # Test mode options
    print("\n🔧 Test Options:")
    print("1. Generate full video")
    print("2. Generate test video (first 30 seconds)")
    print("3. Test slide parsing only")
    
    choice = input("Select option (1/2/3): ").strip()
    
    if choice == "3":
        # Test slide parsing only
        print("\n📝 Testing slide parsing...")
        slides = visual_agent.parse_script_to_slides(script, character['name'])
        print(f"\n📑 Parsed {len(slides)} slides:")
        for i, slide in enumerate(slides):
            print(f"  {i+1}. Type: {slide['type']}, "
                  f"Speaker: {slide.get('speaker_name', 'N/A')}, "
                  f"Text length: {len(slide['text'])} chars")
        return
    
    # Generate video
    test_mode = (choice == "2")
    
    try:
        print(f"\n🎬 Generating {'test' if test_mode else 'full'} video...")
        print("This may take a few minutes...")
        
        output_path = visual_agent.run(input_data, test_mode=test_mode)
        
        print(f"\n✅ Video generated successfully!")
        print(f"📹 Output: {output_path}")
        
        # Optional: Open the video
        import platform
        import subprocess
        
        open_video = input("\n📺 Open video now? (y/n): ").strip().lower()
        if open_video == 'y':
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', output_path])
            elif platform.system() == 'Windows':
                subprocess.run(['start', output_path], shell=True)
            else:
                print(f"Please open manually: {output_path}")
                
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
    
    # This function can be expanded to test specific visual elements
    # without regenerating the entire video

if __name__ == "__main__":
    print("🎬 Content Factory - Video Generation Test Suite")
    print("=" * 50)
    
    print("\nThis test uses existing audio files to test video generation")
    print("without calling the TTS API repeatedly.\n")
    
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