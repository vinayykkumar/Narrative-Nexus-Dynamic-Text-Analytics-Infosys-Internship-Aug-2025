import { LucidePlayCircle, LucideSparkles } from "lucide-react";
import React from "react";
import { useNavigate } from "react-router-dom";

const Hero = () => {
  const navigate = useNavigate();

  return (
    <section className="relative min-h-screen flex flex-col md:flex-row items-center justify-between pb-20 pt-24 px-4 md:px-16 lg:px-24 xl:px-40 bg-black bg-[url(/bg.svg)] text-white">

      <div className="flex flex-col items-center md:items-start">
        {/* Community / Avatar group */}
        <div className="flex flex-wrap items-center justify-center p-1.5 rounded-full border border-slate-600 text-white text-sm px-4 py-2">
          <p className="flex gap-2 items-center">
          <LucideSparkles width={16} height={16} className="mt-0.5" /> 
          Advanced Text Analysis Platform
        </p>
          
        </div>

        {/* Heading */}
        <h1 className="text-center md:text-left text-5xl leading-[68px] md:text-6xl md:leading-[84px] font-semibold max-w-xl text-white mt-6">
          Turn Text Into <span className="text-primary">Actionable Insights</span> Instantly.
        </h1>

        {/* Subheading */}
        <p className="text-center md:text-left text-sm md:text-base text-slate-300 max-w-lg mt-2">
          NarrativeNexus helps you analyze, summarize, and visualize text data—from reports to social media—so you can make smarter decisions faster.
        </p>

        {/* Buttons */}
        <div className="flex items-center gap-4 mt-8 text-sm">
          <button
            className="bg-white hover:bg-slate-200 text-black active:scale-95 rounded-md px-7 h-11"
            onClick={() => navigate("/analyze")}
          >
            Get started
          </button>

          <button className="flex items-center gap-2 border border-slate-600 active:scale-95 hover:bg-white/10 transition text-white rounded-md px-6 h-11">
            <LucidePlayCircle/>
            <span>Watch demo</span>
          </button>
        </div>
      </div>

      {/* Hero image */}
      <img
        src="https://img.freepik.com/premium-photo/accountants-accounting-mobile-business-plan-generative-ai_199064-2128.jpg"
        alt="hero"
        className="max-w-xs sm:max-w-sm lg:max-w-md transition-all rounded-2xl duration-300 mt-10 md:mt-0"
      />
    </section>
  );
};

export default Hero;
