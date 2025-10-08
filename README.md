# Narrative-Nexus-Dynamic-Text-Analytics-Infosys-Internship-Aug-2025
# 🌌 Smart DataSet Analyzer – Advanced NLP Text Analysis Platform

**AI-powered text analysis platform** — upload `.txt`, `.csv`, or `.docx` files to instantly get **sentiment analysis**, **topic modeling**, **key terms**, and **downloadable PDF reports**.

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.8-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.4-06B6D4?style=for-the-badge&logo=tailwind-css&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge&logo=opensourceinitiative&logoColor=white)

</div>

**Smart DataSet Analyzer** is a comprehensive web application for advanced Natural Language Processing (NLP) analysis, including sentiment analysis, topic modeling, text summarization, and professional PDF report generation. It offers both a modern frontend dashboard and a high-performance backend API for end-to-end text analytics.

---

## 🖼️ UI Preview

### 🏠 Landing Page
<div align="center">
  <img src="./assets/landing-page.png" alt="Landing Page" width="80%">
  <p><i>Modern hero section with feature highlights and quick-start call-to-action</i></p>
</div>

### 📤 Upload Page
<div align="center">
  <img src="./assets/upload-page.png" alt="Upload Page" width="80%">
  <p><i>Drag-and-drop file upload interface with CSV/TXT support and column selection</i></p>
</div>

### 📊 Analysis Dashboard
<div align="center">
  <img src="./assets/analysis-page.png" alt="Analysis Dashboard" width="80%">
  <p><i>Interactive dashboard with sentiment analysis, topic modeling, and real-time visualizations</i></p>
</div>

---

## 🚀 Key Features

Sentiment Analysis – Multi-model detection with VADER and ensemble methods

Topic Modeling – LDA and NMF with coherence scoring

Text Summarization – Extractive summarization with advanced NLP techniques

Classification – Supervised learning with cross-validation and optimization

Professional Reports – Four distinct PDF report types with customizable formatting

Interactive Dashboard – Real-time analysis with beautiful visualizations

Responsive Design – Works seamlessly on desktop and mobile

Error Handling & Logging – Robust error management and detailed Loguru logs

---

## 📊 Report Types

Executive Summary – Business-focused overview with key insights

Detailed Analysis – Comprehensive technical analysis with statistics

Visual Report – Chart-centric presentation with interactive visualizations

Overall Report – Complete analysis combining all sections and appendices

---

## 🛠 Tech Stack

### Frontend

React 18 with TypeScript

Vite for fast builds and development

Tailwind CSS for responsive styling

Recharts for interactive charts

shadcn/ui for polished UI components

### Backend

FastAPI for high-performance REST API

Python 3.11+ with advanced NLP libraries

spaCy for natural language processing

scikit-learn for machine learning models

FPDF / python-docx for professional PDF generation


---

## 📁 Project Structure
smart-dataset-analyzer/
├── frontend/                     # 💻 Frontend React application
│   ├── components/               # Reusable React components
│   │   ├── AnalysisPage.tsx      # Main analysis dashboard
│   │   ├── HeroPage.tsx          # Landing page with hero section
│   │   ├── UploadPage.tsx        # Drag-and-drop file upload
│   │   └── ui/                   # shadcn/ui component library (40+ components)
│   ├── contexts/                 # React Context API
│   │   └── AnalysisContext.tsx   # Global state management
│   ├── hooks/                    # Custom React hooks
│   ├── lib/                      # Utility functions
│   ├── pages/                    # Page components
│   ├── App.tsx                   # Root component
│   ├── main.tsx                  # Application bootstrap
│   ├── App.css                   # Global styles
│   ├── index.css                 # Tailwind CSS imports
│   └── README.md                 # 📘 Frontend-specific docs
│
├── backend/                      # 🖥️ Python FastAPI backend
│   ├── pipeline/                 # NLP processing pipeline
│   │   ├── preprocessing.py      # Text cleaning & feature engineering
│   │   ├── topic_modeling.py     # LDA & NMF algorithms
│   │   ├── sentiment.py          # VADER sentiment analysis
│   │   ├── classification.py     # ML classification models
│   │   ├── summarization.py      # Extractive summarization
│   │   └── reporting.py          # PDF report generation
│   ├── main.py                   # FastAPI server & API endpoints
│   ├── utils.py                  # Backend helper functions
│   ├── requirements.txt          # Python dependencies
│   └── README.md                 # 📗 Backend API documentation
│
├── outputs/                      # 📊 Generated charts, PDFs, and reports
├── results/                      # 💾 Cached analysis results (JSON)
├── uploads/                      # 📁 User-uploaded files
├── models/                       # 🤖 Trained ML models
├── assets/                       # 🖼️ UI screenshots and images
└── README.md                     # 📖 Main documentation (you are here)

Node.js 18+ and npm

Python 3.11+

Git

### Installation

**1. Clone Repository**

git clone <repository-url>
cd smart-dataset-analyzer


**2. Setup Frontend**

cd src
npm install


**3. Setup Backend**

cd backend

# Create virtual environment
python -m venv smart-env

# Activate virtual environment
# Windows:
smart-env\Scripts\activate
# macOS/Linux:
source smart-env/bin/activate

# Install dependencies
pip install -r requirements.txt

### Running the Application

**1. Start Backend Server**

cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8001


Runs at: http://localhost:8001

**2. Start Frontend Development Server**

cd src
npm run dev


Runs at: http://localhost:8000


---

## 📖 Usage

Upload Data – CSV/TXT files with text content

Run Analysis – Process data through NLP pipeline

View Results – Explore interactive dashboards: sentiment, topics, and metrics

Generate Reports – Export professional PDFs

Export Data – Save results and charts

---

## 🔧 API Endpoints

POST /upload – Upload files for analysis

POST /analyze – Run complete NLP analysis

POST /generate-pdf/{filename} – Generate PDF reports

GET /download/report/{type}/{filename} – Download generated reports

📈 Analysis Pipeline

Data Preprocessing – Cleaning, normalization, tokenization

Feature Engineering – TF-IDF & Bag-of-Words

Topic Modeling – LDA & NMF with coherence scoring

Sentiment Analysis – VADER & ensemble methods

Classification – Supervised learning with cross-validation

Summarization – Extractive summarization

Report Generation – Professional PDFs with charts and tables

---

## 🎨 Visualization & Design

Real-time Processing – Live updates during analysis

Interactive Charts – Sentiment, topics, ROC curves, and confusion matrices

Responsive UI – Desktop, tablet, and mobile-friendly

Professional Reports – Export-ready PDF documents

---

## 🤝 Contributing

Fork the repository

Create a feature branch: git checkout -b feature/my-feature

Commit changes: git commit -m "Add new feature"

Push branch: git push origin feature/my-feature

Open a Pull Request

---

## 📄 License

MIT License – see LICENSE file for details

---

## 🙏 Acknowledgments

Built using modern web technologies and advanced NLP libraries

Inspired by the need for professional, accessible text analysis tools

Thanks to the open-source community for excellent libraries

Smart DataSet Analyzer – Transforming text data into actionable insights with professional-grade analysis and reporting. 🚀
