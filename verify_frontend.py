#!/usr/bin/env python3
"""
Final verification script to test the frontend
"""

import urllib.request
import json

def test_frontend():
    print("=" * 60)
    print("FINAL FRONTEND VERIFICATION")
    print("=" * 60)
    
    try:
        # Test main page
        print("[TEST] Loading main page...")
        response = urllib.request.urlopen('http://127.0.0.1:5000')
        content = response.read().decode('utf-8')
        
        print(f"[OK] Main page loaded (Status: {response.getcode()})")
        print(f"[OK] Content length: {len(content)} characters")
        
        # Check for key elements
        checks = [
            ("Summary section", "Analysis Summary" in content),
            ("Plot cards", content.count('plot-card') > 0),
            ("Sentiment section", "Sentiment Distribution" in content),
            ("Cyberpunk styling", "Orbitron" in content),
            ("Dark theme", "#0d0d0d" in content)
        ]
        
        print("\n[CHECKS]")
        all_passed = True
        for check_name, passed in checks:
            status = "[OK]" if passed else "[FAIL]"
            print(f"{status} {check_name}")
            if not passed:
                all_passed = False
        
        # Test plot files
        print("\n[TEST] Checking plot files...")
        plot_files = [
            'wordcloud_overall.png',
            'sentiment_distribution.png', 
            'confusion_matrix.png',
            'wordcloud_positive.png',
            'wordcloud_negative.png'
        ]
        
        plot_status = True
        for plot_file in plot_files:
            try:
                resp = urllib.request.urlopen(f'http://127.0.0.1:5000/static/plots/{plot_file}')
                print(f"[OK] {plot_file} - Status: {resp.getcode()}")
            except Exception as e:
                print(f"[FAIL] {plot_file} - Error: {e}")
                plot_status = False
        
        print("\n" + "=" * 60)
        if all_passed and plot_status:
            print("[SUCCESS] FRONTEND IS WORKING PERFECTLY!")
            print("[INFO] Open http://127.0.0.1:5000 in your browser")
            print("[INFO] You should see:")
            print("  - Dark cyberpunk theme with neon colors")
            print("  - All plots and word clouds loading")
            print("  - Analysis summary displayed")
            print("  - Sentiment distribution charts")
            print("  - Topic analysis results")
        else:
            print("[ERROR] Some issues detected. Check the failures above.")
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] Cannot connect to Flask app: {e}")
        print("[INFO] Make sure Flask is running: python app.py")

if __name__ == "__main__":
    test_frontend()

