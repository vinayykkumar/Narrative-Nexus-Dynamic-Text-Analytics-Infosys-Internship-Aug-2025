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
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Summarization</h1>
      <textarea
        className="border p-2 w-full rounded"
        rows="6"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button
        onClick={handleSummarize}
        className="mt-3 bg-green-600 text-white px-4 py-2 rounded"
      >
        Summarize
      </button>

      {summary && (
        <div className="mt-4 bg-gray-100 p-4 rounded">
          <h2 className="font-semibold">Summary</h2>
          <p>{summary}</p>
        </div>
      )}
    </div>
  );
}
