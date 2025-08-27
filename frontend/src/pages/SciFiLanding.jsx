import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import ParticleBG from "../components/ParticleBG";
import AnimatedGradientTitle from "../components/AnimatedGradientTitle";
import { FaRocket } from "react-icons/fa";

function FloatingGlow() {
  // Animated radial glow behind main card
  return (
    <motion.div
      className="absolute z-0 rounded-[3rem] pointer-events-none"
      style={{
        left: "-15%",
        top: "-12%",
        width: "130%",
        height: "130%",
        background: "radial-gradient(ellipse at 50% 40%, #a855f7bb 0%, #06b6d4cc 40%, #ecfeff00 90%)",
        filter: "blur(64px)",
        boxShadow: "0 0 260px 120px #a855f755"
      }}
      initial={{ opacity: 0.15, scale: 0.9 }}
      animate={{ 
        opacity: [0.22, 0.44, 0.22],
        scale: [0.95, 1.05, 0.95],
        y: [0, -24, 0]
      }}
      transition={{
        duration: 6,
        repeat: Infinity,
        repeatType: "reverse"
      }}
    />
  );
}

function AnimatedAuroraBG() {
  // Animated aurora stripes using gradients for "outer-space" mood
  return (
    <div className="absolute inset-0 -z-30 pointer-events-none overflow-hidden">
      <motion.div
        className="absolute top-[-20%] left-[-30%] w-[220%] h-[75%] rotate-[15deg] opacity-40"
        style={{
          background: "linear-gradient(90deg,#a7f3d0 10%,#818cf8 70%,#a855f7 100%)",
          filter: "blur(70px)"
        }}
        initial={{ opacity: 0.3, x: -80 }}
        animate={{ opacity: [0.4, 0.7, 0.4], x: [0, 120, 0] }}
        transition={{ duration: 22, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute bottom-[-25%] right-[-22%] w-[130%] h-[68%] rotate-[-12deg] opacity-30"
        style={{
          background: "linear-gradient(80deg,#06b6d4 8%,#38bdf8 45%,#f0abfc 80%)",
          filter: "blur(60px)"
        }}
        initial={{ opacity: 0.22, x: 80 }}
        animate={{ opacity: [0.2, 0.45, 0.2], x: [0, -50, 0] }}
        transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
      />
    </div>
  );
}

export default function SciFiLanding() {
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-100 via-cyan-50 to-purple-50 overflow-hidden">
      <AnimatedAuroraBG />
      <ParticleBG />
      <motion.div
        initial={{ opacity: 0, y: 68, scale: 0.98, rotateY: -12 }}
        animate={{ opacity: 1, y: 0, scale: 1, rotateY: 0 }}
        whileHover={{ scale: 1.028, rotateY: 3 }}
        transition={{ duration: 0.8, type: "spring" }}
        className="relative max-w-3xl w-full mx-auto px-12 py-16 rounded-[2.5rem] flex flex-col items-center shadow-2xl backdrop-blur-2xl bg-white/90 z-30 overflow-hidden"
        style={{
          boxShadow: "0 20px 60px -8px #a855f755, 0 8px 44px 6px #06b6d422"
        }}
      >
        <FloatingGlow />

        <AnimatedGradientTitle />

        <motion.p
          className="text-xl text-gray-900 text-center mb-10 drop-shadow"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25, duration: 0.7 }}
        >
          Your all-in-one AI-powered text analysis platform.<br />
          Upload articles, reports, or feedback — and get summarization, sentiment insights, and interactive visualizations in seconds.
        </motion.p>

        {/* Enhanced Try Now Button with multishine */}
        <motion.button
          onClick={() => navigate("/upload")}
          className="relative px-14 py-5 text-2xl font-bold bg-gradient-to-r from-fuchsia-400 via-purple-500 to-cyan-400 text-white rounded-full neon-flicker flex items-center gap-3 shadow-xl overflow-hidden border border-white/20"
          style={{ transformStyle: "preserve-3d" }}
          whileHover={{
            scale: 1.14,
            rotateX: -14,
            boxShadow: "0 10px 50px 0 #a855f7cc,0 2px 84px 8px #06b6d4bb"
          }}
          whileTap={{ scale: 0.96, rotateX: 0 }}
          transition={{ 
            type: "spring", 
            stiffness: 340, 
            damping: 18 
          }}
        >
          {/* Shine 1 */}
          <motion.div
            className="absolute left-0 top-0 h-full w-full pointer-events-none z-0"
            initial={{ opacity: 0, scale: 1 }} 
            whileHover={{ 
              opacity: [0.02, 0.12, 0.04], 
              scale: [1, 1.03, 1],
            }}
            transition={{ duration: 0.9, repeat: 1, repeatType: "mirror"}}
            style={{
              background: "linear-gradient(92deg,rgba(255,255,255,0.25) 8%,rgba(255,255,255,0.08) 50%,transparent 95%)",
              filter: "blur(10px)"
            }}
          />
          {/* Shine 2 */}
          <motion.div
            className="absolute left-[-60%] top-0 w-3/4 h-full pointer-events-none z-10"
            initial={{ x: "-100%" }}
            whileHover={{ x: "130%" }}
            transition={{ duration: 1.1, ease: "easeIn" }}
            style={{
              background:
                "linear-gradient(120deg,rgba(255,255,255,0.22),rgba(255,255,255,0.1),transparent)",
              filter: "blur(3.5px)"
            }}
          />
          <span className="relative z-20 flex items-center gap-2">
            <span role="img" aria-label="sparkles" className="mr-1">✨</span>
            Try Now
            <motion.span
              animate={{ rotate: [0, 360] }}
              transition={{ duration: 2.2, repeat: Infinity, ease: "linear" }}
              className="ml-2"
            >
              <FaRocket className="animate-bounce" />
            </motion.span>
          </span>
        </motion.button>
      </motion.div>
    </div>
  );
}
