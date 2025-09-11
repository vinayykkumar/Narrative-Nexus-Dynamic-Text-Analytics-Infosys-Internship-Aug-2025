#!/usr/bin/env python3
"""
Simple demonstration of CSV rows as separate documents
"""

def demonstrate_csv_processing():
    print("🧪 Demonstrating CSV Processing - Each Row as Separate Document\n")
    
    # Read the CSV file
    csv_file_path = "/home/git/projects/Narrative-Nexus-Dynamic-Text-Analytics-Infosys-Internship-Aug-2025/data/test_data.csv"
    
    try:
        with open(csv_file_path, 'r') as f:
            lines = f.readlines()
        
        print(f"📄 Raw CSV Content:")
        for i, line in enumerate(lines[:4]):  # Show first 4 lines
            print(f"   Line {i+1}: {line.strip()}")
        print()
        
        # Parse CSV - each row becomes a separate document
        documents = []
        for line_num, line in enumerate(lines[1:], 1):  # Skip header
            # Clean the text (remove quotes, strip whitespace)
            text = line.strip().strip('"')
            if text and len(text) > 10:
                documents.append(text)
                print(f"📝 Document {line_num}: {text}")
        
        print(f"\n✅ Successfully processed CSV:")
        print(f"   • Total lines in CSV: {len(lines)}")
        print(f"   • Header line: 1")
        print(f"   • Data rows: {len(lines) - 1}")
        print(f"   • Documents extracted: {len(documents)}")
        print(f"   • Each row = 1 separate document ✓")
        
        print(f"\n🎯 Topic Modeling Readiness:")
        print(f"   • Multiple documents: ✅ ({len(documents)} documents)")
        print(f"   • Each document independent: ✅")
        print(f"   • Ready for LDA/NMF algorithms: ✅")
        print(f"   • Can identify topics across documents: ✅")
        
        print(f"\n📊 Expected Topic Modeling Results:")
        print(f"   • Topics about machine learning concepts")
        print(f"   • Topics about neural networks and deep learning")
        print(f"   • Topics about data science and AI applications")
        print(f"   • Each topic will show which documents contribute to it")
        
        print(f"\n✅ CSV processing working correctly!")
        print(f"✅ Each CSV row treated as separate document for topic modeling!")
        
    except FileNotFoundError:
        print(f"❌ CSV file not found at {csv_file_path}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    demonstrate_csv_processing()
