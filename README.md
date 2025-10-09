 🧠 SmartInsights — Narrative Nexus: Dynamic Text Analytics  

A modern **
text analytics platform**with a clean frontend UI (React + Vite) and a lightweight Flask backend for **real‑time text analysis**, sentiment, topic detection, summarization, and report generation.

📌 *Developed as part of Infosys Internship – August 2025*

---

✨ Features

- 🖥️ Frontend: Interactive analyzer dashboard with multiple visualizations.  
- 🧠 Backend: Flask server with REST APIs for text processing.  
- 📊 Sentiment analysis visualization (donut, bar, histogram, trend).  
- 📝 Topic and summary generation (abstractive, extractive, hybrid).  
- 🧾 Report builder and dataset dashboard endpoints.  
- 🚀 Single‑page app with smooth routing and sticky top navigation.  

---

#🧰 Tech Stack

| Layer        | Technology                   |
|--------------|-------------------------------|
| Frontend     | React 18, Vite, React Router  |
| Backend      | Flask, Flask‑CORS             |
| Build/Tools  | npm, Node.js, Python 3.10+    |



## 🏗️ Project Structure


📂 project-root
│
├─ frontend/                     # React + Vite app
│  ├─ src/
│  │  ├─ components/             # NavBar, Modal, Sentiment charts, etc.
│  │  ├─ pages/                  # Landing, Analyzer, Docs pages
│  │  ├─ lib/api.js              # API calls to backend
│  │  ├─ App.jsx, main.jsx
│  │  └─ index.css
│  ├─ package.json
│  └─ vite.config.js
│
├─ src/ (optional for Python)    # backend logic files if expanded
│
├─ ui_input.py                   # Flask backend server
├─ requirements.txt
└─ README.md




⚡ How It Works

1. 🧑 User pastes or uploads text into the **Analyzer** UI.  
2. 🌐 The frontend sends a `POST` request to `/analyze` on the Flask server.  
3. 🤖 The backend runs analysis (demo or actual NLP pipeline).  
4. 📈 The frontend renders sentiment, summaries, topics, keywords, and a **downloadable PDF report**.



🖥️ Frontend Setup

> Requires [Node.js](https://nodejs.org/) 18+

bash
# 1. Go to frontend folder
cd frontend

# 2. Install dependencies
npm install

# 3. Run development server
npm run dev

# 4. Build for production (optional)
npm run build
npm run preview


Frontend will start at **http://localhost:5173** by default.

To change backend API URL, edit:

frontend/.env
VITE_API_BASE=http://localhost:5000




## 🐍 Backend Setup

> Requires Python 3.10+

bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the Flask server
python ui_input.py


Backend runs on **http://localhost:5000** by default.



## 🌐 API Endpoints

### `POST /analyze`  
Analyze the given text and return results.

**Request JSON**
json
{
  "text": "This is a demo text for analysis."
}


**Response JSON**
json
{
  "ok": true,
  "summary_abstractive": "Abstractive summary of: This is a demo text...",
  "summary_extractive": "Extractive summary of: This is a demo text...",
  "summary_hybrid": "Hybrid summary of: This is a demo text...",
  "sentiment_label": "neutral",
  "sentiment_score": 0.0,
  "predicted_topic": null,
  "predicted_label": null,
  "wordcloud_url": "/assets/demo-wordcloud.png",
  "insights": ["Demo insight 1", "Demo insight 2"],
  "key_terms": ["demo", "insight", "smartinsights"],
  "key_uni_counts": {"demo": 2, "insight": 1},
  "rep_sentences": ["This is a demo sentence."],
  "sentence_scores": [0.0]
}




POST /build_report
Generates a demo HTML report and returns its URL.

**Response**
json
{
  "ok": true,
  "url": "/static/demo-report.html"
}




GET /dataset/topics
Returns available dataset topics (demo).

GET /dataset/topic_wordcloud/<topic_id>
Returns URL to topic wordcloud image.

---

🧭 Frontend–Backend Integration

- frontend/src/lib/api.js contains helper functions to call the Flask API.  
- Main analysis logic is handled in Analyzer.jsx.  
- Sentiment charts and summaries update dynamically when /analyze responds.

---

🪄 Key UI Components

| Component               | Purpose |
|--------------------------|---------|
| `NavBar.jsx`             | Top navigation bar |
| `Modal.jsx`              | Reusable modal wrapper |
| `AnalyzerInput.jsx`      | Text input box / upload UI |
| `SentimentDonut.jsx`     | Donut chart for sentiment distribution |
| `SentimentBars.jsx`      | Bar chart visualization |
| `SentimentHistogram.jsx` | Histogram sentiment view |
| `SentimentTrend.jsx`     | Trend line sentiment view |
| `SummaryTabs.jsx`        | Switch between summary types |
| `ReportDownload.jsx`     | Export current view to PDF |

---

🚀 Deployment Notes

- Run `npm run build` in `frontend` to generate `dist/` folder.  
- Flask serves built frontend from `frontend/dist`.  
- Recommended deployment:  
  - Serve both frontend and backend from a single Flask app (already configured in `ui_input.py`).  
  - Or host backend separately and set `VITE_API_BASE` accordingly.

---

📸 Optional Screenshots

You can create a `screenshots/` folder and add:  
- `landing.png` — Landing page  
- `analyzer.png` — Analysis UI  
- `report.png` — PDF export preview

Then embed with:
markdown
![Analyzer Screenshot](screenshots/analyzer.png)




- Built as part of Infosys Internship (Aug 2025).  
- Thanks to React, Vite, Flask, and open-source charting libraries.  
- Special thanks to the mentors and contributors of Narrative Nexus.


