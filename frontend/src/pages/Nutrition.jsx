import { useEffect, useState } from 'react'
import client from '../api/client'
import ProgressBar from '../components/ProgressBar'
import StatCard from '../components/StatCard'

const inputClass =
  'w-full bg-ink-800 border border-ink-700 rounded-lg px-3 py-2 text-white placeholder-ink-500 outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent text-sm'

const emptyForm = { food_name: '', calories: '', protein: '', carbs: '', fat: '', meal_type: 'lunch' }

const today = () => new Date().toISOString().slice(0, 10)

export default function Nutrition() {
  const [date, setDate] = useState(today())
  const [data, setData] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState('')

  const load = (d) => client.get(`/nutrition?date=${d}`).then((res) => setData(res.data))

  useEffect(() => {
    load(date)
  }, [date])

  const update = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await client.post('/nutrition', { ...form, date })
      setForm(emptyForm)
      load(date)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to log food.')
    }
  }

  const deleteLog = async (id) => {
    await client.delete(`/nutrition/${id}`)
    load(date)
  }

  const percent = data ? Math.min(100, Math.round((data.total_calories / data.tdee_target) * 100)) : 0

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="text-2xl font-bold text-white">Nutrition</h1>
        <input type="date" value={date} onChange={(e) => setDate(e.target.value)} className={`${inputClass} w-auto`} />
      </div>

      {data && (
        <>
          <div className="grid sm:grid-cols-3 gap-4">
            <StatCard label="Calories" value={`${Math.round(data.total_calories)}`} sub={`Target: ${data.tdee_target}`} accent="brand" />
            <StatCard label="Protein" value={`${Math.round(data.total_protein)}g`} accent="sky" />
            <StatCard label="Remaining" value={`${data.remaining_calories}`} sub="kcal left today" accent="amber" />
          </div>
          <div className="rounded-2xl border border-ink-800 bg-ink-900 p-5">
            <ProgressBar percent={percent} color={percent > 100 ? 'bg-rose-500' : 'bg-brand-500'} />
            <p className="text-xs text-ink-500 mt-2">{percent}% of daily calorie target</p>
          </div>
        </>
      )}

      <form onSubmit={handleSubmit} className="rounded-2xl border border-ink-800 bg-ink-900 p-5 space-y-4">
        <h2 className="text-white font-semibold">Log food</h2>
        {error && <div className="text-sm text-rose-400">{error}</div>}
        <div className="grid sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs text-ink-400 mb-1">Food</label>
            <input required className={inputClass} value={form.food_name} onChange={update('food_name')} placeholder="e.g. Grilled chicken" />
          </div>
          <div>
            <label className="block text-xs text-ink-400 mb-1">Meal</label>
            <select className={inputClass} value={form.meal_type} onChange={update('meal_type')}>
              <option value="breakfast">Breakfast</option>
              <option value="lunch">Lunch</option>
              <option value="dinner">Dinner</option>
              <option value="snack">Snack</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div>
            <label className="block text-xs text-ink-400 mb-1">Calories</label>
            <input type="number" required min={0} className={inputClass} value={form.calories} onChange={update('calories')} />
          </div>
          <div>
            <label className="block text-xs text-ink-400 mb-1">Protein (g)</label>
            <input type="number" min={0} className={inputClass} value={form.protein} onChange={update('protein')} />
          </div>
          <div>
            <label className="block text-xs text-ink-400 mb-1">Carbs (g)</label>
            <input type="number" min={0} className={inputClass} value={form.carbs} onChange={update('carbs')} />
          </div>
          <div>
            <label className="block text-xs text-ink-400 mb-1">Fat (g)</label>
            <input type="number" min={0} className={inputClass} value={form.fat} onChange={update('fat')} />
          </div>
        </div>
        <button type="submit" className="px-4 py-2 rounded-lg bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium transition-colors">
          Log Food
        </button>
      </form>

      <div className="rounded-2xl border border-ink-800 bg-ink-900 p-5">
        <h2 className="text-white font-semibold mb-4">Today's log</h2>
        <div className="space-y-2">
          {data?.logs.map((l) => (
            <div key={l.id} className="flex items-center justify-between text-sm py-2 border-b border-ink-800 last:border-0">
              <div>
                <span className="text-white font-medium">{l.food_name}</span>
                <span className="text-ink-500 ml-2 capitalize">{l.meal_type}</span>
              </div>
              <div className="text-ink-400">{l.calories} kcal</div>
              <button onClick={() => deleteLog(l.id)} className="text-xs px-2 py-1 rounded bg-rose-500/10 text-rose-400 hover:bg-rose-500/20">
                Delete
              </button>
            </div>
          ))}
          {data?.logs.length === 0 && <p className="text-ink-500 text-sm py-6 text-center">Nothing logged for this day.</p>}
        </div>
      </div>
    </div>
  )
}
