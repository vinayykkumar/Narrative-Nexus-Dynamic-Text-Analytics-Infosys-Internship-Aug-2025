import { useState } from "react";
import { Outlet, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Auth/Login";
import Analysis from "./pages/Analysis";
import Navbar from "./components/Navbar";
import About from "./pages/About";

const AppLayout = () => {
  const [analysisData, setAnalysisData] = useState(null);
  const [sentimentData, setSentimentData] = useState(null);
  const [insights, setInsights] = useState([]);

  return (
    <>
      <Navbar />
      <main className="pt-20">
        <Outlet
          context={{
            analysisData,
            setAnalysisData,
            sentimentData,
            setSentimentData,
            insights,
            setInsights,
          }}
        />
      </main>
    </>
  );
};

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/analyze" element={<Analysis />} />
        <Route path="/about-us" element={<About />} />
      </Route>
    </Routes>
  );
}

export default App;
