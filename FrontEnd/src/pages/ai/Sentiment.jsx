import { useState } from "react";
import { analyzeSentiment } from "../../api";

export default function Sentiment() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);

  const handleAnalyze = async () => {
    try {
      const data = await analyzeSentiment(text);
      setResult(data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Sentiment Analysis</h1>
      <textarea
        className="border p-2 w-full rounded"
        rows="5"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button
        onClick={handleAnalyze}
        className="mt-3 bg-blue-600 text-white px-4 py-2 rounded"
      >
        Analyze
      </button>

      {result && (
        <div className="mt-4 bg-gray-100 p-4 rounded">
          <p className="font-semibold">Label: {result.label}</p>
          <pre className="text-sm">{JSON.stringify(result.scores, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
