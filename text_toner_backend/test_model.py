#!/usr/bin/env python3
"""
Simple test script to check if the tone analyzer can load and work
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.tone_analyzer import tone_analyzer

async def test_tone_analyzer():
    """Test the tone analyzer functionality"""
    print("Testing Tone Analyzer...")
    
    try:
        # Test with a simple text
        test_text = "I am so disappointed with this service. It never works properly."
        print(f"Testing with text: {test_text}")
        
        # Analyze the tone
        result = await tone_analyzer.analyze_tone(test_text)
        print(f"Result: {result}")
        
        # Test with another text
        test_text2 = "This is absolutely terrible! I hate this stupid thing!"
        print(f"\nTesting with text: {test_text2}")
        result2 = await tone_analyzer.analyze_tone(test_text2)
        print(f"Result: {result2}")
        
        # Test with friendly text
        test_text3 = "Hello there! I hope you're having a wonderful day!"
        print(f"\nTesting with text: {test_text3}")
        result3 = await tone_analyzer.analyze_tone(test_text3)
        print(f"Result: {result3}")
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tone_analyzer())
