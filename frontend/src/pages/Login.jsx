import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import AuthLayout from '../components/AuthLayout'

const inputClass =
  'w-full bg-ink-800 border border-ink-700 rounded-lg px-3 py-2.5 text-white placeholder-ink-500 outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout title="Welcome back" subtitle="Log in to continue your progress">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="text-sm text-rose-400 bg-rose-500/10 border border-rose-500/30 rounded-lg px-3 py-2">
            {error}
          </div>
        )}
        <div>
          <label className="block text-sm text-ink-300 mb-1">Email</label>
          <input type="email" required className={inputClass} value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div>
          <label className="block text-sm text-ink-300 mb-1">Password</label>
          <input type="password" required className={inputClass} value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <div className="text-right">
          <Link to="/forgot-password" className="text-sm text-brand-400 hover:text-brand-300">
            Forgot password?
          </Link>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-brand-500 hover:bg-brand-600 text-white font-medium rounded-lg py-2.5 transition-colors disabled:opacity-50"
        >
          {loading ? 'Logging in...' : 'Log In'}
        </button>
      </form>
      <p className="text-sm text-ink-400 mt-6 text-center">
        Don't have an account?{' '}
        <Link to="/register" className="text-brand-400 hover:text-brand-300 font-medium">
          Sign up
        </Link>
      </p>
    </AuthLayout>
  )
}
