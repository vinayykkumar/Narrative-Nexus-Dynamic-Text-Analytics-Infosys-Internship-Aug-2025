import React from "react";
import ReactD3Cloud from "react-d3-cloud";

export default function WordCloudPanel({ words = [] }) {
  const fontSizeMapper = word => Math.log2(word.value + 1) * 14;
  return (
    <div className="glass rounded-xl p-4 shadow-md min-h-[190px]">
      <div className="font-bold text-lg mb-2 text-purple-700">Top Terms</div>
      <div style={{height: 140, width: "100%"}}>
        <ReactD3Cloud
          data={words}
          fontSizeMapper={fontSizeMapper}
          height={140}
          width={240}
          spiral="archimedean"
        />
      </div>
    </div>
  );
}
