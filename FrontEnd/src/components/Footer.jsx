import React from 'react'
import { assets } from '../assets/assets'

const Footer = () => {
  return (
    <footer className="w-full bg-gradient-to-b from-[#1B004D] to-[#2E0A6F] text-white">
            <div className="max-w-7xl mx-auto px-6 py-16 flex flex-col items-center">
                <div className="flex items-center space-x-3 mb-6">
                    <img alt="" className="h-8 md:h-11"
                        src={assets.logo} />
                </div>
                <p className="text-center max-w-2xl text-sm md:text-base font-normal leading-relaxed">
                    NarrativeNexus is a dynamic text analysis platform designed to extract
        key themes, detect sentiment, and generate actionable insights from
        large volumes of text.
                </p>
            </div>
            <div className="border-t border-[#3B1A7A]">
                <div className="max-w-7xl mx-auto px-6 py-6 text-center text-sm font-normal">
                    <a href="/">NarrativeNexus.ai</a> © 2025. All rights reserved.
                </div>
            </div>
        </footer>
    
  )
}

export default Footer