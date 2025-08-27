import React from "react";
import { Particles } from "@tsparticles/react";

export default function ParticleBG() {
  const options = {
    background: { color: { value: "#fcfcfd" } },
    fpsLimit: 60,
    particles: {
      number: { value: 100 },
      color: { value: [ "#a855f7", "#00fff7", "#ff74a4", "#ffe066", "#32ffc7" ] },
      shape: { type: "circle" },
      opacity: { value: 0.19, random: { enable: true, minimumValue: 0.11 } },
      size: { value: 90, random: { enable: true, minimumValue: 32 } },
      move: { enable: true, speed: 1.2, direction: "top-left", outModes: { default: "out" } }
    },
    detectRetina: true
  };
  return <Particles id="tsparticles" options={options} style={{position:'absolute',top:0,left:0,width:'100vw',height:'100vh',zIndex:0}} />;
}
