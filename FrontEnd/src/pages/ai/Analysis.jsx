import React, { useState } from "react";
import { CircleX, FilePlusIcon, Folder } from "lucide-react";

const Analysis = () => {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [dragActive, setDragActive] = useState(false);

  const allowedTypes = [
    "text/plain",
    "text/csv",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  ];

  // Validate and set file
  const validateFile = (selectedFile) => {
    if (!selectedFile) return false;
    if (!allowedTypes.includes(selectedFile.type)) {
      alert(
        "Unsupported file type! Please upload .txt, .csv, .pdf, or .docx files only."
      );
      return false;
    }
    return true;
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (validateFile(selectedFile)) setFile(selectedFile);
    else e.target.value = "";
  };

  // Drag & drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    setDragActive(true);
  };
  const handleDragLeave = () => setDragActive(false);
  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    const droppedFile = e.dataTransfer.files[0];
    if (validateFile(droppedFile)) setFile(droppedFile);
  };

  // Submit file → backend
  const handleSubmit = async () => {
    if (!file) return alert("Please upload a file first!");
    setLoading(true);
    setAnalysis(null);
    setStatus("Extracting text from file...");

    try {
      const formData = new FormData();
      formData.append("file", file);

      setStatus("Extracting text from file...");
      const response = await fetch("http://127.0.0.1:8000/analyze-file", {
        method: "POST",
        body: formData,
      });

      setStatus("Running analysis...");
      const result = await response.json();
      setAnalysis(result);
      setStatus("✅ Analysis completed!");
    } catch (error) {
      console.error("Error:", error);
      setStatus("❌ Error analyzing file.");
      alert("Error analyzing file");
    } finally {
      setLoading(false);
      setTimeout(() => setStatus(""), 3000); // clear after 3s
    }
  };

  return (
    <section className="py-2">
      <div className="max-w-6xl mx-auto px-6 grid md:grid-cols-2 gap-10">
        {/* Upload Section */}
        <div className="w-full p-6 bg-white/70 rounded-lg border border-gray-500/30 shadow-md">
          <div className="flex items-center justify-center w-11 h-11 bg-gray-500/10 rounded-full">
            <Folder className="text-primary w-5 h-5" />
          </div>
          <h2 className="text-2xl text-gray-800 font-medium mt-3">
            Upload a file
          </h2>
          <p className="text-gray-700/80 mt-1">
            Attach a .txt, .csv, .pdf, or .docx file
          </p>

          {/* Drag & Drop Zone */}
          <label
            htmlFor="fileInput"
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dotted p-8 mt-6 flex flex-col items-center gap-4 cursor-pointer transition ${
              dragActive ? "border-blue-500 bg-blue-50/30" : "border-gray-400"
            }`}
          >
            <FilePlusIcon className="text-primary" />
            <p className="text-gray-500">Drag & Drop your file here</p>
            <p className="text-gray-500">
              Or <span className="text-primary underline">click here</span> to
              select
            </p>
            <p className="text-gray-500">Supports: .txt, .csv, .pdf, .docx</p>
            <input
              id="fileInput"
              type="file"
              className="hidden"
              accept=".txt,.csv,.pdf,.docx"
              onChange={handleFileChange}
            />
          </label>

          {/* File Preview */}
          {file && (
            <div className="mt-4 px-4 py-2 rounded-xl flex items-center justify-between bg-blue-100">
              <div>
                <p className="text-gray-700 font-medium">{file.name}</p>
                <p className="text-gray-400 text-xs">
                  {(file.size / 1024).toFixed(2)} KB
                </p>
              </div>
              <button
                onClick={() => setFile(null)}
                className="text-red-500 hover:text-red-700 cursor-pointer"
              >
                <CircleX className="w-5 h-5" />
              </button>
            </div>
          )}

          {/* Buttons + Status */}
          <div className="mt-6 flex flex-col items-end gap-2">
            <div className="flex gap-4">
              <button
                type="button"
                className="px-9 py-2 border border-gray-400 hover:bg-gray-100 transition-all text-gray-600 rounded-full"
                onClick={() => {
                  setFile(null);
                  setAnalysis(null);
                  setStatus("");
                }}
              >
                Cancel
              </button>
              <button
                type="button"
                className="px-6 py-2 bg-primary hover:bg-indigo-600 transition-all text-white rounded-full"
                onClick={handleSubmit}
                disabled={loading || !file}
              >
                {loading ? "Analyzing..." : "Analyze"}
              </button>
            </div>

            {/* Status & Spinner */}
            {status && (
              <div className="flex items-center gap-2 text-blue-600 text-sm">
                {loading && (
                  <svg
                    className="animate-spin h-4 w-4 text-blue-600"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                    ></path>
                  </svg>
                )}
                <span>{status}</span>
              </div>
            )}
          </div>
        </div>

        {/* Analysis Results */}
        <div className="w-full p-6 bg-white/70 rounded-lg border border-gray-500/30 shadow-md">
          <h2 className="text-2xl text-gray-800 font-medium">
            Analysis Summary
          </h2>

          {!analysis && !loading && (
            <p className="text-gray-500/80 mt-[50%] flex items-center justify-center text-center">
              Upload a file to generate insights.
            </p>
          )}

          {/* Skeleton loader */}
          {loading && (
            <div className="mt-6 space-y-4 animate-pulse">
              <div className="h-4 bg-gray-300 rounded w-3/4"></div>
              <div className="h-4 bg-gray-300 rounded w-1/2"></div>
              <div className="h-4 bg-gray-300 rounded w-2/3"></div>
              <div className="h-4 bg-gray-300 rounded w-5/6"></div>
            </div>
          )}

          {/* Results */}
          {analysis && !loading && (
            <ul className="mt-6 space-y-4 text-sm">
              <li>
                <span className="font-medium">Topics:</span>{" "}
                {analysis.topics
                  ?.map(
                    (t) => `${t.keywords.join(", ")} (${t.score.toFixed(2)})`
                  )
                  .join(" | ")}
              </li>

              <li>
                <span className="font-medium">Sentiment:</span>{" "}
                {analysis.sentiment?.label} (
                {analysis.sentiment?.score.toFixed(2)})
              </li>
              <li>
                <span className="font-medium">Extractive Summary:</span>{" "}
                {analysis.extractive_summary}
              </li>
              <li>
                <span className="font-medium">Abstractive Summary:</span>{" "}
                {analysis.abstractive_summary}
              </li>
              <li>
                <span className="font-medium">Suggestions:</span>{" "}
                {analysis.suggestions?.join(" ")}
              </li>
            </ul>
          )}
        </div>
      </div>
    </section>
  );
};

export default Analysis;
