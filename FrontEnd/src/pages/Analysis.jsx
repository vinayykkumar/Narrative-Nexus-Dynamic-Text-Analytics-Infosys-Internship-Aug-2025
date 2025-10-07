import React, { useEffect, useRef, useState } from "react";
import { useOutletContext } from "react-router-dom";
import {
  CircleX,
  FilePlusIcon,
  Folder,
  Loader2,
  MessageSquare,
  NotepadText,
  Sparkles,
  Wand2,
  FileDown,
  Circle,
  Clock,
  CheckCircle,
} from "lucide-react";
import SentimentDistribution from "../components/charts/SentimentDistribution";
import TopicDistribution from "../components/charts/TopicDistribution";
import KeywordWordCloud from "../components/charts/KeywordWordCloud";
import TopicHighlights from "../components/charts/TopicHighlights";
import TopicConfidenceRadar from "../components/charts/TopicConfidenceRadar";

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

const formatPercentage = (value, fractionDigits = 1) => {
  if (typeof value === "number" && Number.isFinite(value)) {
    return `${(value * 100).toFixed(fractionDigits)}%`;
  }
  const numeric = Number(value);
  if (Number.isFinite(numeric)) {
    return `${(numeric * 100).toFixed(fractionDigits)}%`;
  }
  return "0%";
};

const Analysis = () => {
  const [file, setFile] = useState(null);
  const [textInput, setTextInput] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState("");
  const resultRef = useRef(null);
  const [selectedSentimentKey, setSelectedSentimentKey] = useState(null);
  const [selectedTopicKey, setSelectedTopicKey] = useState(null);
  const [selectedKeyword, setSelectedKeyword] = useState(null);
  const [submittedText, setSubmittedText] = useState("");
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [pdfError, setPdfError] = useState("");
  const [includeSentiment, setIncludeSentiment] = useState(true);

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
    setSelectedSentimentKey(null);
    setSelectedTopicKey(null);
    setSelectedKeyword(null);
    setSubmittedText("");
    setPdfError("");
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
      setSubmittedText("");
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
      setSubmittedText("");
    }
  };

  const handleSubmit = async () => {
    const trimmedText = textInput.trim();

    if (!file && !trimmedText) {
      setError("Please upload a file or enter text to analyze.");
      return;
    }

    setLoading(true);
    setAnalysis(null);
    setError("");
    setPdfError("");
    setCurrentStep(0);
    setSelectedSentimentKey(null);
    setSelectedTopicKey(null);
    setSelectedKeyword(null);
    setSubmittedText(file ? "" : trimmedText);

    const scrollTimeout = setTimeout(() => {
      resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 250);

    try {
      let response;

      if (file) {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("include_sentiment", includeSentiment ? "true" : "false");
        response = await fetch(
          `${API_BASE}/analyze-file?include_sentiment=${includeSentiment ? "true" : "false"}`,
          {
            method: "POST",
            body: formData,
          }
        );
      } else {
        response = await fetch(`${API_BASE}/analyze`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: trimmedText, include_sentiment: includeSentiment }),
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

      const computeTopicKey = (topic, index = 0) => {
        if (!topic) return null;
        if (topic.category_key) return topic.category_key;
        if (typeof topic.original_topic_id !== "undefined" && topic.original_topic_id !== null) {
          return `topic-${topic.original_topic_id}`;
        }
        return `topic-${index}`;
      };

      const sentimentDetails = result.sentiment ?? null;
      const hasSentimentData = Boolean(sentimentDetails && Object.keys(sentimentDetails).length > 0);
      const normalizedSentiment = hasSentimentData ? sentimentDetails : null;
      const normalizedResult = { ...result, sentiment: normalizedSentiment };

      setAnalysis(normalizedResult);
      setAnalysisData({
        extractiveSummary: result.extractive_summary ?? "",
        abstractiveSummary: result.abstractive_summary ?? "",
        topics: result.topics ?? [],
        topicDetails: result.topic_details ?? [],
        primaryTopic: result.primary_topic ?? null,
        keywordCloud: result.keyword_cloud ?? [],
        suggestions: result.suggestions ?? [],
      });
      setSentimentData(normalizedSentiment);
      setInsights(result.suggestions ?? []);
      setSelectedSentimentKey(normalizedSentiment?.overall?.label ?? null);
      const defaultTopicKey =
        computeTopicKey(result.primary_topic, 0) ??
        (Array.isArray(result.topics) ? computeTopicKey(result.topics[0], 0) : null);
      setSelectedTopicKey(defaultTopicKey);
      const firstKeyword =
        result.keyword_cloud_weighted?.[0]?.term ?? result.keyword_cloud?.[0] ?? null;
      setSelectedKeyword(firstKeyword);
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

  const handleDownloadPdf = async () => {
    if (!analysis) {
      setPdfError("Run an analysis before downloading a report.");
      return;
    }

    if (!file && !submittedText.trim()) {
      setPdfError("No source content available for the report. Re-run the analysis first.");
      return;
    }

    setPdfError("");
    setDownloadingPdf(true);

    try {
      let response;
      const defaultTitle =
        (analysis?.primary_topic?.label ?? analysis?.topics?.[0]?.label ?? "Insight Report").toString();

      if (file) {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("include_sentiment", includeSentiment ? "true" : "false");
        response = await fetch(`${API_BASE}/report/pdf/file`, {
          method: "POST",
          body: formData,
        });
      } else {
        response = await fetch(`${API_BASE}/report/pdf`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: submittedText,
            include_sentiment: includeSentiment,
            metadata: {
              title: defaultTitle,
              source: {
                type: "text-input",
              },
            },
          }),
        });
      }

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data?.detail ?? data?.error ?? "Failed to generate report");
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
      anchor.href = downloadUrl;
      anchor.download = `narrative-report-${timestamp}.pdf`;
      document.body.appendChild(anchor);
      anchor.click();
      document.body.removeChild(anchor);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      console.error("PDF download failed", err);
      setPdfError(err instanceof Error ? err.message : "Unable to download the PDF report.");
    } finally {
      setDownloadingPdf(false);
    }
  };

  const overallLabel =
  analysis?.sentiment?.overall?.label ?? analysis?.sentiment?.label ?? "--";
  const overallConfidence =
    analysis?.sentiment?.overall?.confidence ?? analysis?.sentiment?.score ?? null;
  const overallProbability = analysis?.sentiment?.overall?.probability ?? null;
  const sentimentDistribution = analysis?.sentiment?.distribution ?? {};
  const positiveShare = Number.isFinite(sentimentDistribution.positive)
    ? sentimentDistribution.positive
    : 0;
  const neutralShare = Number.isFinite(sentimentDistribution.neutral)
    ? sentimentDistribution.neutral
    : 0;
  const negativeShare = Number.isFinite(sentimentDistribution.negative)
    ? sentimentDistribution.negative
    : 0;

  const emojiMap = {
    positive: "😄",
    neutral: "😐",
    negative: "😟",
  };
  const overallEmoji = emojiMap[String(overallLabel).toLowerCase()] ?? "🤔";
  const overallConfidencePercent =
    overallConfidence != null ? formatPercentage(overallConfidence) : "--";
  const hasSourceForPdf = Boolean(file || submittedText.trim());

  const topics = Array.isArray(analysis?.topics) ? analysis.topics : [];
  const primaryTopic =
    analysis?.primary_topic ?? (topics.length > 0 ? topics[0] : null);
  const primaryTopicKey = primaryTopic
    ? `${primaryTopic.category_key ?? ""}:${primaryTopic.label ?? ""}`
    : null;
  const secondaryTopics = primaryTopicKey
    ? topics.filter((topic, index) => {
        const topicKey = `${topic?.category_key ?? ""}:${topic?.label ?? ""}`;
        if (analysis?.primary_topic) {
          return topicKey !== primaryTopicKey;
        }
        return index !== 0;
      })
    : topics;
  const combinedTopics = [primaryTopic, ...secondaryTopics].filter(Boolean);
  const visualTopics = combinedTopics.map((topic, index) => ({
    ...topic,
    __id:
      topic?.category_key ??
      `topic-${typeof topic?.original_topic_id !== "undefined" && topic?.original_topic_id !== null ? topic.original_topic_id : index}`,
  }));
  const keywordCloudWeighted = Array.isArray(analysis?.keyword_cloud_weighted)
    ? analysis.keyword_cloud_weighted
    : Array.isArray(analysis?.keyword_cloud)
    ? analysis.keyword_cloud.map((term, idx) => ({ term, score: 1 - idx * 0.05 }))
    : [];
  const selectedTopicDetails = visualTopics.find((topic) => topic.__id === selectedTopicKey);
const showSentimentSection = Boolean(analysis?.sentiment);

  return (
    <section className="relative min-h-screen bg-black bg-[url(/bg.svg)] text-white pt-24">
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
            Supports .txt, .csv, .pdf, .docx
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
              placeholder="Paste or type text to analyze."
              className="w-full min-h-[160px] bg-white/10 border border-white/20 rounded-lg p-4 text-sm text-gray-100 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary/70"
            />
          </div>

          <div className="mt-6 flex flex-wrap items-center justify-end gap-3">
            <div className="flex items-center gap-2 mr-auto">
              <label htmlFor="sentiment-toggle" className="text-sm text-gray-300 font-medium">
                <span className="mr-2">Include Sentiment Analysis</span>
              </label>
              <button
                id="sentiment-toggle"
                type="button"
                aria-pressed={includeSentiment}
                onClick={() => setIncludeSentiment((prev) => !prev)}
                className={`relative w-12 h-6 rounded-full transition-colors duration-200 focus:outline-none border border-white/20 ${includeSentiment ? "bg-primary" : "bg-gray-700"}`}
                style={{ minWidth: "48px" }}
              >
                <span
                  className={`absolute left-1 top-1 w-4 h-4 rounded-full bg-white transition-transform duration-200 ${includeSentiment ? "translate-x-6" : "translate-x-0"}`}
                  style={{ boxShadow: "0 0 6px #fff2" }}
                />
              </button>
            </div>
            <button
              type="button"
              onClick={resetState}
              className="px-6 py-2 border border-white/30 text-gray-300 rounded-full hover:bg-white/10 transition"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSubmit}
              disabled={loading}
              className="px-6 py-2 bg-primary text-white rounded-full hover:bg-indigo-600 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 cursor-pointer"
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin" />} {loading ? "Analyzing" : "Analyze"}
            </button>
          </div>

          {error && <p className="text-red-400 text-sm mt-4">{error}</p>}
        </div>

        {loading && (
  <div className="flex flex-col items-center justify-center bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/10 rounded-2xl py-10 px-8 space-y-6 shadow-xl animate-fade-in">
    {/* Spinning Loader with Glow */}
    <div className="relative">
      <Loader2 className="w-14 h-14 text-blue-400 animate-spin" />
      <div className="absolute inset-0 rounded-full bg-blue-400/20 blur-xl animate-pulse"></div>
    </div>

    {/* Title + Steps */}
    <div className="text-gray-200 text-center space-y-3">
      <p className="font-semibold text-lg tracking-wide animate-pulse flex items-center justify-center gap-2">
      Analyzing your text...
      </p>
      <ul className="space-y-2 text-sm text-left">
        {STEPS.map((step, idx) => (
          <li
            key={step}
            className={`flex items-center gap-2 transition ${
              idx === currentStep
                ? "text-blue-400 font-semibold"
                : idx < currentStep
                ? "text-green-400"
                : "text-gray-500"
            }`}
          >
            {idx < currentStep ? (
              <CheckCircle className="w-4 h-4" />
            ) : idx === currentStep ? (
              <Clock className="w-4 h-4 animate-pulse" />
            ) : (
              <Circle className="w-4 h-4" />
            )}
            {step}
          </li>
        ))}
      </ul>
    </div>

    {/* Progress Bar */}
    <div className="w-full max-w-md bg-gray-800 rounded-full h-3 overflow-hidden shadow-inner">
      <div
        className={`h-3 transition-all duration-500 bg-gradient-to-r ${
          currentStep + 1 === STEPS.length
            ? "from-green-400 to-green-500"
            : "from-blue-400 to-indigo-500"
        }`}
        style={{ width: `${((currentStep + 1) / STEPS.length) * 100}%` }}
      />
    </div>

    {/* Optional Step Counter */}
    <p className="text-xs text-gray-400 mt-2">
      Step {currentStep + 1} of {STEPS.length}
    </p>
  </div>
)}


        <div ref={resultRef} className="space-y-6">
          {analysis && !loading && (
            <div className="flex flex-col gap-6">
              <div className="p-5 bg-white/10 backdrop-blur rounded-xl border border-white/20 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div className="flex items-center gap-2 text-sm text-white/70">
                  <Sparkles className="w-4 h-4 text-primary" />
                  <span>Export the current analysis as a polished PDF report.</span>
                </div>
                <div className="flex flex-col items-start md:items-end gap-2">
                  {pdfError && <p className="text-xs text-red-400">{pdfError}</p>}
                  <button
                    type="button"
                    onClick={handleDownloadPdf}
                    disabled={!hasSourceForPdf || downloadingPdf}
                    className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-2 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {downloadingPdf ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <FileDown className="h-4 w-4" />
                    )}
                    {downloadingPdf ? "Preparing PDF..." : "Download report"}
                  </button>
                </div>
              </div>

              <div className="p-5 bg-white/10 backdrop-blur rounded-xl border border-white/20">
                <div className="flex items-center gap-2 mb-3">
                  <Wand2 className="w-5 h-5 text-primary" />
                  <h3 className="font-semibold text-primary text-lg">Topics</h3>
                </div>

                {primaryTopic || topics.length > 0 ? (
                  <div className="space-y-6">
                    {primaryTopic && (
                      <div className="p-4 rounded-lg bg-gradient-to-tr from-indigo-500/20 via-black to-purple-500/10 border border-white/20 text-white">
                        <div className="text-xs uppercase tracking-[0.2em] text-white/70 mb-2">
                          Primary Topic
                        </div>
                        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                          <div>
                            <div className="text-2xl font-bold">
                              {primaryTopic?.label ?? "Key Theme"}
                            </div>
                            <p className="text-sm text-white/80 mt-2 max-w-2xl">
                              {Array.isArray(primaryTopic?.keywords) && primaryTopic.keywords.length > 0
                                ? `Key signals: ${primaryTopic.keywords.slice(0, 8).join(", ")}`
                                : "This theme captures the dominant narrative discovered within the text."}
                            </p>
                          </div>
                          <div className="text-center md:text-right">
                            <div className="text-lg font-semibold text-primary">
                              {formatPercentage(
                                Number.isFinite(primaryTopic?.share)
                                  ? Math.min(Math.max(primaryTopic.share, 0), 1)
                                  : Math.min(Math.max(Number(primaryTopic?.confidence ?? 0), 0), 1)
                              )}
                            </div>
                            <p className="text-xs text-white/70">Estimated relevance</p>
                          </div>
                        </div>
                      </div>
                    )}

                    {secondaryTopics.length > 0 && (
                      <div className="space-y-6">
                        <div className="flex flex-col gap-5 xl:flex-row">
                          <div className="xl:w-7/12 w-full space-y-5">
                            <div className="rounded-2xl border border-white/10 bg-gradient-to-tr from-indigo-500/20 via-black to-purple-500/10 p-4">
                              <div className="flex items-center justify-between mb-2">
                                <h4 className="text-sm uppercase tracking-wide text-white/70">
                                  Theme Distribution
                                </h4>
                                <span className="text-xs text-white/50">
                                  {secondaryTopics.length} theme{secondaryTopics.length === 1 ? "" : "s"}
                                </span>
                              </div>
                              <TopicDistribution
                                topics={visualTopics}
                                selectedTopicKey={selectedTopicKey}
                                onTopicSelect={(key) => {
                                  setSelectedTopicKey((prev) => (prev === key ? null : key));
                                  const match = visualTopics.find((topic) => topic.__id === key);
                                  if (match?.keywords && match.keywords.length > 0) {
                                    setSelectedKeyword(match.keywords[0]);
                                  } else {
                                    setSelectedKeyword(null);
                                  }
                                }}
                              />
                            </div>

                            <TopicConfidenceRadar topics={visualTopics} />
                          </div>

                          <div className="xl:w-5/12 w-full space-y-4">
                            <div className="flex items-center justify-between">
                              <h4 className="text-sm uppercase tracking-wide text-white/70">
                                Spotlight Themes
                              </h4>
                              <span className="text-xs text-white/50">Tap to drill in</span>
                            </div>
                            <TopicHighlights
                              topics={visualTopics}
                              selectedTopicKey={selectedTopicKey}
                              onTopicSelect={(key) => {
                                setSelectedTopicKey((prev) => (prev === key ? null : key));
                                const match = visualTopics.find((topic) => topic.__id === key);
                                if (match?.keywords && match.keywords.length > 0) {
                                  setSelectedKeyword(match.keywords[0]);
                                } else {
                                  setSelectedKeyword(null);
                                }
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-white/70 text-sm">
                    No dominant topics were detected. Try analyzing a longer passage for richer insights.
                  </p>
                )}
              </div>

              {showSentimentSection && (
                <div className="p-5 bg-white/10 backdrop-blur rounded-xl border border-white/20 flex flex-col gap-5">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-primary" />
                  <h3 className="font-semibold text-primary text-lg">Sentiment Analysis</h3>
                </div>

                <div className="grid gap-6 xl:grid-cols-[minmax(0,260px)_1fr]">
                  <div className="space-y-4">
                    <div className="rounded-2xl border border-white/15 bg-black/40 px-5 py-6 text-white">
                      <p className="text-[11px] uppercase tracking-[0.35em] text-white/50">Dominant sentiment</p>
                      <div className="mt-4 flex items-center gap-3">
                        <span className="text-4xl" role="img" aria-label="overall sentiment emoji">
                          {overallEmoji}
                        </span>
                        <div>
                          <p className="text-2xl font-semibold uppercase leading-tight text-white">
                            {overallLabel || "--"}
                          </p>
                          <p className="text-sm text-white/60">{overallConfidencePercent} confidence</p>
                          {overallProbability != null && (
                            <p className="text-xs text-white/50 mt-1">
                              Positive probability {formatPercentage(overallProbability)}
                            </p>
                          )}
                        </div>
                      </div>

                      <div className="mt-6 space-y-2 text-sm text-white/70">
                        <div className="flex items-center justify-between border-b border-white/5 pb-2">
                          <span className="flex items-center gap-2 text-white/60">
                            <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" /> Positive
                          </span>
                          <span className="font-medium text-white">{formatPercentage(positiveShare)}</span>
                        </div>
                        <div className="flex items-center justify-between border-b border-white/5 pb-2">
                          <span className="flex items-center gap-2 text-white/60">
                            <span className="h-2.5 w-2.5 rounded-full bg-amber-400" /> Neutral
                          </span>
                          <span className="font-medium text-white">{formatPercentage(neutralShare)}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="flex items-center gap-2 text-white/60">
                            <span className="h-2.5 w-2.5 rounded-full bg-rose-400" /> Negative
                          </span>
                          <span className="font-medium text-white">{formatPercentage(negativeShare)}</span>
                        </div>
                      </div>
                    </div>

                    <div className="rounded-2xl border border-white/10 bg-white/5 px-5 py-4 text-sm text-white/70">
                      <p className="text-[11px] uppercase tracking-[0.35em] text-white/50 mb-3">Model breakdown</p>
                      <ul className="space-y-2">
                        <li className="flex items-center justify-between">
                          <span className="text-white/60">Rule-based</span>
                          <span className="font-medium text-white">
                            {formatProbability(analysis.sentiment?.rule_based?.polarity)} polarity · {formatProbability(analysis.sentiment?.rule_based?.subjectivity)} subjectivity
                          </span>
                        </li>
                        <li className="flex items-center justify-between">
                          <span className="text-white/60">ML model</span>
                          <span className="font-medium text-white">
                            {formatProbability(analysis.sentiment?.ml?.probability)} · {analysis.sentiment?.ml?.label ?? "--"}
                          </span>
                        </li>
                        <li className="flex items-center justify-between">
                          <span className="text-white/60">LSTM</span>
                          <span className="font-medium text-white">
                            {formatProbability(analysis.sentiment?.dl?.probability)} · {analysis.sentiment?.dl?.label ?? "--"}
                          </span>
                        </li>
                        <li className="flex items-center justify-between">
                          <span className="text-white/60">Transformer</span>
                          <span className="font-medium text-white">
                            {formatProbability(analysis.sentiment?.transformer?.probability)} · {analysis.sentiment?.transformer?.label ?? "--"}
                          </span>
                        </li>
                      </ul>
                    </div>
                  </div>

                  <div className="rounded-2xl border border-white/10 bg-slate-900/40 p-5">
                    <h4 className="text-sm uppercase tracking-[0.35em] text-white/50 text-center mb-4">
                      Sentiment distribution
                    </h4>
                    <SentimentDistribution
                      distribution={sentimentDistribution}
                      overallLabel={overallLabel}
                      selectedKey={selectedSentimentKey}
                      onSegmentSelect={setSelectedSentimentKey}
                    />
                  </div>
                </div>
              </div>
              )}

              {(analysis.extractive_summary || analysis.abstractive_summary) && (
                <div className="p-5 bg-white/10 backdrop-blur rounded-xl border border-white/20">
                  <div className="flex items-center gap-2 mb-3">
                    <NotepadText className="w-5 h-5 text-primary" />
                    <h3 className="font-semibold text-primary text-lg">Summarization</h3>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {analysis.extractive_summary && (
                      <div className="p-5 bg-gradient-to-tr from-indigo-500/20 via-black to-purple-500/10 border border-primary/30 text-white rounded-xl shadow-md">
                        <h3 className="font-semibold text-indigo-600 text-lg mb-3">
                          Extractive Summary
                        </h3>
                        <p className="text-gray-200 text-sm whitespace-pre-line">
                          {analysis.extractive_summary}
                        </p>
                      </div>
                    )}

                    {analysis.abstractive_summary && (
                      <div className="p-5 bg-gradient-to-tr from-indigo-500/20 via-black to-purple-500/10 border border-purple-400/30 text-white rounded-xl shadow-md ">
                        <h3 className="font-semibold text-indigo-600 text-lg mb-3">
                          Abstractive Summary
                        </h3>
                        <p className="text-gray-200 text-sm whitespace-pre-line">
                          {analysis.abstractive_summary}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {keywordCloudWeighted.length > 0 && (
                <div className="p-5 bg-white/10 backdrop-blur rounded-xl border border-white/20 space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-primary text-lg">Keyword Cloud</h3>
                    {selectedTopicDetails?.label && (
                      <span className="text-xs text-white/70">
                        Highlighting signals for {selectedTopicDetails.label}
                      </span>
                    )}
                  </div>
                  <KeywordWordCloud
                    keywords={keywordCloudWeighted}
                    selectedKeyword={selectedKeyword}
                    onKeywordSelect={(term) =>
                      setSelectedKeyword((prev) => (prev === term ? null : term))
                    }
                  />
                </div>
              )}

              {analysis.suggestions && analysis.suggestions.length > 0 && (
  <div className="p-6 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-2xl border border-white/20 shadow-lg transition-transform">
    <h3 className="font-bold text-primary text-xl mb-4 flex items-center gap-2">
      💡 Suggestions
    </h3>
    <ul className="space-y-3">
      {analysis.suggestions.map((suggestion, idx) => (
        <li
          key={`${suggestion}-${idx}`}
          className="flex items-start gap-3 p-3 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition"
        >
          <CheckCircle className="w-4 h-4 text-green-600 mt-1" />
          <span className="text-gray-200 text-sm leading-relaxed">{suggestion}</span>
        </li>
      ))}
    </ul>
  </div>
)}

            </div>
          )}

          {!analysis && !loading && (
            <div className="p-6 bg-white/5 backdrop-blur border border-white/10 rounded-xl text-sm text-gray-400 flex items-center gap-3">
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