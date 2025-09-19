// src/pages/ai/Layout.jsx
import React, { useState } from 'react';
import { Outlet, NavLink, Link } from 'react-router-dom';
import { LayoutDashboard, TextSearch, Scissors, ReceiptTextIcon, Smile } from 'lucide-react';
import { assets } from '../../assets/assets';

const Layout = () => {
  const [analysisData, setAnalysisData] = useState(null);
  const [sentimentData, setSentimentData] = useState(null);
  const [insights, setInsights] = useState([]);

  const sidebarLinks = [
    { name: "Dashboard", path: "/ai", icon: LayoutDashboard },
    { name: "Text Analysis", path: "/ai/text-analysis", icon: TextSearch },
    { name: "Sentiment Analysis", path: "/ai/sentiment-analysis", icon: Smile },
    { name: "Text Summarization", path: "/ai/text-summarization", icon: Scissors },
    { name: "Reports & Insights", path: "/ai/reports", icon: ReceiptTextIcon },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1e1b4b] via-[#2e1f6a] to-[#1e1b4b] text-white">
      {/* Top Navbar */}
      <div className="flex items-center justify-between px-4 py-4 md:px-8 border-b border-gray-700 bg-gradient-to-r from-[#1e1b4b] to-[#2e1f6a] transition-all duration-300">
        <Link to={'/'}>
          <img className="md:h-7 h-5 cursor-pointer" src={assets.logo} alt="Logo" />
        </Link>
        <div className="flex items-center gap-5 text-gray-300">
          <button className="border border-blue-500 text-blue-500 hover:bg-blue-500/20 rounded-full text-sm px-4 py-1.5 cursor-pointer">
            Logout
          </button>
        </div>
      </div>

      {/* Sidebar + Main Content */}
      <div className="flex">
        {/* Sidebar */}
        <div className="lg:w-64 md:w-48 w-16 border-r border-gray-700 h-[92vh] pt-4 flex flex-col transition-all duration-300 bg-[#1e1b4b]">
          {sidebarLinks.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                to={item.path}
                key={item.name}
                end={item.path === "/ai"}
                className={({ isActive }) =>
                  `flex items-center py-3 px-4 gap-3 transition
                   ${isActive
                      ? "border-l-4 md:border-l-[6px] bg-blue-500/20 border-blue-500 text-blue-400"
                      : "hover:bg-gray-700/20 border-transparent text-gray-300"}` 
                }
              >
                <Icon className="w-6 h-6" />
                <p className="md:block hidden text-center">{item.name}</p>
              </NavLink>
            );
          })}
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6 bg-gradient-to-br from-[#1e1b4b] via-[#2e1f6a] to-[#1e1b4b] overflow-auto max-h-screen">
          <Outlet context={{
            analysisData,
            setAnalysisData,
            sentimentData,
            setSentimentData,
            insights,
            setInsights
          }} />
        </div>
      </div>
    </div>
  );
};

export default Layout;
