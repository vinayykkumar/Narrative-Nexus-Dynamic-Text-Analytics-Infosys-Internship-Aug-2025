import React from "react";
export default function FloatingBubbles() {
  const bubbles = [
    { left: "16%", top: "24%", size: "110px", blur: "8px", color: "rgba(168,85,247,0.18)" },
    { left: "72%", top: "14%", size: "76px", blur: "13px", color: "rgba(0,255,247,0.17)" },
    { left: "45%", top: "84%", size: "150px", blur: "18px", color: "rgba(255,224,102,0.13)" },
    { left: "85%", top: "73%", size: "82px", blur: "11px", color: "rgba(255,115,186,0.15)" }
  ];
  return (
    <div className="pointer-events-none absolute inset-0 w-full h-full overflow-hidden z-10">
      {bubbles.map((b,i) => (
        <div key={i} style={{
          position: "absolute",
          left: b.left, top: b.top, width: b.size, height: b.size,
          borderRadius: "50%",
          background: b.color,
          filter: `blur(${b.blur})`,
          animation: `floatBubble ${8 + i * 2.1}s ease-in-out infinite alternate`
        }} />
      ))}
      <style>
        {`
        @keyframes floatBubble {
          0% { transform: translateY(0px) scale(1);}
          100% { transform: translateY(-50px) scale(1.13);}
        }
        `}
      </style>
    </div>
  );
}
