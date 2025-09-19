import { useState } from "react";
import { summarizeText } from "../../api";

export default function Summarization() {
  const [text, setText] = useState("");
  const [summary, setSummary] = useState("");

  const handleSummarize = async () => {
    try {
      const data = await summarizeText(text);
      setSummary(data.summary);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center text-white">Text Summarization</h1>

      <textarea
        className="border p-3 w-full rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
        rows="5"
        placeholder="Enter the text for sentiment analysis..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <div className="text-center mt-4">
        <button
          onClick={handleSummarize}
          className="bg-primary text-white px-6 py-2 rounded-lg hover:bg-indigo-800 transition"
        >
          Summarize
        </button>
      </div>

      {summary && (
        <div className="mt-4 bg-gray-100 p-4 rounded">
          <h2 className="font-semibold">Summary</h2>
          <p>{summary}</p>
        </div>
      )}
    </div>
  );
}
