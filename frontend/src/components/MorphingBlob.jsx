import React from "react";
export default function MorphingBlob() {
  return (
    <svg className="absolute left-[-16vw] top-[-6vw] z-0 pointer-events-none" width="400" height="400" viewBox="0 0 600 600" style={{ opacity: 0.22, filter: "blur(22px)" }}>
      <defs>
        <linearGradient id="blobgrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#00fff7" />
          <stop offset="52%" stopColor="#a855f7" />
          <stop offset="100%" stopColor="#53fec8" />
        </linearGradient>
      </defs>
      <path fill="url(#blobgrad)">
        <animate attributeName="d" dur="8s" repeatCount="indefinite"
          values="
            M418,346Q388,442,298,464Q208,486,150,393Q92,300,159,218Q225,137,326,153Q427,169,441,234Q455,299,418,346Z;
            M441,273Q398,399,295,396Q192,393,142,306Q92,219,194,196Q296,173,405,174Q515,175,441,273Z;
            M418,346Q388,442,298,464Q208,486,150,393Q92,300,159,218Q225,137,326,153Q427,169,441,234Q455,299,418,346Z
          "
        />
      </path>
    </svg>
  );
}
