#!/bin/bash

# AI Narrative Nexus - Setup and Preprocessing Script

echo "========================================"
echo "AI Narrative Nexus - Data Preprocessing"
echo "========================================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

echo "Python version: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "python_preprocessing/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv python_preprocessing/venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source python_preprocessing/venv/bin/activate

# Install required packages
echo "Installing required packages..."
pip install --upgrade pip
pip install -r python_preprocessing/requirements.txt

# Download NLTK data
echo "Downloading NLTK data..."
python3 -c "
import nltk
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
print('NLTK data downloaded successfully')
"

echo "Setup complete!"
echo ""
echo "To run preprocessing:"
echo "1. Activate the virtual environment: source python_preprocessing/venv/bin/activate"
echo "2. Run the preprocessing script: python3 python_preprocessing/process_datasets.py"
echo ""
echo "Available options:"
echo "  --dataset alexa          # Process only Amazon Alexa reviews"
echo "  --dataset twitter        # Process only Twitter sentiment data"
echo "  --dataset amazon_reviews # Process only Amazon product reviews"
echo "  --dataset all            # Process all datasets (default)"
echo "  --twitter-sample 5000    # Sample size for Twitter dataset"
echo "  --output-dir ./output    # Custom output directory"
