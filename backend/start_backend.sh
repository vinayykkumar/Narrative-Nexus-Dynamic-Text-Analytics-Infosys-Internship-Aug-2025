#!/bin/bash

# AI Narrative Nexus Backend Startup Script

echo "🚀 Starting AI Narrative Nexus Backend..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
min_version="3.8"

if [ "$(printf '%s\n' "$min_version" "$python_version" | sort -V | head -n1)" = "$min_version" ]; then
    echo "✅ Python $python_version detected"
else
    echo "❌ Python $python_version is too old. Please install Python 3.8 or higher."
    exit 1
fi

# Navigate to backend directory
cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Download NLTK data
echo "🔤 Downloading NLTK data..."
python3 -c "
import nltk
try:
    nltk.data.find('tokenizers/punkt')
    print('punkt already downloaded')
except LookupError:
    nltk.download('punkt')
    print('punkt downloaded')

try:
    nltk.data.find('corpora/stopwords')
    print('stopwords already downloaded')
except LookupError:
    nltk.download('stopwords')
    print('stopwords downloaded')

try:
    nltk.data.find('corpora/wordnet')
    print('wordnet already downloaded')
except LookupError:
    nltk.download('wordnet')
    print('wordnet downloaded')

try:
    nltk.data.find('corpora/omw-1.4')
    print('omw-1.4 already downloaded')
except LookupError:
    nltk.download('omw-1.4')
    print('omw-1.4 downloaded')
"

# Check if .env file exists, create template if not
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env configuration file..."
    cat > .env << EOL
# AI Narrative Nexus Backend Configuration

# Application settings
APP_NAME="AI Narrative Nexus Backend"
DEBUG=false

# Server settings
HOST=0.0.0.0
PORT=8000
RELOAD=true

# Security (change in production)
SECRET_KEY=your-secret-key-here-change-in-production

# External APIs (optional)
OPENAI_API_KEY=""
HUGGINGFACE_API_KEY=""

# Logging
LOG_LEVEL=INFO
EOL
    echo "📝 Created .env file. Please review and update the configuration."
fi

# Start the server
echo "🌐 Starting FastAPI server..."
echo "📍 Backend will be available at: http://localhost:8000"
echo "📖 API documentation at: http://localhost:8000/docs"
echo "🔧 Alternative docs at: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
