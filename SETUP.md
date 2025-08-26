# 🛠️ Detailed Setup Guide

### Required Software

#### 1. Node.js and npm
```bash
# Check if installed
node --version  # Should be 20.19.2+
npm --version   # Should be 10.0.0+

# Install via Node Version Manager (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20.19.2
nvm use 20.19.2
```

#### 2. Python 3.13+
```bash
# Check installation
python3 --version  # Should be 3.13+

# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# macOS (using Homebrew)
brew install python@3.13

# Windows
# Download from https://www.python.org/downloads/
```

#### 3. Git
```bash
# Check installation
git --version

# Ubuntu/Debian
sudo apt install git

# macOS
xcode-select --install

# Windows
# Download from https://git-scm.com/download/win
```

## Step-by-Step Setup

### 1. Clone and Navigate

```bash
# Clone the repository
git clone https://github.com/0x1git/Nexus.git
cd Nexus

# Verify project structure
ls -la
```

Expected output:
```
drwxr-xr-x  app/
drwxr-xr-x  components/
drwxr-xr-x  dataset/
drwxr-xr-x  python_preprocessing/
-rw-r--r--  package.json
-rw-r--r--  README.md
...
```

### 2. Frontend Setup (Next.js)

```bash
# Install Node.js dependencies
npm install

# Verify installation
npm list --depth=0
```

Expected packages:
- `next@15.2.4`
- `react@19.1.1`
- `typescript@5.7.2`
- Plus UI and utility packages

### 3. Backend Setup (Python ML)

#### Option A: Automated Setup (Recommended)
```bash
# Run the setup script
chmod +x setup_preprocessing.sh
./setup_preprocessing.sh
```

#### Option B: Manual Setup
```bash
# Create Python virtual environment
python3 -m venv python_preprocessing/venv

# Activate virtual environment
# Linux/macOS:
source python_preprocessing/venv/bin/activate
# Windows:
# python_preprocessing\venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install pandas==2.3.2 numpy==2.3.2 scikit-learn==1.7.1 nltk==3.9.1 joblib

# Download NLTK data
python3 -c "
import nltk
nltk.download('punkt_tab')
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
print('NLTK data downloaded successfully!')
"
```

### 4. Dataset Preparation

```bash
# Create dataset directory if it doesn't exist
mkdir -p dataset

# Example: Download sample datasets (optional)
# You can add your own datasets here

# Verify dataset directory
ls -la dataset/
```

Supported dataset formats:
- **CSV**: Comma-separated values
- **TSV**: Tab-separated values  
- **JSON**: JavaScript Object Notation
- **TXT**: Plain text files

Expected dataset structure:
```
dataset/
├── amazon_alexa.tsv          # Product reviews
├── twitter_sentiment.csv     # Social media posts
└── your_custom_data.csv      # Your data
```

### 5. Environment Verification

```bash
# Test Node.js setup
npm run build

# Test Python setup
source python_preprocessing/venv/bin/activate
python3 -c "
import pandas as pd
import numpy as np
import sklearn
import nltk
print('All Python packages imported successfully!')
print(f'pandas: {pd.__version__}')
print(f'numpy: {np.__version__}')
print(f'scikit-learn: {sklearn.__version__}')
print(f'nltk: {nltk.__version__}')
"
```

### 6. Initial Data Processing (Optional)

```bash
# Activate Python environment
source python_preprocessing/venv/bin/activate

# Test preprocessing pipeline with sample data
python3 python_preprocessing/test_preprocessing_integration.py

# Process datasets (if available)
# python3 python_preprocessing/process_datasets.py --dataset all
```

### 7. Start Development Server

```bash
# Start the Next.js development server
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) to verify the setup.

## Troubleshooting

### Common Issues

#### 1. Node.js Version Issues
```bash
# Error: Node.js version incompatibility
# Solution: Use Node Version Manager
nvm install 20.19.2
nvm use 20.19.2
npm install
```

#### 2. Python Virtual Environment Issues
```bash
# Error: Virtual environment not activating
# Solution: Recreate virtual environment
rm -rf python_preprocessing/venv
python3 -m venv python_preprocessing/venv
source python_preprocessing/venv/bin/activate
pip install -r requirements.txt  # If available
```

#### 3. NLTK Data Download Issues
```bash
# Error: NLTK data not found
# Solution: Manual download with specific directory
python3 -c "
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')
"
```

#### 4. Port Already in Use
```bash
# Error: Port 3000 already in use
# Solution: Use different port
npm run dev -- -p 3001
```

#### 5. Permission Issues (Linux/macOS)
```bash
# Error: Permission denied
# Solution: Fix permissions
chmod +x setup_preprocessing.sh
sudo chown -R $USER:$USER python_preprocessing/
```

#### 6. Build Errors
```bash
# Clear caches and reinstall
rm -rf .next/
rm -rf node_modules/
npm install
npm run build
```

### Platform-Specific Setup

#### Windows Specific
```powershell
# Use PowerShell or Git Bash
# Virtual environment activation
python_preprocessing\venv\Scripts\activate

# If execution policy issues
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### macOS Specific
```bash
# Install Xcode command line tools
xcode-select --install

# Use Homebrew for Python
brew install python@3.13
```

#### Linux Specific
```bash
# Install build essentials
sudo apt install build-essential python3-dev

# For CentOS/RHEL
# sudo yum groupinstall "Development Tools"
# sudo yum install python3-devel
```

## Environment Variables

Create a `.env.local` file in the project root:

```env
# Development settings
NODE_ENV=development
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Python settings
PYTHON_ENV=development
NLTK_DATA=/path/to/nltk_data

# Optional: API keys
# OPENAI_API_KEY=your_api_key_here
# HUGGINGFACE_API_KEY=your_api_key_here
```

## IDE Setup

### VS Code (Recommended)
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./python_preprocessing/venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "typescript.preferences.importModuleSpecifier": "relative",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

Recommended extensions:
- Python
- TypeScript and JavaScript Language Features
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense

### PyCharm
1. Open the project directory
2. Configure Python interpreter: `python_preprocessing/venv/bin/python`
3. Set content root: Mark `python_preprocessing` as Sources Root

## Verification Checklist

- [ ] Node.js 20.19.2+ installed
- [ ] Python 3.13+ installed
- [ ] Git installed and configured
- [ ] Repository cloned successfully
- [ ] npm packages installed without errors
- [ ] Python virtual environment created
- [ ] Python packages installed
- [ ] NLTK data downloaded
- [ ] Development server starts on port 3000
- [ ] Preprocessing demo accessible at `/preprocessing`
- [ ] No console errors in browser
- [ ] Python integration test passes

## Next Steps

After successful setup:

1. **Explore the Interface**: Visit `/preprocessing` to see text processing in action
2. **Add Your Data**: Place datasets in the `dataset/` directory
3. **Process Data**: Run the preprocessing pipeline on your data
4. **Train Models**: Use the ML pipeline to create custom models
5. **Customize**: Modify components and styling as needed

## Getting Help

If you encounter issues:

1. **Check the logs**: Look for error messages in terminal output
2. **Verify versions**: Ensure all dependencies meet requirements  
3. **Clean installation**: Remove `node_modules` and reinstall
4. **Platform differences**: Check platform-specific instructions
5. **Ask for help**: Create an issue on GitHub with error details

---

