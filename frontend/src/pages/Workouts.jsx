import { useEffect, useState, useCallback } from 'react'
import client from '../api/client'

const inputClass =
  'w-full bg-ink-800 border border-ink-700 rounded-lg px-3 py-2 text-white placeholder-ink-500 outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent text-sm'

const emptyForm = { workout_type: 'Weight Training', exercise: '', sets: '', reps: '', weight: '' }

export default function Workouts() {
  const [exercises, setExercises] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [workouts, setWorkouts] = useState([])
  const [page, setPage] = useState(1)
  const [pages, setPages] = useState(1)
  const [editingId, setEditingId] = useState(null)
  const [editForm, setEditForm] = useState(emptyForm)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const loadWorkouts = useCallback((p = 1) => {
    client.get(`/workouts?page=${p}&per_page=10`).then((res) => {
      setWorkouts(res.data.workouts)
      setPage(res.data.page)
      setPages(res.data.pages || 1)
    })
  }, [])

  useEffect(() => {
    client.get('/exercises').then((res) => setExercises(res.data.exercises))
    loadWorkouts(1)
  }, [loadWorkouts])

  const update = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    try {
      await client.post('/workouts', form)
      setForm(emptyForm)
      setMessage('Workout logged!')
      loadWorkouts(1)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to log workout.')
    }
  }

  const startEdit = (w) => {
    setEditingId(w.id)
    setEditForm({ workout_type: w.workout_type, exercise: w.exercise, sets: w.sets, reps: w.reps, weight: w.weight_lbs || '' })
  }

  const saveEdit = async (id) => {
    await client.put(`/workouts/${id}`, editForm)
    setEditingId(null)
    loadWorkouts(page)
  }

  const deleteWorkout = async (id) => {
    if (!confirm('Delete this workout?')) return
    await client.delete(`/workouts/${id}`)
    loadWorkouts(page)
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      <h1 className="text-2xl font-bold text-white">Workouts</h1>

      <form onSubmit={handleSubmit} className="rounded-2xl border border-ink-800 bg-ink-900 p-5 space-y-4">
        <h2 className="text-white font-semibold">Log a workout</h2>
        {error && <div className="text-sm text-rose-400">{error}</div>}
        {message && <div className="text-sm text-brand-400">{message}</div>}
        <div className="grid sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs text-ink-400 mb-1">Type</label>
            <select className={inputClass} value={form.workout_type} onChange={update('workout_type')}>
              <option>Cardio</option>
              <option>Weight Training</option>
              <option>Strength Training</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-ink-400 mb-1">Exercise</label>
            <input list="exercise-options" required className={inputClass} value={form.exercise} onChange={update('exercise')} placeholder="e.g. Bench Press" />
            <datalist id="exercise-options">
              {exercises.map((ex) => (
                <option key={ex.id} value={ex.name} />
              ))}
            </datalist>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="block text-xs text-ink-400 mb-1">Sets</label>
            <input type="number" required min={1} className={inputClass} value={form.sets} onChange={update('sets')} />
          </div>
          <div>
            <label className="block text-xs text-ink-400 mb-1">Reps</label>
            <input type="number" required min={1} className={inputClass} value={form.reps} onChange={update('reps')} />
          </div>
          <div>
            <label className="block text-xs text-ink-400 mb-1">Weight (lbs)</label>
            <input type="number" min={0} className={inputClass} value={form.weight} onChange={update('weight')} />
          </div>
        </div>
        <button type="submit" className="px-4 py-2 rounded-lg bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium transition-colors">
          Log Workout
        </button>
      </form>

      <div className="rounded-2xl border border-ink-800 bg-ink-900 p-5">
        <h2 className="text-white font-semibold mb-4">History</h2>
        <div className="space-y-2">
          {workouts.map((w) => (
            <div key={w.id} className="border-b border-ink-800 last:border-0 py-2">
              {editingId === w.id ? (
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 items-center">
                  <input className={inputClass} value={editForm.exercise} onChange={(e) => setEditForm((f) => ({ ...f, exercise: e.target.value }))} />
                  <input type="number" className={inputClass} value={editForm.sets} onChange={(e) => setEditForm((f) => ({ ...f, sets: e.target.value }))} />
                  <input type="number" className={inputClass} value={editForm.reps} onChange={(e) => setEditForm((f) => ({ ...f, reps: e.target.value }))} />
                  <input type="number" className={inputClass} value={editForm.weight} onChange={(e) => setEditForm((f) => ({ ...f, weight: e.target.value }))} />
                  <div className="flex gap-2">
                    <button onClick={() => saveEdit(w.id)} className="text-xs px-2 py-1 rounded bg-brand-500 text-white">Save</button>
                    <button onClick={() => setEditingId(null)} className="text-xs px-2 py-1 rounded bg-ink-700 text-ink-200">Cancel</button>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-between text-sm gap-2 flex-wrap">
                  <div>
                    <span className="text-white font-medium">{w.exercise}</span>
                    <span className="text-ink-500 ml-2">{w.workout_type}</span>
                  </div>
                  <div className="text-ink-400">
                    {w.sets}×{w.reps}{w.weight_lbs ? ` @ ${w.weight_lbs} lbs` : ''}
                  </div>
                  <div className="text-ink-500">{w.date.slice(0, 10)}</div>
                  <div className="flex gap-2">
                    <button onClick={() => startEdit(w)} className="text-xs px-2 py-1 rounded bg-ink-800 text-ink-200 hover:bg-ink-700">Edit</button>
                    <button onClick={() => deleteWorkout(w.id)} className="text-xs px-2 py-1 rounded bg-rose-500/10 text-rose-400 hover:bg-rose-500/20">Delete</button>
                  </div>
                </div>
              )}
            </div>
          ))}
          {workouts.length === 0 && <p className="text-ink-500 text-sm py-6 text-center">No workouts logged yet.</p>}
        </div>
        {pages > 1 && (
          <div className="flex items-center justify-center gap-3 mt-4">
            <button disabled={page <= 1} onClick={() => loadWorkouts(page - 1)} className="text-sm px-3 py-1 rounded bg-ink-800 text-ink-200 disabled:opacity-40">
              Prev
            </button>
            <span className="text-sm text-ink-400">Page {page} of {pages}</span>
            <button disabled={page >= pages} onClick={() => loadWorkouts(page + 1)} className="text-sm px-3 py-1 rounded bg-ink-800 text-ink-200 disabled:opacity-40">
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
