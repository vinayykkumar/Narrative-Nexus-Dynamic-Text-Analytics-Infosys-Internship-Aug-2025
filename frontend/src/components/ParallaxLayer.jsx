import React, { useRef, useEffect } from "react";
export default function ParallaxLayer({ depth = 0.2, children, className = "", style }) {
  const ref = useRef();
  useEffect(() => {
    function handleMouse(e) {
      const x = (e.clientX / window.innerWidth - 0.5) * 2;
      const y = (e.clientY / window.innerHeight - 0.5) * 2;
      if (ref.current) {
        ref.current.style.transform = `translate3d(${x * 60 * depth}px, ${y * 36 * depth}px, 0)`;
      }
    }
    window.addEventListener("mousemove", handleMouse);
    return () => window.removeEventListener("mousemove", handleMouse);
  }, [depth]);
  return (
    <div ref={ref} className={className} style={{ transition: "transform 0.23s cubic-bezier(.76,.19,.8,.82)", ...style }}>
      {children}
    </div>
  );
}
