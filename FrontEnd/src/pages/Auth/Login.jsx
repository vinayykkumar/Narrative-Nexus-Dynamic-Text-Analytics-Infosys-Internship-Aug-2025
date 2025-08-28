import { Lock, Mail } from 'lucide-react'
import React from 'react'

const Login = () => {
  return (
    <div className='py-20 px-4 sm:px-20 xl:px-32 bg-[url(bg_gradient.png)] bg-black min-h-screen flex items-center justify-center'>
    <form className="max-w-96 w-full text-center border border-gray-300/60 rounded-2xl px-8 bg-transparent mx-auto my-20">
            <h1 className="text-white text-3xl mt-10 font-medium">Login</h1>
            <p className="text-gray-400 text-sm mt-2">Please sign in to continue</p>
            <div className="flex items-center w-full mt-10 bg-white border border-gray-300/80 h-12 rounded-full overflow-hidden pl-6 gap-2">
                <Mail className='w-4 h-4'/>
                <input type="email" placeholder="Email id" className="bg-transparent text-gray-500 placeholder-gray-500 outline-none text-sm w-full h-full" required />                 
            </div>
        
            <div className="flex items-center mt-4 w-full bg-white border border-gray-300/80 h-12 rounded-full overflow-hidden pl-6 gap-2">
                <Lock className='w-4 h-4'/>
                <input type="password" placeholder="Password" className="bg-transparent text-gray-500 placeholder-gray-500 outline-none text-sm w-full h-full pr-4" required />                 
            </div>
            <div className="mt-5 text-left text-primary">
                <a className="text-sm" href="">Forgot password?</a>
            </div>
        
            <button type="submit" className="mt-2 w-full h-11 rounded-full text-white bg-primary hover:opacity-90 transition-opacity">
                Login
            </button> 
            <p className="text-gray-500 text-sm mt-3 mb-11">Don’t have an account? <a className="text-primary" href="#">Sign up</a></p>
        </form>
    </div>
  )
}

export default Login