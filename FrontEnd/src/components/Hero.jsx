<<<<<<< HEAD
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

    
=======
import { LucidePlayCircle, LucideSparkles } from "lucide-react";
import React from "react";
import { useNavigate } from "react-router-dom";

const Hero = () => {
  const navigate = useNavigate();

  return (
    <section className="relative min-h-screen flex flex-col md:flex-row items-center justify-between pb-20 pt-24 px-4 md:px-16 lg:px-24 xl:px-40 bg-black bg-[url(/bg.svg)] bg-no-repeat bg-cover text-white">

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
            className="bg-primary hover:bg-indigo-800 text-white active:scale-95 cursor-pointer rounded-md px-7 h-11"
            onClick={() => navigate("/analyze")}
          >
            Get started
          </button>

          <button className="flex items-center gap-2 border border-primary active:scale-95 hover:bg-primary/20 transition text-primary rounded-md px-6 h-11">
            <LucidePlayCircle/>
            <span>Watch demo</span>
          </button>
        </div>
      </div>

      {/* Hero image */}
      <img
        src="gradient-cybersickness-illustration_52683-137622.jpg"
        alt="hero"
        className="max-w-xs sm:max-w-sm lg:max-w-md transition-all rounded-full duration-300 mt-10 md:mt-0"
      />
>>>>>>> origin/main
    </section>
  );
};

export default Hero;
