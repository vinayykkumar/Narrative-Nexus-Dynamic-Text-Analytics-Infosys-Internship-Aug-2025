import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import ParticleBG from "../components/ParticleBG";
import jsPDF from "jspdf";
import "jspdf-autotable";

export default function ExplorePage() {
  const navigate = useNavigate();
  const { state } = useLocation();

  if (!state || !state.text) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-cyan-50 to-fuchsia-100">
        <ParticleBG />
        <div className="glass px-10 py-12 rounded-2xl text-center shadow-xl">
          <h2 className="text-2xl font-bold mb-6 text-blue-600">Nothing to Explore</h2>
          <button
            onClick={() => navigate(-1)}
            className="px-8 py-3 rounded-full bg-gradient-to-r from-fuchsia-400 via-purple-400 to-cyan-400 text-white font-bold text-lg shadow-neon"
          >
            ← Back
          </button>
        </div>
      </div>
    );
  }

  const handleDownload = () => {
    const doc = new jsPDF();
    doc.text(state.title || "Explore Text", 14, 20);
    const lines = doc.splitTextToSize(state.text, 180);
    doc.setFontSize(12);
    doc.text(lines, 14, 30);
    doc.save((state.title || "text") + ".pdf");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-cyan-50 to-fuchsia-100 relative">
      <ParticleBG />
      <button
        className="fixed top-6 left-6 glass px-4 py-2 rounded-full text-xl font-bold"
        onClick={() => navigate(-1)}
      >← Back</button>
      <div className="glass max-w-2xl w-full mx-auto p-10 rounded-xl shadow-xl text-center z-10">
        <h2 className="text-2xl font-extrabold mb-5 text-blue-700">{state.title}</h2>
        <div className="whitespace-pre-wrap break-words text-lg mb-6">{state.text}</div>
        <button
          className="px-8 py-3 bg-gradient-to-r from-purple-500 to-cyan-400 text-white rounded-full text-lg font-bold mt-2"
          onClick={handleDownload}
        >
          Download PDF
        </button>
      </div>
    </div>
  );
}
