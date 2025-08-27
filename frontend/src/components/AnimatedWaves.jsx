import React from "react";
export default function AnimatedWaves() {
  return (
    <div className="absolute bottom-0 left-0 w-full h-52 z-0 pointer-events-none overflow-hidden">
      <svg viewBox="0 0 1440 320" className="w-full h-full" preserveAspectRatio="none">
        <defs>
          <linearGradient id="wavegrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#a855f7" stopOpacity="0.19"/>
            <stop offset="55%" stopColor="#00fff7" stopOpacity="0.12"/>
            <stop offset="100%" stopColor="#32ffc7" stopOpacity="0.18"/>
          </linearGradient>
        </defs>
        <path fill="url(#wavegrad)">
          <animate attributeName="d" dur="8.7s" repeatCount="indefinite"
            values="
              M0,160L80,171.7C160,183,320,205,480,213.3C640,221,800,215,960,213.3C1120,211,1280,213,1360,213.3L1440,213.3L1440,320L1360,320C1280,320,1120,320,960,320C800,320,640,320,480,320C320,320,160,320,80,320L0,320Z;
              M0,220L80,196C160,172,320,124,480,119.3C640,115,800,145,960,161.3C1120,177,1280,179,1360,170.7L1440,162.7L1440,320L1360,320C1280,320,1120,320,960,320C800,320,640,320,480,320C320,320,160,320,80,320L0,320Z;
              M0,160L80,171.7C160,183,320,205,480,213.3C640,221,800,215,960,213.3C1120,211,1280,213,1360,213.3L1440,213.3L1440,320L1360,320C1280,320,1120,320,960,320C800,320,640,320,480,320C320,320,160,320,80,320L0,320Z
            "
          />
        </path>
      </svg>
    </div>
  );
}
