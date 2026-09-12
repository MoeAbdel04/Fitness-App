import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import client from '../api/client'
import AuthLayout from '../components/AuthLayout'

const inputClass =
  'w-full bg-ink-800 border border-ink-700 rounded-lg px-3 py-2.5 text-white placeholder-ink-500 outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent'

export default function ResetPassword() {
  const location = useLocation()
  const navigate = useNavigate()
  const resetToken = location.state?.resetToken
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)

  if (!resetToken) {
    return (
      <AuthLayout title="Reset password">
        <p className="text-sm text-ink-400">
          Please start from the{' '}
          <Link to="/forgot-password" className="text-brand-400">
            forgot password
          </Link>{' '}
          form first.
        </p>
      </AuthLayout>
    )
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await client.post('/auth/reset-password', { reset_token: resetToken, password })
      setSuccess(true)
      setTimeout(() => navigate('/login'), 1500)
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout title="Reset your password">
      {success ? (
        <p className="text-sm text-brand-400">Password updated! Redirecting to login...</p>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="text-sm text-rose-400 bg-rose-500/10 border border-rose-500/30 rounded-lg px-3 py-2">
              {error}
            </div>
          )}
          <div>
            <label className="block text-sm text-ink-300 mb-1">New Password</label>
            <input type="password" required minLength={6} className={inputClass} value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-brand-500 hover:bg-brand-600 text-white font-medium rounded-lg py-2.5 transition-colors disabled:opacity-50"
          >
            {loading ? 'Updating...' : 'Update Password'}
          </button>
        </form>
      )}
    </AuthLayout>
  )
}
