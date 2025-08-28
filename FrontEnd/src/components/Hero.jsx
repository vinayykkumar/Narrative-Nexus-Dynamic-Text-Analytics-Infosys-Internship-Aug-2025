import { ArrowRight, LucideSparkles, Sparkle } from "lucide-react";
import React from "react";
import { useNavigate } from "react-router-dom";
import {assets} from '../assets/assets'



const Hero = () => {
  const navigate = useNavigate();
  return (
    <section className="relative min-h-screen flex flex-col items-center bg-black text-white pt-12 sm:pt-16 md:pt-20 bg-[url(/bg_gradient.png)] bg-center bg-cover">
    <div className="flex items-center justify-center gap-2 border border-white/40 rounded-full px-4 py-2 text-xs sm:text-sm mt-34 mx-auto">
        <p className="flex gap-2 text-center"><LucideSparkles width={16} height={16} className="mt-0.5"/> Advanced Text Analysis Platform</p>
        
    </div>

    <h1 className="text-4xl md:text-6xl text-center font-semibold max-w-3xl mt-5 text-white  mb-2">
        Turn Text Into Actionable Insights Instantly
    </h1>
    <p className="text-slate-300 md:text-lg line-clamp-3 max-md:px-2 text-center max-w-2xl mt-3">
        NarrativeNexus helps you analyze, summarize, and visualize text data—from reports to social media—so you can make smarter decisions faster.
    </p>

    <div className="grid grid-cols-2 gap-2 mt-8 text-sm">
        <button onClick={() => navigate('/ai')} className="px-8 py-3 bg-primary hover:bg-indigo-700 active:scale-95 transition-all cursor-pointer rounded-full">
            Get Started
        </button>
        <a href="#ai-features"><button className="flex items-center gap-2 bg-white/10 border border-white/15 rounded-full px-6 py-3 cursor-pointer">
            <span>Learn More</span>
            
        </button></a>
    </div>

    
    </section>
  );
};

export default Hero;
