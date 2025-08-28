import React, { useState } from 'react'
import { ArrowUp, FilePlusIcon, Folder, X } from 'lucide-react'

const Analysis = () => {
  const [file, setFile] = useState(null)
  const [text, setText] = useState("")
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [dragActive, setDragActive] = useState(false)

  const allowedTypes = [
    "text/plain", // .txt
    "text/csv", // .csv
    "application/pdf", // .pdf
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document", // .docx
  ]

  // Validate and set file
  const validateFile = (selectedFile) => {
    if (!selectedFile) return false
    if (!allowedTypes.includes(selectedFile.type)) {
      alert("Unsupported file type! Please upload .txt, .csv, .pdf, or .docx files only.")
      return false
    }
    return true
  }

  // Handle file selection
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (validateFile(selectedFile)) {
      setFile(selectedFile)
    } else {
      e.target.value = "" // reset input
    }
  }

  // Drag & drop handlers
  const handleDragOver = (e) => {
    e.preventDefault()
    setDragActive(true)
  }

  const handleDragLeave = () => {
    setDragActive(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragActive(false)
    const droppedFile = e.dataTransfer.files[0]
    if (validateFile(droppedFile)) {
      setFile(droppedFile)
    }
  }

  // Submit handler
  const handleSubmit = async () => {
    if (!file && !text.trim()) {
      alert("Please upload a file or enter text!")
      return
    }
    setLoading(true)

    try {
      const formData = new FormData()
      if (file) formData.append("file", file)
      if (text.trim()) formData.append("text", text)

      const response = await fetch("http://localhost:5000/analyze", {
        method: "POST",
        body: formData,
      })

      const result = await response.json()
      setAnalysis(result)
    } catch (error) {
      console.error("Error:", error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="py-8">
      <div className="max-w-6xl mx-auto px-6 grid md:grid-cols-2 gap-10">
        {/* Left Side */}
        <div className="max-w-auto w-full p-6 bg-white/80 rounded-lg border border-gray-500/30 shadow-[0px_1px_15px_0px] shadow-black/10 text-sm">
          <div className="flex items-center justify-center w-11 h-11 bg-gray-500/10 rounded-full">
            <Folder className="text-primary w-5 h-5" />
          </div>
          <h2 className="text-2xl text-gray-800 font-medium mt-3">Upload a file</h2>
          <p className="text-gray-500/80 mt-1">Attach the file below</p>

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
            <p className="text-gray-500">Drag and Drop files here</p>
            <p className="text-gray-400">
              Or <span className="text-primary underline">click here</span> to select
            </p>
            <p className="text-gray-400">Supports: .txt, .csv, .pdf, .docx</p>
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
            <div className="mt-4 p-3 border rounded-lg flex items-center justify-between bg-gray-50">
              <div>
                <p className="text-gray-700 font-medium">{file.name}</p>
                <p className="text-gray-400 text-xs">{(file.size / 1024).toFixed(2)} KB</p>
              </div>
              <button
                onClick={() => setFile(null)}
                className="text-red-500 hover:text-red-700 cursor-pointer"
                aria-label="Remove file"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          )}

          <div className="text-black flex justify-center text-center my-6">OR</div>

          {/* Text Area */}
          <div className="max-w-xl w-full border border-gray-500 rounded-xl overflow-hidden mt-4">
            <textarea
              className="w-full p-3 pb-0 resize-none outline-none bg-transparent text-gray-800"
              placeholder="Enter your text here..."
              rows="4"
              value={text}
              onChange={(e) => setText(e.target.value)}
            ></textarea>
          </div>

          {/* Submit Button */}
          <div className="mt-6 flex justify-end gap-4">
            <button
              type="button"
              className="px-9 py-2 border border-gray-500/50 bg-white hover:bg-blue-100/30 active:scale-95 transition-all text-gray-500 rounded-full"
              onClick={() => {
                setFile(null)
                setText("")
                setAnalysis(null)
              }}
            >
              Cancel
            </button>
            <button
              type="button"
              className="px-6 py-2 bg-primary hover:bg-indigo-600 active:scale-95 transition-all text-white rounded-full"
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? "Analyzing..." : "Submit"}
            </button>
          </div>
        </div>

        {/* Right Side - Analysis */}
        <div className="max-w-auto w-full p-6 bg-white/80 rounded-lg border border-gray-500/30 shadow-[0px_1px_15px_0px] shadow-black/10">
          <h2 className="text-2xl text-gray-800 font-medium">Analysis Summary</h2>

          {!analysis ? (
            <p className="text-gray-500/80 mt-[50%] flex items-center justify-center text-center">
              Once you upload a file, NarrativeNexus will analyze the text and generate insights.
            </p>
          ) : (
            <ul className="mt-6 space-y-4 text-sm">
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 flex items-center justify-center bg-indigo-100 text-indigo-600 rounded-full text-xs font-bold">
                  1
                </span>
                <p className="text-gray-600">
                  <span className="font-medium">Topics Identified:</span>{" "}
                  {analysis.topics?.join(", ")}
                </p>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 flex items-center justify-center bg-indigo-100 text-indigo-600 rounded-full text-xs font-bold">
                  2
                </span>
                <p className="text-gray-600">
                  <span className="font-medium">Sentiment:</span> {analysis.sentiment}
                </p>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 flex items-center justify-center bg-indigo-100 text-indigo-600 rounded-full text-xs font-bold">
                  3
                </span>
                <p className="text-gray-600">
                  <span className="font-medium">Summary:</span> {analysis.summary}
                </p>
              </li>
            </ul>
          )}
        </div>
      </div>
    </section>
  )
}

export default Analysis
