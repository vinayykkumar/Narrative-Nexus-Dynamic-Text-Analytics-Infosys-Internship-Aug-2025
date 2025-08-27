import React from "react";
export default function AnimatedGradientTitle() {
  return (
    <h1 className="font-black text-5xl md:text-6xl mb-6 tracking-tight drop-shadow-lg text-center">
      <span className="text-black">Welcome</span>{" "}
      <span className="animated-gradient-text bg-gradient-to-r from-fuchsia-500 via-blue-400 to-cyan-400 bg-clip-text text-transparent">
        Smart Dataset Analyzer
      </span>
    </h1>
    
  );
}
