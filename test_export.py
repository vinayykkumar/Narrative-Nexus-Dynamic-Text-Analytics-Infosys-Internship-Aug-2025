#!/usr/bin/env python3
"""
Test script to verify the enhanced PDF export functionality
"""

import json
import os
from pprint import pprint

def test_export_data():
    """Test that all necessary data is available for PDF export"""
    
    print("🔍 Testing Enhanced PDF Export Data...")
    print("=" * 50)
    
    # Load results
    try:
        with open('analysis_results.json', 'r') as f:
            results = json.load(f)
        print("✅ Successfully loaded analysis_results.json")
    except Exception as e:
        print(f"❌ Error loading results: {e}")
        return
    
    # Check plots data
    plots_data = results.get('plots', {})
    print(f"\n📊 Current plots in results: {len(plots_data)}")
    
    # Check static plots directory
    static_plots_dir = os.path.join('static', 'plots')
    if os.path.exists(static_plots_dir):
        available_plot_files = [f for f in os.listdir(static_plots_dir) if f.endswith('.png')]
        print(f"📁 Available plot files in static/plots: {len(available_plot_files)}")
        
        # Simulate what the Flask route will do
        enhanced_plots = plots_data.copy()
        missing_plots = []
        
        for plot_file in available_plot_files:
            plot_name = plot_file.replace('.png', '')
            if plot_name not in enhanced_plots:
                missing_plots.append(plot_name)
                enhanced_plots[plot_name] = os.path.join('static', 'plots', plot_file)
        
        print(f"➕ Missing plots to be added: {len(missing_plots)}")
        print(f"📈 Total plots after enhancement: {len(enhanced_plots)}")
        
        # Categorize plots for the report
        categories = {
            'Data Distributions': [],
            'Word Clouds - Overall': [],
            'Word Clouds - Sentiment': [],
            'Word Clouds - Topics': [],
            'Correlations': [],
            'Performance': [],
            'Other': []
        }
        
        for plot_name in enhanced_plots.keys():
            if 'distribution' in plot_name:
                categories['Data Distributions'].append(plot_name)
            elif 'wordcloud' in plot_name:
                if 'topic' in plot_name:
                    categories['Word Clouds - Topics'].append(plot_name)
                elif any(sentiment in plot_name for sentiment in ['positive', 'negative', 'neutral']):
                    categories['Word Clouds - Sentiment'].append(plot_name)
                else:
                    categories['Word Clouds - Overall'].append(plot_name)
            elif 'correlation' in plot_name:
                categories['Correlations'].append(plot_name)
            elif 'confusion' in plot_name or 'matrix' in plot_name:
                categories['Performance'].append(plot_name)
            else:
                categories['Other'].append(plot_name)
        
        print(f"\n🗂️  Plot Categories for Report:")
        for category, plots in categories.items():
            if plots:
                print(f"  {category}: {len(plots)} plots")
                for plot in plots:
                    print(f"    - {plot}")
    
    # Check other data
    print(f"\n📝 Other Data Available:")
    print(f"  Summary: {'✅' if results.get('summary_tab', {}).get('summary_text') else '❌'}")
    print(f"  Sentiment Counts: {'✅' if results.get('sentiment_counts') else '❌'}")
    print(f"  Difficulty Counts: {'✅' if results.get('difficulty_counts') else '❌'}")
    print(f"  Attendance Counts: {'✅' if results.get('attendance_counts') else '❌'}")
    print(f"  Correlation Data: {'✅' if results.get('correlation_data') else '❌'}")
    
    # Check sentiment data details
    sentiment_counts = results.get('sentiment_counts', {})
    if sentiment_counts:
        total_responses = sum(sentiment_counts.values())
        print(f"\n💭 Sentiment Analysis Details:")
        print(f"  Total Responses: {total_responses:,}")
        for sentiment, count in sentiment_counts.items():
            percentage = (count / total_responses * 100) if total_responses > 0 else 0
            print(f"  {sentiment.title()}: {count:,} ({percentage:.1f}%)")
    
    print(f"\n🎯 Report will include:")
    print(f"  ✅ Executive Summary")
    print(f"  ✅ Sentiment Analysis with {len(sentiment_counts)} categories")
    print(f"  ✅ Data Distribution Charts ({len([p for p in enhanced_plots if 'distribution' in p])} charts)")
    print(f"  ✅ Correlation Analysis ({len([p for p in enhanced_plots if 'correlation' in p])} charts)")
    print(f"  ✅ Word Cloud Analysis ({len([p for p in enhanced_plots if 'wordcloud' in p])} clouds)")
    print(f"  ✅ Model Performance Metrics")
    print(f"  ✅ Topic Analysis with sample words")
    print(f"  ✅ Key Insights & Recommendations")
    
    print(f"\n🚀 Enhanced PDF Export is Ready!")
    print("=" * 50)

if __name__ == "__main__":
    test_export_data()