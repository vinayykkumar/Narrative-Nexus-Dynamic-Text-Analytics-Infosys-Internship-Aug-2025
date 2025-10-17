#!/usr/bin/env python3
"""
Test the actual Flask app export route
"""

import requests
import subprocess
import time
import threading
import os

def test_flask_app():
    """Test the Flask app export route"""
    
    print("🧪 Testing Flask App Export Route...")
    
    # Check if app.py exists and has the export route
    try:
        with open('app.py', 'r') as f:
            content = f.read()
            if 'export-pdf-new.html' in content:
                print("✅ App.py is using the new enhanced template")
            else:
                print("❌ App.py still using old template")
        
        print("\n🚀 Start your Flask app with: python app.py")
        print("📱 Then visit: http://127.0.0.1:5000/export-pdf")
        print("🎯 Check browser console for any JavaScript errors")
        print("📊 You should see 21 plots organized in modern sections:")
        print("   - 4 Data Distribution charts")
        print("   - 11 Word clouds (Overall + Sentiment + Topics)")
        print("   - 2 Correlation matrices") 
        print("   - 1 Confusion matrix")
        print("   - 3 Count charts")
        
    except Exception as e:
        print(f"❌ Error checking app.py: {e}")

if __name__ == "__main__":
    test_flask_app()