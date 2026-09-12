import { useEffect, useState } from 'react'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'

const inputClass =
  'w-full bg-ink-800 border border-ink-700 rounded-lg px-3 py-2.5 text-white placeholder-ink-500 outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent'
const labelClass = 'block text-sm text-ink-300 mb-1'

export default function Profile() {
  const { refreshUser } = useAuth()
  const [form, setForm] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    client.get('/profile').then((res) => {
      const u = res.data.user
      setForm({
        username: u.username,
        email: u.email,
        age: u.age,
        gender: u.gender,
        feet: u.height_feet,
        inches: u.height_inches,
        weight_lbs: u.weight_lbs,
        activity_level: u.activity_level,
        workout_preference: u.workout_preference || '',
        goal: u.goal || '',
      })
    })
  }, [])

  if (!form) return <p className="text-ink-400 px-4 py-10 text-center">Loading profile...</p>

  const update = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    try {
      await client.put('/profile', form)
      await refreshUser()
      setMessage('Profile updated successfully!')
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update profile.')
    }
  }

  const downloadData = async () => {
    const res = await client.get('/profile/download', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'user_data.json')
    document.body.appendChild(link)
    link.click()
    link.remove()
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
      <h1 className="text-2xl font-bold text-white">Profile</h1>

      <form onSubmit={handleSubmit} className="rounded-2xl border border-ink-800 bg-ink-900 p-6 space-y-4">
        {error && <div className="text-sm text-rose-400">{error}</div>}
        {message && <div className="text-sm text-brand-400">{message}</div>}
        <div className="grid sm:grid-cols-2 gap-3">
          <div>
            <label className={labelClass}>Username</label>
            <input className={inputClass} value={form.username} onChange={update('username')} />
          </div>
          <div>
            <label className={labelClass}>Email</label>
            <input type="email" className={inputClass} value={form.email} onChange={update('email')} />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={labelClass}>Age</label>
            <input type="number" className={inputClass} value={form.age} onChange={update('age')} />
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
            <input type="number" className={inputClass} value={form.feet} onChange={update('feet')} />
          </div>
          <div>
            <label className={labelClass}>Height (in)</label>
            <input type="number" className={inputClass} value={form.inches} onChange={update('inches')} />
          </div>
          <div>
            <label className={labelClass}>Weight (lbs)</label>
            <input type="number" className={inputClass} value={form.weight_lbs} onChange={update('weight_lbs')} />
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
            <input className={inputClass} value={form.goal} onChange={update('goal')} />
          </div>
        </div>
        <button type="submit" className="px-4 py-2 rounded-lg bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium transition-colors">
          Save Changes
        </button>
      </form>

      <div className="rounded-2xl border border-ink-800 bg-ink-900 p-6 flex items-center justify-between">
        <div>
          <p className="text-white font-medium">Download your data</p>
          <p className="text-sm text-ink-500">Export your profile, workouts, goals, and nutrition logs as JSON.</p>
        </div>
        <button onClick={downloadData} className="px-4 py-2 rounded-lg bg-ink-800 hover:bg-ink-700 text-ink-200 text-sm font-medium transition-colors">
          Download
        </button>
      </div>
    </div>
  )
}
