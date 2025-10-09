import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Landing from "./pages/Landing";
import AnalyzerPage from "./pages/Analyzer";
import DocsPage from "./pages/Docs";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/analyzer" element={<AnalyzerPage />} />
        <Route path="/docs" element={<DocsPage />} />
        {/* Fallback to landing */}
        <Route path="*" element={<Landing />} />
      </Routes>
    </BrowserRouter>
  );
}
