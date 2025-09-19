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

  // Calculate percentage score for each sentiment
  const getScore = (type) => {
    if (!result) return 0;
    if (type === "positive") {
      return (
        (result.vader.pos * 100 +
          (result.textblob.polarity > 0 ? 100 : 0) +
          (result.transformer.label === "positive" ? result.transformer.score * 100 : 0)) /
        3
      ).toFixed(1);
    } else if (type === "neutral") {
      return (
        (result.vader.neu * 100 +
          (Math.abs(result.textblob.polarity) < 0.1 ? 100 : 0) +
          (result.transformer.label === "neutral" ? result.transformer.score * 100 : 0)) /
        3
      ).toFixed(1);
    } else if (type === "negative") {
      return (
        (result.vader.neg * 100 +
          (result.textblob.polarity < 0 ? 100 : 0) +
          (result.transformer.label === "negative" ? result.transformer.score * 100 : 0)) /
        3
      ).toFixed(1);
    }
  };

  // Provide topic explanations
  const getTopic = (type) => {
    if (!result) return "";
    if (type === "positive") {
      return "The text contains positive expressions or praise.";
    } else if (type === "neutral") {
      return "The text is mostly factual or lacks emotional tone.";
    } else if (type === "negative") {
      return "The text mentions complaints or dissatisfaction.";
    }
  };

  // Determine overall sentiment based on highest score
  const getOverall = () => {
    const scores = {
      positive: parseFloat(getScore("positive")),
      neutral: parseFloat(getScore("neutral")),
      negative: parseFloat(getScore("negative")),
    };
    const max = Math.max(scores.positive, scores.neutral, scores.negative);
    const sentiment = Object.keys(scores).find((key) => scores[key] === max);
    return { sentiment, score: max };
  };

  const overall = result ? getOverall() : null;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center text-white">Sentiment Analysis</h1>

      <textarea
        className="border p-3 w-full rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
        rows="5"
        placeholder="Enter the text for sentiment analysis..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <div className="text-center mt-4">
        <button
          onClick={handleAnalyze}
          className="bg-primary text-white px-6 py-2 rounded-lg hover:bg-indigo-800 transition"
        >
          Analyze
        </button>
      </div>

      {result && (
        <>
          {/* Sentiment Cards */}
          <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-lg bg-gradient-to-br from-green-100 to-green-200 shadow hover:scale-105 transition">
              <div className="text-xl font-bold text-green-800 text-center">Positive 😊</div>
              <div className="text-3xl font-extrabold text-green-700 text-center">{getScore("positive")}%</div>
              <div className="text-sm text-green-600 mt-2 text-center">{getTopic("positive")}</div>
            </div>

            <div className="p-4 rounded-lg bg-gradient-to-br from-yellow-100 to-yellow-200 shadow hover:scale-105 transition">
              <div className="text-xl font-bold text-yellow-800 text-center">Neutral 😐</div>
              <div className="text-3xl font-extrabold text-yellow-700 text-center">{getScore("neutral")}%</div>
              <div className="text-sm text-yellow-600 mt-2 text-center">{getTopic("neutral")}</div>
            </div>

            <div className="p-4 rounded-lg bg-gradient-to-br from-red-100 to-red-200 shadow hover:scale-105 transition">
              <div className="text-xl font-bold text-red-800 text-center">Negative 😢</div>
              <div className="text-3xl font-extrabold text-red-700 text-center">{getScore("negative")}%</div>
              <div className="text-sm text-red-600 mt-2 text-center">{getTopic("negative")}</div>
            </div>
          </div>

          {/* Overall Sentiment */}
          <div className="mt-6 p-6 rounded-lg bg-blue-100 shadow hover:scale-105 transition text-center">
            <div className="text-2xl font-bold text-blue-800 mb-2">Overall Sentiment</div>
            <div className="text-4xl font-extrabold text-blue-700 mb-2">
              {overall.sentiment.charAt(0).toUpperCase() + overall.sentiment.slice(1)} {overall.sentiment === "positive" ? "😊" : overall.sentiment === "neutral" ? "😐" : "😢"}
            </div>
            <div className="text-lg text-primary mb-2">{overall.score}% confidence</div>
            <div className="text-sm text-primary">This is the dominant sentiment based on the analysis.</div>
          </div>
        </>
      )}
    </div>
  );
}
