import { Lock, Mail, User } from 'lucide-react'
import React, { useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'

const Login = () => {
    const navigate = useNavigate()
    const { login, register, isAuthenticated, loading: authLoading } = useAuth()
    const [mode, setMode] = useState('login')
    const [name, setName] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [submitting, setSubmitting] = useState(false)
    const [error, setError] = useState('')

    useEffect(() => {
        if (!authLoading && isAuthenticated) {
            navigate('/dashboard')
        }
    }, [authLoading, isAuthenticated, navigate])

    const handleSubmit = async (event) => {
        event.preventDefault()
        setError('')
        setSubmitting(true)
        try {
            if (mode === 'login') {
                await login(email, password)
            } else {
                await register(name, email, password)
            }
            navigate('/analyze')
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Authentication failed')
        } finally {
            setSubmitting(false)
        }
    }

    const toggleMode = () => {
        setMode((prev) => (prev === 'login' ? 'register' : 'login'))
        setError('')
    }

  return (
        <div className='py-24 px-4 sm:px-20 xl:px-32 bg-[url(/bg.svg)] bg-black min-h-screen flex items-center justify-center'>
            <form onSubmit={handleSubmit} className="max-w-[420px] w-full text-center border border-white/10 rounded-2xl px-8 bg-white/5 backdrop-blur mx-auto py-12 flex flex-col gap-5">
                <div className="space-y-2">
                    <h1 className="text-white text-3xl font-medium">
                        {mode === 'login' ? 'Welcome back' : 'Create an account'}
                    </h1>
                    <p className="text-gray-400 text-sm">
                        {mode === 'login'
                            ? 'Sign in to access your personalized analyses.'
                            : 'Sign up to save insights and revisit them anytime.'}
                    </p>
                </div>

                {mode === 'register' ? (
                    <div className="flex items-center bg-white border border-gray-200/60 h-12 rounded-full overflow-hidden pl-6 gap-2">
                        <User className='w-4 h-4 text-gray-600'/>
                        <input
                            type="text"
                            placeholder="Full name"
                            className="bg-transparent text-gray-700 placeholder-gray-500 outline-none text-sm w-full h-full"
                            value={name}
                            onChange={(event) => setName(event.target.value)}
                            required
                        />
                    </div>
                ) : null}

                <div className="flex items-center bg-white border border-gray-200/60 h-12 rounded-full overflow-hidden pl-6 gap-2">
                    <Mail className='w-4 h-4 text-gray-600'/>
                    <input
                        type="email"
                        placeholder="Email address"
                        className="bg-transparent text-gray-700 placeholder-gray-500 outline-none text-sm w-full h-full"
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                        required
                    />
                </div>

                <div className="flex items-center bg-white border border-gray-200/60 h-12 rounded-full overflow-hidden pl-6 gap-2">
                    <Lock className='w-4 h-4 text-gray-600'/>
                    <input
                        type="password"
                        placeholder="Password"
                        className="bg-transparent text-gray-700 placeholder-gray-500 outline-none text-sm w-full h-full pr-4"
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                        required
                        minLength={8}
                    />
                </div>

                {error ? (
                    <div className="text-sm text-rose-200 bg-rose-500/10 border border-rose-400/40 rounded-lg py-2 px-3">
                        {error}
                    </div>
                ) : null}

                <button
                    type="submit"
                    disabled={submitting}
                    className="mt-2 w-full h-12 rounded-full text-white bg-primary hover:opacity-90 transition-opacity disabled:opacity-50"
                >
                    {submitting ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}
                </button>

                <p className="text-gray-300 text-sm">
                    {mode === 'login' ? (
                        <>Don’t have an account?{' '}
                            <button type="button" onClick={toggleMode} className="text-primary underline">
                                Sign up
                            </button>
                        </>
                    ) : (
                        <>Already registered?{' '}
                            <button type="button" onClick={toggleMode} className="text-primary underline">
                                Sign in
                            </button>
                        </>
                    )}
                </p>
            </form>
        </div>
  )
}

export default Login