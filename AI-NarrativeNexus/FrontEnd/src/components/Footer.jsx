import React from 'react'
import { assets } from '../assets/assets'
import { Link } from 'react-router-dom'

const Footer = () => {
  return (
    
    <footer className="px-6 md:px-16 lg:px-24 xl:px-32 w-full text-sm bg-gradient-to-b from-[#040405] to-[#431f86] text-white pt-10">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-14">
                    <div className="sm:col-span-2 lg:col-span-1">
                        <img src={assets.logo} alt="" className='h-6 md:h-9'/>
                        <p className="text-sm/7 mt-6">NarrativeNexus is a dynamic text analysis platform designed to extract key themes, detect sentiment, and generate actionable insights from large volumes of text.</p>
                    </div>
                    <div className="flex flex-col lg:items-center lg:justify-center">
                        <div className="flex flex-col text-sm space-y-2.5">
                            <h2 className="font-semibold mb-5 text-primary">Company</h2>
                            <Link to="/about-us" className="hover:text-slate-600 transition" >About us</Link>
                            <Link to="/careers" className="hover:text-slate-600 transition" >Careers</Link>
                            <Link to="/contact-us" className="hover:text-slate-600 transition" >Contact us</Link>
                            <Link to="/privacy-policy" className="hover:text-slate-600 transition" >Privacy policy</Link>
                        </div>
                    </div>
                    <div className='hidden md:block'>
                        <h2 className="font-semibold text-primary mb-5">Subscribe to our newsletter</h2>
                        <div className="text-sm space-y-6 max-w-sm">
                            <p>The latest news, articles, and resources, sent to your inbox weekly.</p>
                            <div className="flex items-center justify-center gap-2 p-2 rounded-md bg-indigo-100">
                                <input className="focus:ring-2 ring-indigo-600 outline-none text-black w-full max-w-64 py-2 rounded px-2" type="email" placeholder="Enter your email" />
                                <button className="bg-indigo-600 px-4 py-2 text-white rounded">Subscribe</button>
                            </div>
                        </div>
                    </div>
                </div>
                <p className="py-4 text-center border-t mt-6 border-slate-200">
                    Copyright 2025 © <a href="/">NarrativeNexus.ai</a> | All Right Reserved.
                </p>
            </footer>
    
  )
}

export default Footer