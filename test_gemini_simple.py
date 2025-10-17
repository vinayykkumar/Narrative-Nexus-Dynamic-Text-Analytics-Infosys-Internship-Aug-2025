#!/usr/bin/env python3
"""
Simple test script for standard Google GenerativeAI
"""

import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyAbFTcNf6-Xq64tma7ZV7V2EE59ZIQTm9Q"

def test_simple_gemini():
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("✓ API key configured")
        
        # Try different model names
        models_to_try = ['gemini-1.5-flash-latest', 'gemini-1.5-pro', 'gemini-pro', 'gemini-1.0-pro']
        
        model = None
        for model_name in models_to_try:
            try:
                print(f"Trying model: {model_name}")
                model = genai.GenerativeModel(model_name)
                print(f"✓ Model created: {model_name}")
                break
            except Exception as e:
                print(f"Failed with {model_name}: {e}")
                continue
                
        if not model:
            raise Exception("No working model found")
        
        test_prompt = """
        You are an expert educational analyst. Analyze this student feedback and create a professional summary:
        
        "good teacher very good he is good sir is good he is ok her teaching is very good for us good he is a good teacher good teacher good teacher"
        
        Please provide a meaningful, non-repetitive analysis of teaching quality.
        """
        
        print("🔄 Generating content...")
        response = model.generate_content(test_prompt)
        
        print("✓ Content generated successfully!")
        print(f"📝 Response: {response.text[:300]}...")
        
        return response.text
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    result = test_simple_gemini()
    if result:
        print(f"\n🎉 Full response:\n{result}")
    else:
        print("\n💔 Test failed")