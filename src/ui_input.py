from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from pathlib import Path
import json, os

# === project paths ===
ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "frontend" / "dist"
ASSETS_DIR = DIST / "assets"

# === Flask setup ===
app = Flask(__name__, static_folder=str(DIST), static_url_path="/static")
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})

print(">>> STATIC FOLDER:", app.static_folder)
print(">>> DIST Exists:", DIST.exists())
print(">>> ASSETS Exists:", ASSETS_DIR.exists())

# === Serve built assets ===
@app.route("/assets/<path:filename>")
def serve_assets(filename):
    target = ASSETS_DIR / filename
    if target.exists():
        return send_from_directory(str(ASSETS_DIR), filename, conditional=True)
    return jsonify({"error": f"Asset {filename} not found"}), 404

# === SPA routes (Landing, Analyzer, Docs, etc.) ===
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_spa(path):
    requested = DIST / path
    if path and requested.exists():
        return send_from_directory(str(DIST), path, conditional=True)
    index_file = DIST / "index.html"
    if index_file.exists():
        return send_from_directory(str(DIST), "index.html", conditional=True)
    return Response("<h1>SmartInsights</h1><p>Frontend build missing. Run npm run build.</p>", mimetype="text/html")

# === API: analyze ===
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json(force=True)
        text = data.get("text", "")
        if not text.strip():
            return jsonify({"ok": False, "error": "No text provided"}), 400

        # 👇 Replace this with your actual analysis pipeline
        result = {
            "ok": True,
            "summary_abstractive": f"Abstractive summary of: {text[:50]}...",
            "summary_extractive": f"Extractive summary of: {text[:50]}...",
            "summary_hybrid": f"Hybrid summary of: {text[:50]}...",
            "sentiment_label": "neutral",
            "sentiment_score": 0.0,
            "predicted_topic": None,
            "predicted_label": None,
            "wordcloud_url": "/assets/demo-wordcloud.png",
            "insights": ["Demo insight 1", "Demo insight 2"],
            "key_terms": ["demo", "insight", "smartinsights"],
            "key_uni_counts": {"demo": 2, "insight": 1},
            "rep_sentences": ["This is a demo sentence."],
            "sentence_scores": [0.0],
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# === API: build_report ===
@app.route("/build_report", methods=["POST"])
def build_report():
    try:
        data = request.get_json(force=True)
        report_path = DIST / "demo-report.html"
        report_path.write_text("<h1>Demo Report</h1><p>This is a test report.</p>", encoding="utf-8")
        return jsonify({"ok": True, "url": f"/static/demo-report.html"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# === Dataset dashboard demo endpoints ===
@app.route("/dataset/topics")
def dataset_topics():
    return jsonify({"ok": True, "topics": [{"id": 0, "label": "Demo Topic"}]})

@app.route("/dataset/topic_wordcloud/<int:topic_id>")
def dataset_wordcloud(topic_id):
    return jsonify({"ok": True, "url": "/assets/demo-wordcloud.png"})

# === Run server ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
