import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import AuthLayout from '../components/AuthLayout'

const inputClass =
  'w-full bg-ink-800 border border-ink-700 rounded-lg px-3 py-2.5 text-white placeholder-ink-500 outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent'
const labelClass = 'block text-sm text-ink-300 mb-1'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    username: '', email: '', password: '', age: '', gender: 'male',
    feet: '5', inches: '8', weight_lbs: '', activity_level: 'moderate',
    workout_preference: 'weight_training', goal: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const update = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const heightMeters = ((parseFloat(form.feet) * 12) + parseFloat(form.inches)) * 0.0254
      await register({
        username: form.username,
        email: form.email,
        password: form.password,
        age: form.age,
        gender: form.gender,
        height: Number(heightMeters.toFixed(2)),
        weight_lbs: form.weight_lbs,
        activity_level: form.activity_level,
        workout_preference: form.workout_preference,
        goal: form.goal,
      })
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout title="Create your account" subtitle="Start tracking your fitness journey">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="text-sm text-rose-400 bg-rose-500/10 border border-rose-500/30 rounded-lg px-3 py-2">
            {error}
          </div>
        )}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={labelClass}>Username</label>
            <input required className={inputClass} value={form.username} onChange={update('username')} />
          </div>
          <div>
            <label className={labelClass}>Email</label>
            <input type="email" required className={inputClass} value={form.email} onChange={update('email')} />
          </div>
        </div>
        <div>
          <label className={labelClass}>Password</label>
          <input type="password" required minLength={6} className={inputClass} value={form.password} onChange={update('password')} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={labelClass}>Age</label>
            <input type="number" required min={13} max={110} className={inputClass} value={form.age} onChange={update('age')} />
          </div>
          <div>
            <label className={labelClass}>Gender</label>
            <select className={inputClass} value={form.gender} onChange={update('gender')}>
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className={labelClass}>Height (ft)</label>
            <input type="number" required min={3} max={8} className={inputClass} value={form.feet} onChange={update('feet')} />
          </div>
          <div>
            <label className={labelClass}>Height (in)</label>
            <input type="number" required min={0} max={11} className={inputClass} value={form.inches} onChange={update('inches')} />
          </div>
          <div>
            <label className={labelClass}>Weight (lbs)</label>
            <input type="number" required min={50} max={700} className={inputClass} value={form.weight_lbs} onChange={update('weight_lbs')} />
          </div>
        </div>
        <div>
          <label className={labelClass}>Activity Level</label>
          <select className={inputClass} value={form.activity_level} onChange={update('activity_level')}>
            <option value="sedentary">Sedentary</option>
            <option value="light">Lightly Active</option>
            <option value="moderate">Moderately Active</option>
            <option value="active">Active</option>
            <option value="very_active">Very Active</option>
          </select>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={labelClass}>Workout Preference</label>
            <select className={inputClass} value={form.workout_preference} onChange={update('workout_preference')}>
              <option value="cardio">Cardio</option>
              <option value="weight_training">Weight Training</option>
              <option value="strength_training">Strength Training</option>
            </select>
          </div>
          <div>
            <label className={labelClass}>Goal</label>
            <input placeholder="e.g. Lose weight" className={inputClass} value={form.goal} onChange={update('goal')} />
          </div>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-brand-500 hover:bg-brand-600 text-white font-medium rounded-lg py-2.5 transition-colors disabled:opacity-50"
        >
          {loading ? 'Creating account...' : 'Create Account'}
        </button>
      </form>
      <p className="text-sm text-ink-400 mt-6 text-center">
        Already have an account?{' '}
        <Link to="/login" className="text-brand-400 hover:text-brand-300 font-medium">
          Log in
        </Link>
      </p>
    </AuthLayout>
  )
}
