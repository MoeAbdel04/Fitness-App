import { useEffect, useState } from 'react'
import client from '../api/client'
import ProgressBar from '../components/ProgressBar'

const inputClass =
  'w-full bg-ink-800 border border-ink-700 rounded-lg px-3 py-2 text-white placeholder-ink-500 outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent text-sm'

const emptyForm = { goal_type: 'weight', title: '', start_value: '', target_value: '', unit: 'lbs', target_date: '' }

export default function Goals() {
  const [goals, setGoals] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState('')
  const [updatingId, setUpdatingId] = useState(null)
  const [progressInput, setProgressInput] = useState('')

  const load = () => client.get('/goals').then((res) => setGoals(res.data.goals))

  useEffect(() => {
    load()
  }, [])

  const update = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await client.post('/goals', form)
      setForm(emptyForm)
      load()
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create goal.')
    }
  }

  const updateProgress = async (id) => {
    await client.put(`/goals/${id}`, { current_value: progressInput })
    setUpdatingId(null)
    setProgressInput('')
    load()
  }

  const deleteGoal = async (id) => {
    if (!confirm('Delete this goal?')) return
    await client.delete(`/goals/${id}`)
    load()
  }

  const activeGoals = goals.filter((g) => g.status !== 'completed')
  const completedGoals = goals.filter((g) => g.status === 'completed')

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      <h1 className="text-2xl font-bold text-white">Goals</h1>

      <form onSubmit={handleSubmit} className="rounded-2xl border border-ink-800 bg-ink-900 p-5 space-y-4">
        <h2 className="text-white font-semibold">Create a goal</h2>
        {error && <div className="text-sm text-rose-400">{error}</div>}
        <div className="grid sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs text-ink-400 mb-1">Type</label>
            <select className={inputClass} value={form.goal_type} onChange={update('goal_type')}>
              <option value="weight">Weight</option>
              <option value="strength">Strength</option>
              <option value="workout_count">Workout Count</option>
              <option value="custom">Custom</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-ink-400 mb-1">Title</label>
            <input required className={inputClass} value={form.title} onChange={update('title')} placeholder="e.g. Bench 225 lbs" />
          </div>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div>
            <label className="block text-xs text-ink-400 mb-1">Start value</label>
            <input type="number" className={inputClass} value={form.start_value} onChange={update('start_value')} />
          </div>
          <div>
            <label className="block text-xs text-ink-400 mb-1">Target value</label>
            <input type="number" required className={inputClass} value={form.target_value} onChange={update('target_value')} />
          </div>
          <div>
            <label className="block text-xs text-ink-400 mb-1">Unit</label>
            <input className={inputClass} value={form.unit} onChange={update('unit')} placeholder="lbs, reps..." />
          </div>
          <div>
            <label className="block text-xs text-ink-400 mb-1">Target date</label>
            <input type="date" className={inputClass} value={form.target_date} onChange={update('target_date')} />
          </div>
        </div>
        <button type="submit" className="px-4 py-2 rounded-lg bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium transition-colors">
          Create Goal
        </button>
      </form>

      <div className="space-y-4">
        <h2 className="text-white font-semibold">Active goals</h2>
        {activeGoals.length === 0 && <p className="text-ink-500 text-sm">No active goals yet — create one above.</p>}
        {activeGoals.map((g) => (
          <div key={g.id} className="rounded-2xl border border-ink-800 bg-ink-900 p-5">
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="text-white font-medium">{g.title}</p>
                <p className="text-xs text-ink-500">
                  {g.current_value ?? '--'} → {g.target_value} {g.unit || ''}
                  {g.target_date ? ` · by ${g.target_date}` : ''}
                </p>
              </div>
              <div className="flex gap-2">
                {updatingId === g.id ? (
                  <>
                    <input
                      type="number"
                      className="w-24 bg-ink-800 border border-ink-700 rounded px-2 py-1 text-sm text-white"
                      value={progressInput}
                      onChange={(e) => setProgressInput(e.target.value)}
                      placeholder="Current"
                    />
                    <button onClick={() => updateProgress(g.id)} className="text-xs px-2 py-1 rounded bg-brand-500 text-white">Save</button>
                  </>
                ) : (
                  <button onClick={() => { setUpdatingId(g.id); setProgressInput(g.current_value ?? '') }} className="text-xs px-2 py-1 rounded bg-ink-800 text-ink-200 hover:bg-ink-700">
                    Update progress
                  </button>
                )}
                <button onClick={() => deleteGoal(g.id)} className="text-xs px-2 py-1 rounded bg-rose-500/10 text-rose-400 hover:bg-rose-500/20">Delete</button>
              </div>
            </div>
            <ProgressBar percent={g.progress_percent} />
            <p className="text-xs text-ink-500 mt-1">{g.progress_percent}% complete</p>
          </div>
        ))}
      </div>

      {completedGoals.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-white font-semibold">Completed</h2>
          {completedGoals.map((g) => (
            <div key={g.id} className="rounded-xl border border-brand-500/30 bg-brand-500/5 px-4 py-3 flex items-center justify-between">
              <span className="text-white">{g.title}</span>
              <span className="text-brand-400 text-sm">✓ Achieved</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
