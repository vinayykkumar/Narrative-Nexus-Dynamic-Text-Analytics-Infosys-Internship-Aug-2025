import React from 'react'
import { assets } from '../assets/assets'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, LogOut, Save, UserCircle } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const Navbar = () => {
    const navigate = useNavigate();
    const { isAuthenticated, user, logout } = useAuth();
    const displayName = user?.name || user?.email?.split('@')[0] || 'Account';

    const handleLogout = () => {
        logout();
        navigate('/');
    }
    return (
        <div className='fixed z-5 w-full backdrop-blur-2xl flex justify-between items-center py-3 px-4 sm:px-20 xl:px-32'>
            <img src={assets.logo} alt="logo" className='h-5 sm:h-8 cursor-pointer' onClick={() => navigate('/')} />
            {isAuthenticated ? (
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="hidden sm:flex items-center gap-2 rounded-lg active:scale-95 transition-all text-sm cursor-pointer bg-white/10 text-white px-4 py-2 border border-white/20"
                    >
                        <Save className="w-4 h-4" /> Saved analyses
                    </button>
                    <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/15 text-white border border-white/10">
                        <UserCircle className="w-5 h-5" />
                        <span className="text-sm font-medium">{displayName}</span>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-2 rounded-lg active:scale-95 transition-all text-sm cursor-pointer bg-[#ef4444] text-white px-4 py-2"
                    >
                        <LogOut className="w-4 h-4" /> Sign out
                    </button>
                </div>
            ) : (
                <button onClick={() => navigate('/login')} className="flex items-center gap-2 rounded-lg active:scale-95 transition-all text-sm cursor-pointer bg-[#4f46e5] text-white px-5 py-2 md:px-8 md:py-2.5" >
                    Sign in <ArrowRight className="w-4 h-4 mt-0.5" />
                </button>
            )}
        </div>
    )
}

export default Navbar