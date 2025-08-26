# 🧠 AI Narrative Nexus

> **Dynamic Text Analysis Platform for Advanced NLP Insights**

A comprehensive text analysis platform that combines cutting-edge machine learning with an intuitive web interface to extract themes, analyze sentiment, and generate actionable insights from textual data.



## 🎯 Project Overview

AI Narrative Nexus is an 8-week development project aimed at creating a dynamic text analysis platform capable of processing various text inputs and providing comprehensive insights through:

- **Topic Modeling**: Identify key themes using LDA and NMF algorithms
- **Sentiment Analysis**: Assess emotional tone with 90%+ accuracy
- **Text Summarization**: Generate concise extractive and abstractive summaries
- **Interactive Visualizations**: Word clouds, sentiment distribution, topic graphs
- **Comprehensive Reporting**: Actionable insights and recommendations

### Project Timeline
- **Week 1-2**: ✅ Data Collection & Preprocessing (COMPLETE)
- **Week 3**: Topic Modeling Implementation
- **Week 4**: Sentiment Analysis
- **Week 5**: Insights Generation & Summarization
- **Week 6-7**: Visualization & Reporting
- **Week 8**: Final Evaluation & Documentation




### 1-Minute Setup
```bash
# Clone the repository
git clone https://github.com/0x1git/Nexus.git
cd Nexus

# Setup everything (automated)
./setup_preprocessing.sh

# Start the development server
npm install
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) to access the application.

## 📖 Detailed Setup

### 1. Environment Setup

```bash
# Clone and navigate
git clone https://github.com/0x1git/Nexus.git
cd Nexus

# Install Node.js dependencies
npm install

# Setup Python environment
python3 -m venv python_preprocessing/venv
source python_preprocessing/venv/bin/activate  # On Windows: python_preprocessing\venv\Scripts\activate
```


### 5. Start Development

```bash
# Start Next.js development server
npm run dev

# In another terminal, keep Python environment ready
source python_preprocessing/venv/bin/activate
```

## 📚 Usage Guide

### Web Interface

1. **Text Processing Demo** (`/preprocessing`)
   - Enter text in the input area
   - Click "Process Text" to see step-by-step preprocessing
   - View cleaning, normalization, and tokenization results

2. **File Upload** (`/analyze`)
   - Drag and drop text files or use the file picker
   - Supports CSV, TSV, TXT, JSON formats
   - Real-time validation and error handling

3. **Analysis Dashboard** (`/dashboard`)
   - View processed data statistics
   - Interactive charts and visualizations
   - Export results in multiple formats



## 🔧 Development

### Building for Production

```bash
# Build the Next.js application
npm run build

# Start production server
npm start
```



---

**🚀 Ready to analyze text data like never before!**

*Built with ❤️ by the AI Narrative Nexus Team*
