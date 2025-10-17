#!/usr/bin/env python3
"""
Simple test script to verify the Flask app is working correctly
"""

import os
import sys
import time
import subprocess
import threading
from urllib.request import urlopen
from urllib.error import URLError

def test_flask_app():
    """Test if the Flask app starts and serves content correctly"""
    print("Testing Flask app...")
    
    # Start the Flask app in a subprocess
    try:
        process = subprocess.Popen([
            sys.executable, "app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a bit for the app to start
        time.sleep(3)
        
        # Test if the app is responding
        try:
            response = urlopen("http://localhost:5000", timeout=5)
            print(f"[OK] Flask app is running! Status: {response.getcode()}")
            print("[OK] Frontend should be accessible at http://localhost:5000")
            return True
        except URLError as e:
            print(f"[ERROR] Flask app not responding: {e}")
            return False
        finally:
            # Clean up the process
            process.terminate()
            process.wait()
            
    except Exception as e:
        print(f"[ERROR] Error starting Flask app: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        'flask', 'pandas', 'matplotlib', 'seaborn', 
        'nltk', 'sklearn', 'wordcloud', 'sumy'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"[OK] {package}")
        except ImportError:
            print(f"[MISSING] {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n[MISSING] Missing packages: {', '.join(missing)}")
        print("Install them with: pip install " + " ".join(missing))
        return False
    else:
        print("[OK] All dependencies are installed!")
        return True

def check_files():
    """Check if all required files exist"""
    print("Checking required files...")
    
    required_files = [
        'app.py', 'main.py', 'templates/index.html', 
        'merged_student_feedback.csv', 'opportunity.tsv'
    ]
    
    missing = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"[OK] {file_path}")
        else:
            print(f"[MISSING] {file_path} - MISSING")
            missing.append(file_path)
    
    if missing:
        print(f"\n[MISSING] Missing files: {', '.join(missing)}")
        return False
    else:
        print("[OK] All required files exist!")
        return True

if __name__ == "__main__":
    print("=" * 50)
    print("FRONTEND DIAGNOSTIC TEST")
    print("=" * 50)
    
    # Check files
    files_ok = check_files()
    print()
    
    # Check dependencies
    deps_ok = check_dependencies()
    print()
    
    # Test Flask app
    if files_ok and deps_ok:
        app_ok = test_flask_app()
    else:
        print("[ERROR] Skipping Flask test due to missing files/dependencies")
        app_ok = False
    
    print("\n" + "=" * 50)
    if files_ok and deps_ok and app_ok:
        print("[SUCCESS] ALL TESTS PASSED! Your frontend should be working.")
        print("[INFO] Open http://localhost:5000 in your browser")
    else:
        print("[ERROR] SOME TESTS FAILED. Please fix the issues above.")
    print("=" * 50)
