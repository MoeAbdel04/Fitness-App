import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import client from '../api/client'
import AuthLayout from '../components/AuthLayout'

const inputClass =
  'w-full bg-ink-800 border border-ink-700 rounded-lg px-3 py-2.5 text-white placeholder-ink-500 outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent'

export default function ForgotPassword() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await client.post('/auth/forgot-password', { email })
      navigate('/reset-password', { state: { resetToken: res.data.reset_token } })
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout title="Forgot password" subtitle="We'll verify your email so you can reset it on-site">
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
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-brand-500 hover:bg-brand-600 text-white font-medium rounded-lg py-2.5 transition-colors disabled:opacity-50"
        >
          {loading ? 'Verifying...' : 'Continue'}
        </button>
      </form>
      <p className="text-sm text-ink-400 mt-6 text-center">
        <Link to="/login" className="text-brand-400 hover:text-brand-300 font-medium">
          Back to login
        </Link>
      </p>
    </AuthLayout>
  )
}
