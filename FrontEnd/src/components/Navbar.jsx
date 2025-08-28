import React from 'react'
import { assets } from '../assets/assets'
import { useNavigate } from 'react-router-dom'
import { ArrowRight } from 'lucide-react';
// import { useClerk, UserButton, useUser } from '@clerk/clerk-react'

const Navbar = () => {
    const navigate = useNavigate();
    // const { user } = useUser();
    // const { openSignIn } = useClerk();
    return (
        <div className='fixed z-5 w-full backdrop-blur-2xl flex justify-between items-center py-3 px-4 sm:px-20 xl:px-32'>
            <img src={assets.logo} alt="logo" className='h-5 sm:h-8 cursor-pointer' onClick={() => navigate('/')} />
            {/* {
                user ? <UserButton /> : ( */}
                    <button onClick={() => navigate('/login')} className="flex items-center gap-2 rounded-full active:scale-95 transition-all text-sm cursor-pointer bg-[#4f46e5] text-white px-5 py-2 md:px-8 md:py-2.5" >
                        Sign in <ArrowRight className="w-4 h-4 mt-0.5" />
                    </button>
                
        </div>
    )
}

export default Navbar