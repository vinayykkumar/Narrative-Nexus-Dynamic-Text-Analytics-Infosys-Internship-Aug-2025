import React from "react";
export default function AnimatedUploadTitle() {
  return (
    <h2 className="font-black text-4xl mb-6 tracking-tight text-center">
      <span className="text-black">Upload Your </span>
      <span className="animated-gradient-text bg-gradient-to-r from-fuchsia-500 via-blue-400 to-cyan-400 bg-clip-text text-transparent">
        Dataset
      </span>
    </h2>
  );
}
