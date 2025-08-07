"""
Debug and test different voice styles
"""

import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv

load_dotenv()

def test_voice_styles():
    """Test different voice styles with Azure TTS"""
    
    print("🎭 Azure TTS Voice Style Tester\n")
    
    # Setup
    speech_key = os.getenv("AZURE_OPENAI_TTS_KEY")
    speech_region = os.getenv("AZURE_OPENAI_TTS_REGION")
    
    if not speech_key or not speech_region:
        print("❌ Missing Azure TTS credentials in .env")
        return
    
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key,
        region=speech_region
    )
    
    # Test configurations
    test_cases = [
        {
            "voice": "en-US-AvaMultilingualNeural",
            "style": "cheerful",
            "text": "Hello! I'm so excited to learn with you today!",
            "description": "Cheerful greeting"
        },
        {
            "voice": "en-US-AvaMultilingualNeural",
            "style": "excited",
            "text": "Wow! Did you know that water can exist in three different states?",
            "description": "Excited discovery"
        },
        {
            "voice": "en-US-JennyMultilingualNeural",
            "style": "documentary-narration",
            "text": "The water cycle is a continuous process that has shaped our planet for billions of years.",
            "description": "Documentary narration"
        },
        {
            "voice": "en-US-GuyNeural",
            "style": "friendly",
            "text": "Let me explain this in a simple way that makes sense.",
            "description": "Friendly explanation"
        },
        {
            "voice": "en-US-AvaMultilingualNeural",
            "style": "encouraging",
            "text": "You're doing great! Keep exploring and asking questions!",
            "description": "Encouraging feedback"
        }
    ]
    
    print("📋 Available test cases:")
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. {case['description']} - {case['voice']} ({case['style']})")
    
    print("\n🎤 Generating samples...")
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['description']}:")
        print(f"   Voice: {test['voice']}")
        print(f"   Style: {test['style']}")
        print(f"   Text: {test['text']}")
        
        # Create SSML
        ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
                   xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
            <voice name="{test['voice']}">
                <mstts:express-as style="{test['style']}">
                    {test['text']}
                </mstts:express-as>
            </voice>
        </speak>"""
        
        # Generate audio
        output_file = f"output/style_test_{i}_{test['style']}.mp3"
        
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )
        
        result = synthesizer.speak_ssml_async(ssml).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"   ✅ Saved to: {output_file}")
        else:
            print(f"   ❌ Failed: {result.reason}")
            if result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                print(f"   Error: {cancellation.error_details}")
    
    print("\n✅ All style tests complete! Check the output folder for MP3 files.")
    print("\n💡 Tips:")
    print("- Not all styles work with all voices")
    print("- AvaMultilingualNeural and JennyMultilingualNeural have the most style support")
    print("- GuyNeural has limited style support")
    print("- Use 'assistant' or 'friendly' as safe defaults")

def list_available_voices():
    """List all available voices and their supported styles"""
    
    print("\n📚 Common Educational Voices and Supported Styles:\n")
    
    voices_info = {
        "en-US-AvaMultilingualNeural": {
            "gender": "Female",
            "styles": ["cheerful", "excited", "friendly", "hopeful", "sad", "angry", "terrified", "shouting", "unfriendly", "whispering"]
        },
        "en-US-JennyMultilingualNeural": {
            "gender": "Female", 
            "styles": ["assistant", "chat", "customerservice", "newscast", "angry", "cheerful", "sad", "excited", "friendly", "terrified", "shouting", "unfriendly", "whispering", "hopeful"]
        },
        "en-US-GuyNeural": {
            "gender": "Male",
            "styles": ["newscast", "angry", "cheerful", "sad", "excited", "friendly", "terrified", "shouting", "unfriendly", "whispering", "hopeful"]
        },
        "en-US-AriaNeural": {
            "gender": "Female",
            "styles": ["chat", "customerservice", "narration-professional", "newscast-casual", "newscast-formal", "cheerful", "empathetic", "angry", "sad", "excited", "friendly", "terrified", "shouting", "unfriendly", "whispering", "hopeful"]
        },
        "en-US-DavisNeural": {
            "gender": "Male",
            "styles": ["chat", "angry", "cheerful", "excited", "friendly", "hopeful", "sad", "shouting", "terrified", "unfriendly", "whispering"]
        }
    }
    
    for voice, info in voices_info.items():
        print(f"🎤 {voice} ({info['gender']})")
        print(f"   Styles: {', '.join(info['styles'])}")
        print()

if __name__ == "__main__":
    print("🔊 Azure TTS Style Testing Tool\n")
    
    choice = input("Choose option:\n1. Test voice styles\n2. List available voices\n\nEnter choice (1/2): ").strip()
    
    if choice == "1":
        test_voice_styles()
    elif choice == "2":
        list_available_voices()
    else:
        print("Invalid choice")