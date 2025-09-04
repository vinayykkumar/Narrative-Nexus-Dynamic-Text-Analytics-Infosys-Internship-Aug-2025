import subprocess
import sys
import nltk

def install_requirements():
    """Install required packages and models"""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("Downloading NLTK data...")
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('punkt', quiet=True)
    
    print("Installing spaCy English model...")
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    
    print("Setup completed successfully!")

if __name__ == "__main__":
    install_requirements()

