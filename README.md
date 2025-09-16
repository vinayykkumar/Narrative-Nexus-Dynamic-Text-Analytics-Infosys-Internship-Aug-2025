# 🎯 AI Narrative Nexus - Dynamic Text Analytics Platform

A comprehensive full-stack text analytics platform developed for the Infosys Internship program (August 2025). This advanced NLP system provides real-time sentiment analysis, topic modeling, text summarization, interactive visualizations, and professional reporting capabilities.

## 🚀 **PROJECT COMPLETED SUCCESSFULLY** ✅

All 8-week development timeline objectives have been achieved with full-stack implementation including:
- ✅ **Sentiment Analysis**: Real-time lexicon-based analysis with emotional indicators  
- ✅ **Topic Modeling**: LDA/NMF implementations with interactive debugging
- ✅ **Text Summarization**: Frequency-based and TF-IDF extractive methods
- ✅ **Advanced Visualizations**: Interactive charts and analytics dashboards
- ✅ **Comprehensive Reporting**: PDF export, email delivery, and data sharing
- ✅ **Professional UI**: Modern React interface with dark/light themes

## 🎪 **Quick Start**

### **Live Demo Access**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs

### **Installation**
```bash
# Backend Setup
cd backend
pip install --break-system-packages fastapi uvicorn python-multipart pydantic nltk aiofiles requests
python app_minimal.py

# Frontend Setup (new terminal)
npm install chart.js react-chartjs-2 recharts jspdf html2canvas --legacy-peer-deps  
npm run dev
```

## 📋 **Complete Feature Overview**

| Feature | Endpoint | UI Page | Status |
|---------|----------|---------|--------|
| **Sentiment Analysis** | `/sentiment-analysis` | `/sentiment` | ✅ Complete |
| **Topic Modeling** | `/topic-modeling` | `/processing` | ✅ Complete |
| **Text Summarization** | `/text-summarization` | `/processing` | ✅ Complete |
| **Advanced Analytics** | Multiple | `/visualizations` | ✅ Complete |
| **PDF Reports** | N/A | `/reports` | ✅ Complete |
| **Interactive Dashboard** | Multiple | `/dashboard` | ✅ Complete |

## 🏗️ **Architecture**

**Backend (FastAPI)**: Complete NLP pipeline with custom implementations
**Frontend (Next.js 15 + React)**: Modern responsive interface  
**Visualizations**: Chart.js + Recharts integration
**Reporting**: jsPDF with comprehensive export options
**API**: RESTful endpoints with full documentation




## 🎯 **Key Achievements**

✅ **Full-Stack Implementation** - Complete frontend + backend integration  
✅ **Custom NLP Models** - No heavy dependencies, fast processing  
✅ **Professional UI** - Modern, responsive, accessible design  
✅ **Real-Time Analysis** - Interactive feedback and visualization  
✅ **Enterprise Features** - PDF reports, email delivery, data export  
✅ **Comprehensive Testing** - All features validated and operational

**Final Status**: 🏆 **ALL PROJECT OBJECTIVES COMPLETED** 🏆

## 🎯 Project Overview

AI Narrative Nexus is an 8-week development project aimed at creating a dynamic text analysis platform capable of processing various text inputs and providing comprehensive insights through:

- **Topic Modeling**: Identify key themes using LDA and NMF algorithms
- **Sentiment Analysis**: Assess emotional tone with 90%+ accuracy
- **Text Summarization**: Generate concise extractive and abstractive summaries
- **Interactive Visualizations**: Word clouds, sentiment distribution, topic graphs
- **Comprehensive Reporting**: Actionable insights and recommendations




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
