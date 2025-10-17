#!/usr/bin/env python3
"""
Enhanced diagnostic script to identify frontend issues
"""

import os
import sys
import urllib.request
import urllib.error
from urllib.parse import urljoin

def test_web_page():
    """Test the main web page and check for errors"""
    print("Testing main web page...")
    try:
        response = urllib.request.urlopen('http://127.0.0.1:5000', timeout=10)
        content = response.read().decode('utf-8')
        
        print(f"[OK] Main page loaded successfully (Status: {response.getcode()})")
        print(f"[INFO] Content length: {len(content)} characters")
        
        # Check if content contains error messages
        if "error" in content.lower() or "exception" in content.lower():
            print("[WARNING] Page content contains error-related text")
            # Extract error portion
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "error" in line.lower() or "exception" in line.lower():
                    print(f"[ERROR] Line {i}: {line.strip()}")
        
        return True, content
        
    except urllib.error.URLError as e:
        print(f"[ERROR] Cannot connect to Flask app: {e}")
        return False, None
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False, None

def test_static_files():
    """Test if static files are accessible"""
    print("\nTesting static file serving...")
    
    static_files = [
        'sentiment_distribution.png',
        'wordcloud_overall.png',
        'wordcloud_positive.png',
        'confusion_matrix.png'
    ]
    
    base_url = 'http://127.0.0.1:5000/static/plots/'
    
    for filename in static_files:
        try:
            url = urljoin(base_url, filename)
            response = urllib.request.urlopen(url, timeout=5)
            print(f"[OK] {filename} - Status: {response.getcode()}")
        except urllib.error.HTTPError as e:
            print(f"[ERROR] {filename} - HTTP Error: {e.code}")
        except urllib.error.URLError as e:
            print(f"[ERROR] {filename} - URL Error: {e}")
        except Exception as e:
            print(f"[ERROR] {filename} - Unexpected error: {e}")

def check_plot_files():
    """Check if plot files exist and are valid"""
    print("\nChecking plot files...")
    
    plots_dir = "plots"
    static_plots_dir = "static/plots"
    
    if not os.path.exists(plots_dir):
        print(f"[ERROR] {plots_dir} directory does not exist")
        return False
    
    if not os.path.exists(static_plots_dir):
        print(f"[ERROR] {static_plots_dir} directory does not exist")
        return False
    
    plots_files = [f for f in os.listdir(plots_dir) if f.endswith('.png')]
    static_files = [f for f in os.listdir(static_plots_dir) if f.endswith('.png')]
    
    print(f"[INFO] Found {len(plots_files)} PNG files in {plots_dir}")
    print(f"[INFO] Found {len(static_files)} PNG files in {static_plots_dir}")
    
    # Check for missing files
    missing_in_static = set(plots_files) - set(static_files)
    if missing_in_static:
        print(f"[WARNING] Files missing in static directory: {missing_in_static}")
    
    # Check file sizes
    for filename in plots_files[:5]:  # Check first 5 files
        filepath = os.path.join(plots_dir, filename)
        size = os.path.getsize(filepath)
        print(f"[INFO] {filename}: {size} bytes")
        if size == 0:
            print(f"[ERROR] {filename} is empty!")
    
    return True

def check_flask_logs():
    """Check if Flask app is running and show recent logs"""
    print("\nChecking Flask app status...")
    
    try:
        # Try to get the main page
        response = urllib.request.urlopen('http://127.0.0.1:5000', timeout=5)
        print("[OK] Flask app is responding")
        return True
    except urllib.error.URLError as e:
        print(f"[ERROR] Flask app not responding: {e}")
        print("[INFO] Make sure to run: python app.py")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("ENHANCED FRONTEND DIAGNOSTIC")
    print("=" * 60)
    
    # Check Flask app
    flask_ok = check_flask_logs()
    
    if flask_ok:
        # Test main page
        page_ok, content = test_web_page()
        
        # Test static files
        test_static_files()
        
        # Check plot files
        check_plot_files()
        
        print("\n" + "=" * 60)
        if page_ok:
            print("[SUCCESS] Frontend appears to be working!")
            print("[INFO] Open http://127.0.0.1:5000 in your browser")
            print("[INFO] If you see errors in the browser, check the browser console (F12)")
        else:
            print("[ERROR] Frontend has issues. Check the errors above.")
    else:
        print("[ERROR] Flask app is not running. Start it with: python app.py")
    
    print("=" * 60)

