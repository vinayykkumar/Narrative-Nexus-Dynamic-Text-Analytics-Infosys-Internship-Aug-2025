#!/usr/bin/env python3
"""
Test Flask export route to debug errors
"""

from flask import Flask, render_template, url_for
import json
import os

app = Flask(__name__)

@app.route('/test-export')
def test_export():
    """Test export route with simplified logic"""
    try:
        # Load results
        with open('analysis_results.json', 'r') as f:
            results = json.load(f)
        
        print("✅ Successfully loaded analysis_results.json")
        
        # Get plots data
        plots_data = results.get('plots', {})
        print(f"📊 Original plots: {len(plots_data)}")
        
        # Add missing plots
        static_plots_dir = os.path.join('static', 'plots')
        if os.path.exists(static_plots_dir):
            available_plot_files = os.listdir(static_plots_dir)
            for plot_file in available_plot_files:
                if plot_file.endswith('.png'):
                    plot_name = plot_file.replace('.png', '')
                    if plot_name not in plots_data:
                        plots_data[plot_name] = os.path.join('static', 'plots', plot_file)
        
        print(f"📈 Enhanced plots: {len(plots_data)}")
        
        # Extract summary
        summary_text = ""
        if "summary_tab" in results and "summary_text" in results["summary_tab"]:
            summary_text = results["summary_tab"]["summary_text"]
        
        # Test template rendering
        template_data = {
            'filename': 'test_dataset',
            'summary': summary_text,
            'insights': 'Test insights for debugging',
            'sentiment_counts': results.get('sentiment_counts', {}),
            'sentiment_text': 'Test sentiment interpretation',
            'plots': plots_data,
            'lda_top_words': [['test', 'words', 'topic', 'one'], ['another', 'test', 'topic', 'two']],
            'nmf_top_words': [['nmf', 'test', 'topic']],
            'classification_metrics': {'accuracy': 0.85, 'precision': 0.82},
            'correlation_data': results.get('correlation_data', {}),
            'difficulty_counts': results.get('difficulty_counts', {}),
            'attendance_counts': results.get('attendance_counts', {})
        }
        
        print("🎯 Template data prepared")
        print(f"  - Plots: {len(template_data['plots'])}")
        print(f"  - Sentiment categories: {len(template_data['sentiment_counts'])}")
        print(f"  - LDA topics: {len(template_data['lda_top_words'])}")
        
        return render_template('export-pdf-new.html', **template_data)
        
    except Exception as e:
        print(f"❌ Error in test export: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}"

@app.route('/serve-plot/<filename>')
def serve_plot(filename):
    """Simple plot serving route"""
    return app.send_static_file(f'plots/{filename}')

if __name__ == '__main__':
    # Test template rendering without running server
    with app.app_context():
        try:
            result = test_export()
            if isinstance(result, str) and result.startswith("Error:"):
                print(result)
            else:
                print("✅ Template rendered successfully!")
        except Exception as e:
            print(f"❌ Template rendering failed: {e}")
            import traceback
            traceback.print_exc()