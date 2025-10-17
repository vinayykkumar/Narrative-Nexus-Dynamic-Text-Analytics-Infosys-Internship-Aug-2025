#!/usr/bin/env python3
"""
Test script to verify Gemini API integration
"""

import os

GEMINI_API_KEY = "AIzaSyAbFTcNf6-Xq64tma7ZV7V2EE59ZIQTm9Q"

def test_gemini():
    try:
        from google import genai
        from google.genai import types
        
        print("✓ Google GenAI library imported successfully")
        
        client = genai.Client(api_key=GEMINI_API_KEY)
        print("✓ Client created successfully")
        
        # Test with simple text
        test_text = """
        You are analyzing student feedback. Create a professional summary.
        
        Sample feedback: "good teacher very good he is good sir is good he is ok her teaching is very good for us good he is a good teacher"
        """
        
        contents = [
            types.Content(
                role="user",
                parts=[types.Part(text=test_text)]
            )
        ]
        
        config = types.GenerateContentConfig(
            response_mime_type="text/plain",
            temperature=0.7,
            max_output_tokens=512
        )
        
        print("🔄 Making API call...")
        
        # Try different model names
        models_to_try = ["models/gemini-1.5-flash", "models/gemini-pro", "gemini-1.5-flash", "gemini-pro"]
        
        result = None
        for model_name in models_to_try:
            try:
                print(f"Trying model: {model_name}")
                result = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config
                )
                print(f"✓ Success with model: {model_name}")
                break
            except Exception as model_error:
                print(f"Failed with {model_name}: {model_error}")
                continue
        
        if result:
            print("✓ API call successful!")
            print(f"📝 Response: {result.text[:200]}...")
            return True
        else:
            print("❌ All models failed")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini()
    if success:
        print("\n🎉 Gemini integration working correctly!")
    else:
        print("\n💔 Gemini integration failed")