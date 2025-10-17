#!/usr/bin/env python3
"""
Standalone analysis script that generates plots without Flask interference
"""

import os
import sys
import warnings
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
plt.ioff()  # Turn off interactive mode

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main analysis function
from main import main

def generate_plots():
    """Generate all plots and analysis results"""
    print("[INFO] Generating analysis and plots...")
    
    try:
        # Run the main analysis
        results = main(use_gemini=False)
        
        print("[OK] Analysis completed successfully!")
        print(f"[INFO] Generated {len(results.get('plots', {}))} plots")
        print(f"[INFO] Summary: {len(results.get('summary', ''))} characters")
        
        return results
        
    except Exception as e:
        print(f"[ERROR] Error during analysis: {e}")
        return None

if __name__ == "__main__":
    # Suppress warnings
    warnings.filterwarnings("ignore")
    
    print("=" * 50)
    print("[AI] FEEDBACK ANALYSIS GENERATOR")
    print("=" * 50)
    
    results = generate_plots()
    
    if results:
        print("\n[SUCCESS] All plots and analysis generated.")
        print("[INFO] Now start your Flask app: python app.py")
        print("[INFO] Open: http://127.0.0.1:5000")
    else:
        print("\n[ERROR] FAILED! Check the error messages above.")
    
    print("=" * 50)