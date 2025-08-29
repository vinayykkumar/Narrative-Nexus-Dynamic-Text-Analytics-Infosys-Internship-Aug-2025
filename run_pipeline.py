import os
import sys
import subprocess

def run_script(script_name, description):
    """Run a Python script and handle any errors"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, check=True)
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}:")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    return True

def main():
    """Run the complete text processing pipeline"""
    print("🚀 Starting Text Processing Pipeline")
    print("="*50)
    
    # Check if input file exists
    input_file = r"D:\Infosys_SpringBoard\Dataset\arxiv-metadata-oai-snapshot.json"
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return
    
    # Create JSON directory if it doesn't exist
    json_dir = r"D:\Infosys_SpringBoard\JSON"
    os.makedirs(json_dir, exist_ok=True)
    
    # Run pipeline steps
    steps = [
        ("clean_text.py", "Text Cleaning"),
        ("tokenize_text.py", "Text Tokenization"),
        ("remove_stopwords.py", "Stopword Removal"),
        ("lemmatization_parallel.py", "Lemmatization")
    ]
    
    success_count = 0
    for script, description in steps:
        if run_script(script, description):
            success_count += 1
        else:
            print(f"❌ Pipeline failed at: {description}")
            break
    
    print(f"\n{'='*50}")
    print(f"Pipeline completed: {success_count}/{len(steps)} steps successful")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()

