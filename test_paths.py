#!/usr/bin/env python3
"""
Test script to debug plot path fixing
"""

import json

def test_path_fixing():
    print("Testing plot path fixing...")
    
    # Load the JSON data
    with open('analysis_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    plots = data.get("plots", {})
    print(f"Original plots count: {len(plots)}")
    
    # Show first few original paths
    print("\nOriginal paths:")
    for i, (key, path) in enumerate(list(plots.items())[:3]):
        print(f"  {key}: {path}")
    
    # Fix the paths
    fixed_plots = {}
    for key, path in plots.items():
        if isinstance(path, str):
            # Extract just the filename if it's a full path
            filename = path.split('\\')[-1].split('/')[-1]
            fixed_plots[key] = filename
        else:
            fixed_plots[key] = path
    
    print("\nFixed paths:")
    for i, (key, path) in enumerate(list(fixed_plots.items())[:3]):
        print(f"  {key}: {path}")
    
    return fixed_plots

if __name__ == "__main__":
    fixed_plots = test_path_fixing()
    print(f"\nTotal fixed plots: {len(fixed_plots)}")

