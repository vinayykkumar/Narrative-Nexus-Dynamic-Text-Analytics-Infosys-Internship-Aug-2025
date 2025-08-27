import React, { useCallback, useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useDropzone } from "react-dropzone";
import { motion } from "framer-motion";
import Confetti from "react-confetti";
import ParticleBG from "../components/ParticleBG";
import AnimatedUploadTitle from "../components/AnimatedUploadTitle";
import { AnimatedFileIcon } from "../components/AnimatedFileIcon";

// Aurora/nebula animated gradient background
function AuroraBG() {
  return (
    <div className="absolute inset-0 -z-30 pointer-events-none overflow-hidden">
      <motion.div
        className="absolute top-[-15%] left-[-28%] w-[185%] h-[72%] rotate-[13deg] opacity-60"
        style={{
          background: "linear-gradient(90deg,#f472b6 10%,#818cf8 60%,#06b6d4 90%)",
          filter: "blur(100px)"
        }}
        initial={{ opacity: 0.45, x: -60 }}
        animate={{ opacity: [0.38, 0.82, 0.38], x: [0, 99, 0] }}
        transition={{ duration: 13, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute bottom-[-22%] right-[-20%] w-[138%] h-[62%] rotate-[-12deg] opacity-50"
        style={{
          background: "linear-gradient(80deg,#06b6d4 16%,#38bdf8 55%,#f0abfc 93%)",
          filter: "blur(82px)"
        }}
        initial={{ opacity: 0.26, x: 72 }}
        animate={{ opacity: [0.17, 0.44, 0.17], x: [0, -60, 0] }}
        transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
      />
    </div>
  );
}

// Confetti celebration on file set
function useConfettiBurst(trigger) {
  const [show, setShow] = useState(false);
  const prev = useRef(false);
  useEffect(() => {
    if (trigger && !prev.current) {
      setShow(true);
      setTimeout(() => setShow(false), 1500);
    }
    prev.current = trigger;
  }, [trigger]);
  return show;
}

export default function UploadPage() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  const onDrop = useCallback((accepted, rejections) => {
    setError(null);
    setProgress(0);
    setFile(null);
    if (rejections.length) {
      setError("Only .txt, .csv, .docx files up to 50MB are allowed.");
    } else if (accepted.length) {
      setFile(accepted[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    multiple: false,
    maxSize: 50 * 1024 * 1024,
    accept: {
      "text/plain": [".txt"],
      "text/csv": [".csv"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
    noClick: true,
    noKeyboard: true,
  });

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file.");
      return;
    }
    setProgress(5);
    setError(null);
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch("http://localhost:8001/analyze-all", {
        method: "POST",
        body: form,
      });
      if (!res.ok) throw new Error();
      setProgress(70);
      const data = await res.json();
      setProgress(100);
      setTimeout(() => navigate("/analysis", { state: data }), 600);
    } catch {
      setError("Analysis failed. Is backend running?");
      setProgress(0);
    }
  };

  const confetti = useConfettiBurst(!!file);

  // Always-working back: goes back if possible, else landing


  function NeonPulseRing({ active }) {
    return (
      <motion.div
        className="absolute inset-0 rounded-2xl pointer-events-none"
        style={{
          boxShadow: active
            ? "0 0 64px 20px #a855f7cc, 0 0 120px 40px #06b6d4bb"
            : "0 0 32px 10px #a21caf44"
        }}
        animate={{
          opacity: active ? [0.38, 0.88, 0.38] : 0.23,
          scale: active ? [1, 1.07, 1] : 1
        }}
        transition={{ duration: 1, repeat: Infinity }}
      />
    );
  }

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-100 via-purple-50 to-fuchsia-100 overflow-hidden">
      <AuroraBG />
      <ParticleBG />
      {/* Confetti on file drop */}
      {confetti && (
        <Confetti
          width={window.innerWidth}
          height={window.innerHeight}
          numberOfPieces={160}
          gravity={0.16}
          initialVelocityY={17}
          tweenDuration={3300}
          recycle={false}
          colors={[
            "#a855f7", "#06b6d4", "#fcd34d", "#38bdf8", "#f472b6", "#34d399", "#bef264"
          ]}
        />
      )}

      {/* Back Button (robust) */}
      <motion.button
        className="fixed top-7 left-8 z-50 flex items-center px-5 py-2.5 rounded-full bg-white/95 hover:bg-fuchsia-50 shadow-md text-2xl font-bold border border-fuchsia-300"
        onClick={() => navigate("/")}
        aria-label="Go Back"
        style={{ backdropFilter: "blur(5px)", boxShadow: "0 8px 26px -2px #c084fcbb" }}
        whileHover={{ scale: 1.09, x: -5, boxShadow: "0 8px 36px 0 #a855f7" }}
        whileTap={{ scale: 0.97 }}
        transition={{ type: "spring", stiffness: 270, damping: 19 }}
      >
        ← Back
      </motion.button>

      {/* Main Card */}
      <motion.div
        initial={{ opacity: 0, x: 60, scale: 0.97, rotateY: -3 }}
        animate={{ opacity: 1, x: 0, scale: 1, rotateY: 0 }}
        whileHover={{
          scale: 1.02,
          rotateY: 2,
          boxShadow: "0 38px 85px -11px #a855f7aa, 0 2px 65px 5px #06b6d4bb"
        }}
        transition={{ duration: 0.7, type: "spring" }}
        className="relative w-full max-w-xl mx-auto p-12 pb-10 rounded-[2.3rem] flex flex-col items-center z-30 glass shadow-2xl border border-white/25 bg-white/75 backdrop-blur-xl overflow-hidden"
      >
        {/* Pulse effect */}
        <NeonPulseRing active={isDragActive} />

        {/* Glow/flare inside card */}
        <motion.div
          className="absolute inset-0 pointer-events-none rounded-[2.3rem]"
          style={{
            background: "radial-gradient(circle at 62% 32%, #a855f7bb 0%, #06b6d4bb 68%, transparent 100%)",
            filter: "blur(2.3rem)"
          }}
          initial={{ opacity: 0.13, scale: 0.99 }}
          animate={{
            opacity: [0.09, 0.18, 0.09],
            scale: [0.95, 1.04, 0.95],
            y: [0, -12, 0]
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            repeatType: "reverse"
          }}
        />

        <AnimatedUploadTitle />

        <motion.p
          className="text-base mb-2 text-center text-gray-900 font-bold drop-shadow"
          initial={{ opacity: 0, y: 22 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.13, duration: 0.6 }}
        >
          Upload your files for <span className="text-fuchsia-600">AI-powered</span> instant insights.
        </motion.p>

        <div className="mb-7 text-[1rem] text-center text-gray-600 font-semibold backdrop-blur-xs">
          Supported: <span className="text-fuchsia-500 font-bold">.txt</span>,{" "}
          <span className="text-blue-500 font-bold">.csv</span>,{" "}
          <span className="text-cyan-500 font-bold">.docx</span> | Max:{" "}
          <span className="text-fuchsia-600 font-extrabold">50MB</span>
        </div>

        {/* Dropzone box */}
        <div
          {...getRootProps()}
          className={`relative w-full mb-6 p-12 border-2 border-dashed rounded-2xl glass cursor-pointer text-center shadow-xl transition-all
            duration-200 bg-white/30
            ${
              isDragActive ? "border-fuchsia-500 bg-fuchsia-100/30 scale-105 shadow-neon" 
                : "border-fuchsia-400/30 hover:scale-[1.03]"
            }
          `}
        >
          <input {...getInputProps()} />

          <motion.div
            initial={{ scale: 1, y: 0 }}
            animate={isDragActive ? { scale: 1.12, y: -11 } : { scale: 1, y: 0 }}
            transition={{ type: "spring", stiffness: 345, damping: 22 }}
          >
            <AnimatedFileIcon />
          </motion.div>
          <motion.p
            className="mt-2 mb-2 text-purple-600 font-semibold text-[1.16rem]"
            animate={isDragActive ? { scale: 1.12, color: "#a855f7" } : { scale: 1, color: "#7c3aed" }}
            transition={{ duration: 0.09 }}
          >
            Drag & drop file here
          </motion.p>

          {/* BROWSE BUTTON with double shine! */}
          <motion.button
            type="button"
            className="relative mt-4 px-12 py-3 text-lg font-extrabold rounded-full bg-gradient-to-r from-fuchsia-400 via-purple-500 to-cyan-400 text-white shadow-lg overflow-hidden border border-white/20 focus:outline-none"
            style={{ transformStyle: "preserve-3d" }}
            onClick={open}
            whileHover={{
              scale: 1.13,
              rotateX: -11,
              boxShadow: "0 4px 32px #a855f7cc,0 3px 20px 7px #06b6d4bb"
            }}
            whileTap={{ scale: 0.97, rotateX: 0 }}
            transition={{ type: "spring", stiffness: 265, damping: 15 }}
          >
            {/* Shine 1 */}
            <motion.div
              className="absolute left-0 top-0 h-full w-full pointer-events-none z-0"
              initial={{ opacity: 0, scale: 1 }}
              whileHover={{
                opacity: [0.03, 0.11, 0.03],
                scale: [1, 1.03, 1],
              }}
              transition={{ duration: 0.9, repeat: 1, repeatType: "mirror" }}
              style={{
                background: "linear-gradient(90deg,rgba(255,255,255,0.19) 9%,rgba(255,255,255,0.08) 49%,transparent 95%)",
                filter: "blur(8px)"
              }}
            />
            {/* Shine 2 */}
            <motion.div
              className="absolute left-[-60%] top-0 w-2/3 h-full pointer-events-none z-10"
              initial={{ x: "-100%" }}
              whileHover={{ x: "120%" }}
              transition={{ duration: 1.1, ease: "easeIn" }}
              style={{
                background: "linear-gradient(120deg,rgba(255,255,255,0.14),rgba(255,255,255,0.1),transparent)",
                filter: "blur(2.5px)"
              }}
            />
            <span className="relative z-20 flex items-center gap-2">
              <span className="mr-1" aria-label="folder" role="img">📁</span>Browse
            </span>
          </motion.button>
          <div className="mt-2 text-xs text-purple-800 font-bold">or click to select</div>
        </div>

        {/* File name and errors */}
        {file && <div className="w-full text-center my-3 font-bold text-lg text-fuchsia-600">{file.name}</div>}
        {error && <div className="text-fuchsia-700 font-semibold mt-2 animate-pulse">{error}</div>}

        {/* START ANALYSIS BUTTON with double shine! */}
        {file && (
          <>
            <motion.button
              onClick={handleUpload}
              disabled={progress > 0 && progress < 100}
              className="relative mt-4 px-12 py-3 rounded-full bg-gradient-to-r from-fuchsia-500 via-purple-500 to-cyan-400 text-white text-[1.22rem] font-extrabold shadow-lg overflow-hidden border border-white/25 focus:outline-none disabled:opacity-60"
              style={{ transformStyle: "preserve-3d" }}
              whileHover={{
                scale: 1.14,
                rotateX: -11,
                boxShadow: "0 7px 30px 0 #a855f7cc,0 4px 20px 7px #06b6d4bb"
              }}
              whileTap={{ scale: 0.96, rotateX: 0 }}
              transition={{ type: "spring", stiffness: 260, damping: 16 }}
            >
              {/* Shine 1 */}
              <motion.div
                className="absolute left-0 top-0 h-full w-full pointer-events-none z-0"
                initial={{ opacity: 0, scale: 1 }}
                whileHover={{
                  opacity: [0.04, 0.16, 0.04],
                  scale: [1, 1.03, 1],
                }}
                transition={{ duration: 0.8, repeat: 1, repeatType: "mirror" }}
                style={{
                  background: "linear-gradient(92deg,rgba(255,255,255,0.19) 8%,rgba(255,255,255,0.09) 48%,transparent 98%)",
                  filter: "blur(9px)"
                }}
              />
              {/* Shine 2 */}
              <motion.div
                className="absolute left-[-60%] top-0 w-2/3 h-full pointer-events-none z-10"
                initial={{ x: "-100%" }}
                whileHover={{ x: "120%" }}
                transition={{ duration: 1.1, ease: "easeIn" }}
                style={{
                  background: "linear-gradient(125deg,rgba(255,255,255,0.18),rgba(255,255,255,0.10),transparent)",
                  filter: "blur(2.2px)"
                }}
              />
              <span className="relative z-20 flex items-center gap-2">
                <span aria-label="sparkle" role="img" className="mr-1">✨</span>Start Analysis
              </span>
            </motion.button>
            {/* Progress bar and completion text */}
            <div className="w-full mt-4">
              <div className="h-4 w-full rounded-full bg-gray-200/60 overflow-hidden shadow-inner">
                <div
                  className="h-4 rounded-full bg-gradient-to-r from-fuchsia-500 via-purple-400 to-cyan-400 transition-all duration-500 shadow-lg"
                  style={{
                    width: `${progress}%`,
                    boxShadow: progress > 0 ? "0 0 14px #a855f7cc" : ""
                  }}
                />
              </div>
              {progress > 0 && progress < 100 && (
                <div className="mt-2 text-center animate-pulse text-fuchsia-600 font-bold">Processing... {progress}%</div>
              )}
              {progress === 100 && (
                <div className="mt-2 text-center text-green-600 font-extrabold">Analysis Complete! Redirecting...</div>
              )}
            </div>
          </>
        )}
      </motion.div>
    </div>
  );
}
