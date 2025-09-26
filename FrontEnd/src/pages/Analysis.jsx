import React, { useEffect, useRef, useState } from "react";
import { useOutletContext } from "react-router-dom";
import {
  CircleX,
  FilePlusIcon,
  Folder,
  Loader2,
  MessageSquare,
  Sparkles,
  Wand2,
} from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";
const STEPS = [
  "Cleaning text",
  "Extracting features",
  "Running analysis",
  "Generating results",
];
const ALLOWED_TYPES = [
  "text/plain",
  "text/csv",
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
];

const formatProbability = (value) => {
  if (typeof value === "number") return value.toFixed(2);
  const num = Number(value);
  return Number.isFinite(num) ? num.toFixed(2) : "--";
};

const Analysis = () => {
  const [file, setFile] = useState(null);
  const [textInput, setTextInput] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState("");
  const resultRef = useRef(null);

  const {
    setAnalysisData = () => {},
    setSentimentData = () => {},
    setInsights = () => {},
  } = useOutletContext() || {};

  useEffect(() => {
    if (!loading) return undefined;

    setCurrentStep(0);
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < STEPS.length - 1 ? prev + 1 : prev));
    }, 1500);

    return () => clearInterval(interval);
  }, [loading]);

  useEffect(() => {
    if (!analysis || loading) return;

    const timeout = setTimeout(() => {
      resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 300);

    return () => clearTimeout(timeout);
  }, [analysis, loading]);

  const resetState = () => {
    setFile(null);
    setTextInput("");
    setAnalysis(null);
    setError("");
    setCurrentStep(0);
  };

  const validateFile = (selectedFile) => {
    if (!selectedFile) return false;
    if (!ALLOWED_TYPES.includes(selectedFile.type)) {
      setError("Unsupported file type. Upload .txt, .csv, .pdf, or .docx only.");
      return false;
    }
    setError("");
    return true;
  };

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];
    if (!selectedFile) return;

    if (validateFile(selectedFile)) {
      setFile(selectedFile);
      setTextInput("");
    } else {
      event.target.value = "";
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files?.[0];
    if (!droppedFile) return;

    if (validateFile(droppedFile)) {
      setFile(droppedFile);
      setTextInput("");
    }
  };

  const handleSubmit = async () => {
    if (!file && !textInput.trim()) {
      setError("Please upload a file or enter text to analyze.");
      return;
    }

    setLoading(true);
    setAnalysis(null);
    setError("");
    setCurrentStep(0);

    const scrollTimeout = setTimeout(() => {
      resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 250);

    try {
      let response;

      if (file) {
        const formData = new FormData();
        formData.append("file", file);
        response = await fetch(`${API_BASE}/analyze-file`, {
          method: "POST",
          body: formData,
        });
      } else {
        response = await fetch(`${API_BASE}/analyze`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: textInput }),
        });
      }

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const result = await response.json();
      if (result?.error) {
        setError(result.error);
        return;
      }

      setAnalysis(result);
      setAnalysisData({
        extractiveSummary: result.extractive_summary ?? "",
        abstractiveSummary: result.abstractive_summary ?? "",
        topics: result.topics ?? [],
        keywordCloud: result.keyword_cloud ?? [],
        suggestions: result.suggestions ?? [],
      });
      setSentimentData(result.sentiment ?? null);
      setInsights(result.suggestions ?? []);
    } catch (err) {
      console.error("Analysis error", err);
      setError("Something went wrong while analyzing the data. Please try again.");
    } finally {
      clearTimeout(scrollTimeout);
      setLoading(false);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
  };

  const overallLabel =
    analysis?.sentiment?.overall?.label ?? analysis?.sentiment?.label ?? "--";
  const overallConfidence =
    analysis?.sentiment?.overall?.confidence ?? analysis?.sentiment?.score ?? null;

  return (
    <section className="relative min-h-screen bg-black bg-[url(/bg.svg)] text-white pt-20">
      <h1 className="text-3xl md:text-4xl font-semibold text-primary text-center">
        Text Analysis Platform
      </h1>

      <div className="max-w-6xl pt-8 mx-auto px-6 flex flex-col gap-8 pb-16">
        <div className="w-full p-6 bg-white/10 backdrop-blur rounded-lg border border-white/20 shadow-md">
          <div className="flex items-center justify-center w-12 h-12 bg-white/20 rounded-full">
            <Folder className="text-white w-5 h-5" />
          </div>
          <h2 className="text-2xl font-semibold text-white mt-4">
            Upload a File or Paste Text
          </h2>
          <p className="text-gray-300 mt-1 text-sm">
            Supports: .txt, .csv, .pdf, .docx
          </p>

          <label
            htmlFor="fileInput"
            onDrop={handleDrop}
            onDragOver={(event) => event.preventDefault()}
            className="border-2 border-dotted border-white/30 p-6 mt-4 flex flex-col items-center gap-3 cursor-pointer hover:border-primary transition-colors rounded-lg"
          >
            <FilePlusIcon className="text-primary w-6 h-6" />
            <p className="text-gray-300 text-sm">Drag & drop your file here</p>
            <p className="text-gray-300 text-sm">
              Or <span className="text-primary underline">click to select</span>
            </p>
            <input
              id="fileInput"
              type="file"
              accept={ALLOWED_TYPES.join(",")}
              className="hidden"
              onChange={handleFileChange}
            />
          </label>

          {file && (
            <div className="mt-4 flex items-center justify-between bg-white/10 border border-white/20 rounded-lg px-4 py-3">
              <div className="flex flex-col text-sm text-gray-200">
                <span className="font-medium text-white">{file.name}</span>
                <span className="text-gray-400">{(file.size / 1024).toFixed(1)} KB</span>
              </div>
              <button
                type="button"
                onClick={handleRemoveFile}
                className="text-red-400 hover:text-red-200"
                aria-label="Remove file"
              >
                <CircleX className="w-5 h-5" />
              </button>
            </div>
          )}

          <div className="mt-6">
            <div className="flex items-center gap-2 text-sm text-gray-300 mb-2">
              <MessageSquare className="w-4 h-4" />
              <span>Or paste text directly</span>
            </div>
            <textarea
              value={textInput}
              onChange={(event) => setTextInput(event.target.value)}
              placeholder="paste or type text to analyze..."
              className="w-full min-h-[160px] bg-white/10 border border-white/20 rounded-lg p-4 text-sm text-gray-100 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary/70"
            />
          </div>

          <div className="mt-6 flex flex-wrap justify-end gap-3">
            <button
              type="button"
              onClick={resetState}
              className="px-6 py-2 border border-white/30 text-gray-300 rounded-full hover:bg-white/10 transition"
            >
              Reset
            </button>
            <button
              type="button"
              onClick={handleSubmit}
              disabled={loading}
              className="px-6 py-2 bg-primary text-white rounded-full hover:bg-indigo-600 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin" />} {loading ? "Analyzing..." : "Analyze"}
            </button>
          </div>

          {error && <p className="text-red-400 text-sm mt-4">{error}</p>}
        </div>

        {loading && (
          <div className="flex flex-col items-center justify-center bg-white/10 backdrop-blur border border-white/20 rounded-xl py-10 px-6 space-y-5">
            <Loader2 className="w-12 h-12 text-primary animate-spin" />
            <div className="text-gray-300 text-center space-y-2">
              <p className="font-medium">Analyzing data...</p>
              <ul className="list-disc list-inside text-left space-y-1 text-gray-400">
                {STEPS.map((step, idx) => (
                  <li
                    key={step}
                    className={
                      idx === currentStep
                        ? "text-blue-400 font-semibold"
                        : idx < currentStep
                        ? "text-green-400"
                        : "text-gray-500"
                    }
                  >
                    {step}
                  </li>
                ))}
              </ul>
            </div>
            <div className="w-full max-w-md bg-gray-700 rounded-full h-2 overflow-hidden">
              <div
                className={`h-2 transition-all duration-500 ${
                  currentStep + 1 === STEPS.length ? "bg-green-500" : "bg-blue-500"
                }`}
                style={{ width: `${((currentStep + 1) / STEPS.length) * 100}%` }}
              />
            </div>
          </div>
        )}

        <div ref={resultRef} className="space-y-6">
          {analysis && !loading && (
            <div className="flex flex-col gap-6">
              <div className="p-5 bg-white/10 backdrop-blur rounded-xl border border-white/20">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles className="w-5 h-5 text-primary" />
                  <h3 className="font-semibold text-primary text-lg">Sentiment</h3>
                </div>
                <p className="text-gray-300 text-sm">
                  {overallLabel.toUpperCase()} {overallConfidence != null ? `(${formatProbability(overallConfidence)})` : ""}
                </p>
                <div className="text-xs text-gray-400 space-y-1 mt-3">
                  <p>
                    Rule-based polarity {formatProbability(analysis.sentiment?.rule_based?.polarity)}, subjectivity {formatProbability(analysis.sentiment?.rule_based?.subjectivity)}
                  </p>
                  <p>
                    ML probability: {formatProbability(analysis.sentiment?.ml?.probability)} ({analysis.sentiment?.ml?.label ?? "--"})
                  </p>
                  <p>
                    LSTM probability: {formatProbability(analysis.sentiment?.dl?.probability)} ({analysis.sentiment?.dl?.label ?? "--"})
                  </p>
                  <p>
                    Transformer probability: {formatProbability(analysis.sentiment?.transformer?.probability)} ({analysis.sentiment?.transformer?.label ?? "--"})
                  </p>
                </div>
              </div>

              <div className="p-5 bg-white/10 backdrop-blur rounded-xl border border-white/20">
                <div className="flex items-center gap-2 mb-3">
                  <Wand2 className="w-5 h-5 text-primary" />
                  <h3 className="font-semibold text-primary text-lg">Topics</h3>
                </div>
                <p className="text-gray-300 text-sm">
                  {analysis.topics && analysis.topics.length > 0
                    ? analysis.topics
                        .map(
                          (topic) =>
                            `Topic ${(topic.topic_id ?? topic.id ?? 0) + 1}: ${(topic.keywords || [])
                              .slice(0, 6)
                              .join(", ")} (score ${formatProbability(topic.score)})`
                        )
                        .join(" | ")
                    : "No topics available."}
                </p>
              </div>

              {analysis.extractive_summary && (
                <div className="p-5 bg-white/10 backdrop-blur rounded-xl border border-white/20">
                  <h3 className="font-semibold text-primary text-lg mb-3">Extractive Summary</h3>
                  <p className="text-gray-300 text-sm whitespace-pre-line">
                    {analysis.extractive_summary}
                  </p>
                </div>
              )}

              {analysis.abstractive_summary && (
                <div className="p-5 bg-white/10 backdrop-blur rounded-xl border border-white/20">
                  <h3 className="font-semibold text-primary text-lg mb-3">Abstractive Summary</h3>
                  <p className="text-gray-300 text-sm whitespace-pre-line">
                    {analysis.abstractive_summary}
                  </p>
                </div>
              )}

              {analysis.keyword_cloud && analysis.keyword_cloud.length > 0 && (
                <div className="p-5 bg-white/10 backdrop-blur rounded-xl border border-white/20">
                  <h3 className="font-semibold text-primary text-lg mb-3">Keyword Cloud</h3>
                  <div className="flex flex-wrap gap-2">
                    {analysis.keyword_cloud.slice(0, 20).map((word, idx) => (
                      <span
                        key={`${word}-${idx}`}
                        className="bg-indigo-100/90 text-indigo-700 px-3 py-1 rounded-full text-xs"
                      >
                        {word}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {analysis.suggestions && analysis.suggestions.length > 0 && (
                <div className="p-5 bg-white/10 backdrop-blur rounded-xl border border-white/20">
                  <h3 className="font-semibold text-primary text-lg mb-3">Suggestions</h3>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-1">
                    {analysis.suggestions.map((suggestion, idx) => (
                      <li key={`${suggestion}-${idx}`}>{suggestion}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {!analysis && !loading && (
            <div className="p-6 bg-white/10 backdrop-blur border border-white/20 rounded-xl text-sm text-gray-400 flex items-center gap-3">
              <Sparkles className="w-5 h-5 text-primary" />
              <p>
                Submit text or upload a document to reveal sentiment, topic insights, summaries, and tailored suggestions.
              </p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default Analysis;