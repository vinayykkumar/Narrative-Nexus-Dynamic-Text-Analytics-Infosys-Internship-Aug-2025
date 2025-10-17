#!/usr/bin/env python3
"""
Test script to debug Flask app JSON loading
"""

import json
import os

def test_json_loading():
    print("Testing JSON loading...")
    
    results_file = "analysis_results.json"
    
    if os.path.exists(results_file):
        print("Results file exists")
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            print(f"JSON loaded successfully")
            print(f"Keys: {list(results.keys())}")
            print(f"Summary length: {len(results.get('summary', ''))}")
            print(f"Summary preview: {results.get('summary', 'NO SUMMARY')[:100]}")
            print(f"Plots count: {len(results.get('plots', {}))}")
            return results
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return None
    else:
        print("Results file does not exist")
        return None

if __name__ == "__main__":
    results = test_json_loading()
    if results:
        print("\n[SUCCESS] JSON loading works correctly")
    else:
        print("\n[ERROR] JSON loading failed")

