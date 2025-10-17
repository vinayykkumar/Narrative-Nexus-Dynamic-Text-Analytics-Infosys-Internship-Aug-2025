#!/usr/bin/env python3
"""
Create analysis results file for Flask app
"""

import os
import sys
import json
import warnings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.ioff()

# Import the main analysis function
from main import main

def create_results_file():
    """Generate analysis and save results to JSON file"""
    print("[INFO] Generating analysis results...")
    
    try:
        # Run the main analysis
        results = main(use_gemini=False)
        
        # Save results to JSON file
        with open('analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("[OK] Analysis results saved to analysis_results.json")
        print(f"[INFO] Summary length: {len(results.get('summary', ''))} characters")
        print(f"[INFO] Plots generated: {len(results.get('plots', {}))}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to generate results: {e}")
        return False

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    
    print("=" * 50)
    print("CREATING ANALYSIS RESULTS FILE")
    print("=" * 50)
    
    success = create_results_file()
    
    if success:
        print("\n[SUCCESS] Results file created!")
        print("[INFO] Flask app will now load this data")
    else:
        print("\n[ERROR] Failed to create results file")
    
    print("=" * 50)

