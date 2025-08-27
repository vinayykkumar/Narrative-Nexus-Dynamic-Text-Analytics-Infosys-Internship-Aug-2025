import React from "react";
export default function InsightsCard({ insight = "" }) {
  return (
    <div className="glass rounded-xl p-4 shadow-xl min-h-[220px]">
      <div className="font-bold text-lg text-cyan-700 mb-1">Key Insights &amp; Recommendations</div>
      <div className="text-base text-gray-800">{insight}</div>
    </div>
  );
}
