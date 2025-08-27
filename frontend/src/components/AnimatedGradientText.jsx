// src/components/AnimatedGradientText.jsx
import React from "react";
export default function AnimatedGradientText({ children, className = "" }) {
  return (
    <span className={`font-extrabold text-black bg-gradient-to-r from-fuchsia-500 via-blue-500 to-cyan-500 bg-clip-text text-transparent animate-gradientText ${className}`}>
      {children}
    </span>
  );
}
