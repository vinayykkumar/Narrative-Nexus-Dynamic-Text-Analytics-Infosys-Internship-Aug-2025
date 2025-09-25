import React, { useState, useEffect, useRef } from "react";
import { CircleX, FilePlusIcon, Folder } from "lucide-react";

const Analysis = () => {
  const [file, setFile] = useState(null);
  const [textInput, setTextInput] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  // 🔹 Loader steps
  const steps = [
    "Cleaning text",
    "Extracting features",
    "Running analysis",
    "Generating results",
  ];
  const [currentStep, setCurrentStep] = useState(0);

  // 🔹 Ref for scrolling
  const resultRef = useRef(null);

  useEffect(() => {
    if (loading) {
      setCurrentStep(0);
      const interval = setInterval(() => {
        setCurrentStep((prev) =>
          prev < steps.length - 1 ? prev + 1 : prev
        );
      }, 1500);
      return () => clearInterval(interval);
    }
  }, [loading]);

  // 🔹 Scroll down again when results are ready
  useEffect(() => {
    if (analysis && !loading) {
      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 300);
    }
  }, [analysis, loading]);

  const allowedTypes = [
    "text/plain",
    "text/csv",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  ];

  const validateFile = (selectedFile) => {
    if (!selectedFile) return false;
    if (!allowedTypes.includes(selectedFile.type)) {
      alert("Unsupported file type! Upload .txt, .csv, .pdf, or .docx only.");
      return false;
    }
    return true;
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (validateFile(selectedFile)) {
      setFile(selectedFile);
      setTextInput("");
    } else e.target.value = "";
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (validateFile(droppedFile)) {
      setFile(droppedFile);
      setTextInput("");
    }
  };

  const handleSubmit = async () => {
    if (!file && !textInput)
      return alert("Please upload a file or enter text!");

    setLoading(true);
    setAnalysis(null);

    // 🔹 Scroll to loader immediately after clicking Analyze
    setTimeout(() => {
      resultRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 300);

    try {
      let response;
      if (file) {
        const formData = new FormData();
        formData.append("file", file);

        response = await fetch("http://127.0.0.1:8000/api/analyze-file", {
          method: "POST",
          body: formData,
        });
      } else {
        response = await fetch("http://127.0.0.1:8000/api/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: textInput }),
        });
      }

      const result = await response.json();
      setAnalysis(result);
    } catch (error) {
      console.error("Error:", error);
      alert("Error analyzing data");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="relative min-h-screen bg-black bg-[url(/bg.svg)] text-white pt-24">
      <h1 className="text-3xl md:text-4xl font-semibold text-primary text-center">
        Text Analysis Platform
      </h1>

      <div className="max-w-6xl pt-8 mx-auto px-6 flex flex-col gap-8 pb-12">
        {/* Upload & Text Input */}
        <div className="w-full p-6 bg-white/10 backdrop-blur rounded-lg border border-white/20 shadow-md">
          <div className="flex items-center justify-center w-12 h-12 bg-white/20 rounded-full">
            <Folder className="text-white w-5 h-5" />
          </div>
          <h2 className="text-2xl font-semibold text-white mt-3">
            Upload a File or Paste Text
          </h2>
          <p className="text-gray-300 mt-1 text-sm">
            Supports: .txt, .csv, .pdf, .docx
          </p>

          {/* File Upload */}
          <label
            htmlFor="fileInput"
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
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
              className="hidden"
              accept=".txt,.csv,.pdf,.docx"
              onChange={handleFileChange}
            />
          </label>
          <p className="pt-4 text-center">OR</p>

          {/* Text Input */}
          <textarea
            placeholder="type/paste your text here..."
            className="w-full mt-4 p-3 rounded-lg bg-white/10 border border-white/30 text-white placeholder-gray-400 focus:outline-none focus:border-primary resize-none"
            rows={4}
            value={textInput}
            onChange={(e) => {
              setTextInput(e.target.value);
              setFile(null);
            }}
          />

          {/* File Preview */}
          {file && (
            <div className="mt-4 px-4 py-2 bg-white/20 rounded-lg flex items-center justify-between">
              <div>
                <p className="font-medium text-white">{file.name}</p>
                <p className="text-xs text-gray-300">
                  {(file.size / 1024).toFixed(2)} KB
                </p>
              </div>
              <button
                onClick={() => setFile(null)}
                className="text-red-500 hover:text-red-700"
              >
                <CircleX className="w-5 h-5" />
              </button>
            </div>
          )}

          {/* Buttons */}
          <div className="mt-6 flex justify-end gap-3">
            <button
              onClick={() => {
                setFile(null);
                setTextInput("");
                setAnalysis(null);
              }}
              className="px-6 py-2 border border-white/30 text-gray-300 rounded-full hover:bg-white/10 transition"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={loading || (!file && !textInput)}
              className="px-6 py-2 bg-primary text-white rounded-full hover:bg-indigo-600 transition disabled:opacity-50"
            >
              {loading ? "Analyzing..." : "Analyze"}
            </button>
          </div>
        </div>

        {/* Results + Loader section (scroll target) */}
        <div ref={resultRef}>
          {/* Analysis Results */}
          {analysis && !loading && (
            <div className="flex flex-col gap-6">
              {/* Text Data */}
              <div className="p-5 bg-white/10 rounded-xl border border-white/20">
                <h3 className="font-semibold text-primary text-lg mb-3">
                  Text Data
                </h3>
                <p className="text-gray-300 text-sm">
                  {textInput || file?.name}
                </p>
              </div>

              {/* Topics */}
              {analysis.topics && (
                <div className="p-5 bg-white/10 rounded-xl border border-white/20">
                  <h3 className="font-semibold text-primary text-lg mb-3">
                    Topic Modeling
                  </h3>
                  <p className="text-gray-300 text-sm">
                    {analysis.topics
                      ?.map(
                        (t) =>
                          `${t.keywords.join(", ")} (${t.score.toFixed(2)})`
                      )
                      .join(" | ")}
                  </p>
                </div>
              )}

              {/* Sentiment */}
              {analysis.sentiment && (
                <div className="p-5 bg-white/10 rounded-xl border border-white/20">
                  <h3 className="font-semibold text-primary text-lg mb-3">
                    Sentiment Analysis
                  </h3>
                  <p className="text-gray-300 text-sm">
                    {analysis.sentiment.label} (
                    {analysis.sentiment.score.toFixed(2)})
                  </p>
                </div>
              )}

              {/* Summarization */}
              {(analysis.extractive_summary || analysis.abstractive_summary) && (
                <div className="p-5 bg-white/10 rounded-xl border border-white/20">
                  <h3 className="font-semibold text-primary text-lg mb-3">
                    Summarization
                  </h3>
                  {analysis.extractive_summary && (
                    <p className="text-gray-300 text-sm mb-2">
                      <strong>Extractive:</strong>{" "}
                      {analysis.extractive_summary}
                    </p>
                  )}
                  {analysis.abstractive_summary && (
                    <p className="text-gray-300 text-sm">
                      <strong>Abstractive:</strong>{" "}
                      {analysis.abstractive_summary}
                    </p>
                  )}
                </div>
              )}

              {/* Suggestions */}
              {analysis.suggestions && analysis.suggestions.length > 0 && (
                <div className="p-5 bg-white/10 rounded-xl border border-white/20">
                  <h3 className="font-semibold text-primary text-lg mb-3">
                    Suggestions / Visualization
                  </h3>
                  <p className="text-gray-300 text-sm">
                    {analysis.suggestions.join(" ")}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Loader with steps + progress bar */}
          {loading && (
            <div className="flex flex-col items-center mt-6 space-y-4">
              {/* Spinner */}
              <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-400"></div>

              {/* Steps */}
              <div className="text-gray-300 text-sm space-y-2 text-center">
                <p className="font-medium">Analyzing data...</p>
                <ul className="list-disc list-inside space-y-1 text-gray-400 text-left">
                  {steps.map((step, idx) => (
                    <li
                      key={idx}
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

              {/* Progress bar */}
              <div className="w-full max-w-md bg-gray-700 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-2 transition-all duration-500 ${
                    currentStep + 1 === steps.length
                      ? "bg-green-500"
                      : "bg-blue-500"
                  }`}
                  style={{
                    width: `${((currentStep + 1) / steps.length) * 100}%`,
                  }}
                ></div>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default Analysis;
