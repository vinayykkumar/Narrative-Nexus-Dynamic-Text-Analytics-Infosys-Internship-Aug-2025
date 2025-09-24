import React, { useState } from "react";
import { CircleX, FilePlusIcon, Folder } from "lucide-react";

const Analysis = () => {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

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
    if (validateFile(selectedFile)) setFile(selectedFile);
    else e.target.value = "";
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (validateFile(droppedFile)) setFile(droppedFile);
  };

  const handleSubmit = async () => {
    if (!file) return alert("Please upload a file first!");
    setLoading(true);
    setAnalysis(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://127.0.0.1:8000/analyze-file", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      setAnalysis(result);
    } catch (error) {
      console.error("Error:", error);
      alert("Error analyzing file");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="py-4">
      <div className="max-w-6xl mx-auto px-6 flex gap-8">
        {/* Left Panel - Upload */}
        <div className="w-[420px] max-h-fit top-4 p-6 bg-white rounded-lg border border-gray-200 shadow-md ">
          <div className="flex items-center justify-center w-12 h-12 bg-gray-100 rounded-full">
            <Folder className="text-primary w-5 h-5" />
          </div>
          <h2 className="text-2xl font-semibold text-gray-800 mt-3">
            Upload a File
          </h2>
          <p className="text-gray-500 mt-1 text-sm">
            Attach a .txt, .csv, .pdf, or .docx file
          </p>

          {/* Drag & Drop */}
          <label
            htmlFor="fileInput"
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            className="border-2 border-dotted border-gray-300 p-6 mt-6 flex flex-col items-center gap-3 cursor-pointer hover:border-primary transition-colors rounded-lg"
          >
            <FilePlusIcon className="text-primary w-6 h-6" />
            <p className="text-gray-500 text-sm">Drag & drop your file here</p>
            <p className="text-gray-500 text-sm">
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

          {/* File Preview */}
          {file && (
            <div className="mt-4 px-4 py-2 bg-blue-50 rounded-lg flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-700">{file.name}</p>
                <p className="text-xs text-gray-500">
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
                setAnalysis(null);
              }}
              className="px-6 py-2 border border-gray-300 text-gray-600 rounded-full hover:bg-gray-100 transition"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={loading || !file}
              className="px-6 py-2 bg-primary text-white rounded-full hover:bg-indigo-600 transition disabled:opacity-50"
            >
              {loading ? "Analyzing..." : "Analyze"}
            </button>
          </div>
        </div>

        {/* Right Panel - Results */}
        <div className="flex-1 p-6 bg-white rounded-lg border border-gray-200 shadow-md">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            Analysis Results
          </h2>

          {!analysis && !loading && (
            <p className="text-gray-400 mt-30 text-center">
              Upload a file to generate results.
            </p>
          )}

          {loading && (
            <p className="text-gray-500 mt-6 text-center">Analyzing file...</p>
          )}

          {analysis && !loading && (
            <div className="space-y-6">
              {/* Topics Card */}
              <div className="p-5 bg-white rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow duration-300">
                <h3 className="font-semibold text-indigo-600 text-lg mb-3">
                  Topics
                </h3>
                <p className="text-gray-700 text-sm">
                  {analysis.topics
                    ?.map(
                      (t) => `${t.keywords.join(", ")} (${t.score.toFixed(2)})`
                    )
                    .join(" | ")}
                </p>
              </div>

              {/* Sentiment Card */}
              <div className="p-5 bg-white rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow duration-300">
                <h3 className="font-semibold text-indigo-600 text-lg mb-3">
                  Sentiment
                </h3>
                <p className="text-gray-700 text-sm">
                  {analysis.sentiment?.label} (
                  {analysis.sentiment?.score.toFixed(2)})
                </p>
              </div>

              {/* Extractive Summary Card */}
              <div className="p-5 bg-white rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow duration-300">
                <h3 className="font-semibold text-indigo-600 text-lg mb-3">
                  Extractive Summary
                </h3>
                <p className="text-gray-700 text-sm">
                  {analysis.extractive_summary}
                </p>
              </div>

              {/* Abstractive Summary Card */}
              <div className="p-5 bg-white rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow duration-300">
                <h3 className="font-semibold text-indigo-600 text-lg mb-3">
                  Abstractive Summary
                </h3>
                <p className="text-gray-700 text-sm">
                  {analysis.abstractive_summary}
                </p>
              </div>

              {/* Suggestions Card */}
              {analysis.suggestions && analysis.suggestions.length > 0 && (
                <div className="p-5 bg-white rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow duration-300">
                  <h3 className="font-semibold text-indigo-600 text-lg mb-3">
                    Suggestions
                  </h3>
                  <p className="text-gray-700 text-sm">
                    {analysis.suggestions.join(" ")}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default Analysis;
