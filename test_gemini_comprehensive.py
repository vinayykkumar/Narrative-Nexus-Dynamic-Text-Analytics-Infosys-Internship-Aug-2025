#!/usr/bin/env python3
"""
Comprehensive test for Gemini API to find working configuration
"""

import google.generativeai as genai
import time

GEMINI_API_KEY = "AIzaSyAbFTcNf6-Xq64tma7ZV7V2EE59ZIQTm9Q"

def test_model_availability():
    """Test which models are actually available"""
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("✓ API key configured")
        
        print("🔍 Checking available models...")
        models = genai.list_models()
        
        available_models = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                available_models.append(model.name)
                print(f"  ✓ {model.name} - supports content generation")
        
        return available_models
        
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return []

def test_with_available_model(model_name):
    """Test generation with a specific model"""
    try:
        model = genai.GenerativeModel(model_name)
        print(f"✓ Model {model_name} created")
        
        test_prompt = """
        You are analyzing student feedback. Create a professional summary of this data:
        
        Sample feedback: "good teacher very good he is good sir teaching is good overall nice personality"
        
        Provide a meaningful analysis of teaching effectiveness.
        """
        
        print(f"🔄 Generating content with {model_name}...")
        response = model.generate_content(test_prompt)
        
        print(f"✓ Success! Generated content:")
        print(f"📝 Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Failed with {model_name}: {e}")
        return False

def main():
    print("🚀 Starting comprehensive Gemini API test...\n")
    
    # Step 1: Check available models
    available_models = test_model_availability()
    
    if not available_models:
        print("\n💔 No available models found. Trying common model names...")
        # Try common model names directly
        common_models = [
            'models/gemini-pro',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro',
            'gemini-pro',
            'gemini-1.5-flash',
            'gemini-1.5-pro'
        ]
        
        for model_name in common_models:
            print(f"\n🧪 Testing {model_name}...")
            if test_with_available_model(model_name):
                print(f"🎉 SUCCESS! Working model found: {model_name}")
                return model_name
        
        print("\n💔 No working models found")
        return None
    
    else:
        print(f"\n🎯 Found {len(available_models)} available models")
        
        # Test the first available model
        for model_name in available_models[:3]:  # Test first 3
            print(f"\n🧪 Testing available model: {model_name}")
            if test_with_available_model(model_name):
                print(f"🎉 SUCCESS! Working model: {model_name}")
                return model_name
        
        print("\n💔 Available models didn't work")
        return None

if __name__ == "__main__":
    working_model = main()
    
    if working_model:
        print(f"\n✅ RESULT: Use model '{working_model}' in your application!")
    else:
        print(f"\n❌ RESULT: No working Gemini models found. Check API key or try different approach.")
        print("Consider using alternative text analysis or check Google AI Studio for model availability.")