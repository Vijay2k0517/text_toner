#!/usr/bin/env python3
"""
Simple test script to verify the tone analysis API
"""
import requests
import json
import time

# API endpoint
BASE_URL = "http://localhost:8000"
ANALYZE_ENDPOINT = f"{BASE_URL}/api/v1/tone/analyze-tone"

def test_tone_analysis():
    """Test the tone analysis endpoint"""
    print("Testing Tone Analysis API...")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "text": "I'm so excited about this project!",
            "target_tone": None,
            "expected_tone": "positive"
        },
        {
            "text": "This is terrible and I hate it.",
            "target_tone": None,
            "expected_tone": "negative"
        },
        {
            "text": "The meeting is scheduled for 3 PM.",
            "target_tone": None,
            "expected_tone": "neutral"
        },
        {
            "text": "Hey, can you help me with this?",
            "target_tone": "professional",
            "expected_tone": "neutral"
        },
        {
            "text": "I need this done ASAP!",
            "target_tone": "friendly",
            "expected_tone": "negative"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input: {test_case['text']}")
        print(f"Target Tone: {test_case['target_tone'] or 'None'}")
        
        try:
            # Prepare request
            payload = {
                "text": test_case["text"]
            }
            if test_case["target_tone"]:
                payload["target_tone"] = test_case["target_tone"]
            
            # Make request
            start_time = time.time()
            response = requests.post(
                ANALYZE_ENDPOINT,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success ({end_time - start_time:.2f}s)")
                print(f"Detected Tone: {result['detected_tone']}")
                print(f"Original Text: {result['original_text']}")
                print(f"Improved Text: {result['improvised_text']}")
                
                # Check if detected tone matches expected
                if result['detected_tone'] == test_case['expected_tone']:
                    print("✅ Tone detection correct")
                else:
                    print(f"⚠️  Expected {test_case['expected_tone']}, got {result['detected_tone']}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        print("-" * 30)

def test_health_check():
    """Test the health check endpoint"""
    print("\nTesting Health Check...")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Health check passed")
            print(f"Status: {result['status']}")
            print(f"Database Connected: {result['database_connected']}")
            print(f"Model Loaded: {result['model_loaded']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_supported_tones():
    """Test the supported tones endpoint"""
    print("\nTesting Supported Tones...")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/tone/supported-tones", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Supported tones retrieved")
            print(f"Supported Tones: {result['supported_tones']}")
            print(f"Target Tones: {result['target_tones']}")
        else:
            print(f"❌ Failed to get supported tones: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting supported tones: {e}")

if __name__ == "__main__":
    print("Text Toner API Test Suite")
    print("=" * 50)
    
    # Test health check first
    test_health_check()
    
    # Test supported tones
    test_supported_tones()
    
    # Test tone analysis
    test_tone_analysis()
    
    print("\n" + "=" * 50)
    print("Test suite completed!")
