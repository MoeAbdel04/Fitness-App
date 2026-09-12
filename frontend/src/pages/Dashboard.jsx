import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from 'recharts'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'
import StatCard from '../components/StatCard'

export default function Dashboard() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    client.get('/workouts/dashboard')
      .then((res) => setData(res.data))
      .catch(() => setError('Could not load dashboard data.'))
  }, [])

  if (error) return <p className="text-rose-400 px-4 py-10 text-center">{error}</p>
  if (!data) return <p className="text-ink-400 px-4 py-10 text-center">Loading dashboard...</p>

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Welcome back, {user?.username}</h1>
        <p className="text-ink-400 mt-1">{data.recommended_workout}</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="BMI" value={data.bmi ?? '--'} sub="Body Mass Index" accent="brand" />
        <StatCard label="Weight" value={`${data.weight_lbs} lbs`} sub="Current weight" accent="sky" />
        <StatCard label="TDEE" value={`${data.tdee} kcal`} sub="Maintenance calories" accent="amber" />
        <StatCard label="Workouts Logged" value={data.total_workouts} sub="All time" accent="rose" />
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Object.entries(data.calorie_plans).map(([key, value]) => (
          <div key={key} className="rounded-xl border border-ink-800 bg-ink-900 px-4 py-3">
            <p className="text-xs text-ink-500 uppercase tracking-wide">{key.replace('_', ' ')}</p>
            <p className="text-lg font-semibold text-white">{value} kcal</p>
          </div>
        ))}
      </div>

      <div className="rounded-2xl border border-ink-800 bg-ink-900 p-5">
        <h2 className="text-white font-semibold mb-4">Weight & BMI Trend</h2>
        {data.chart_series.length > 0 ? (
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={data.chart_series}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
              <YAxis yAxisId="left" stroke="#34d399" fontSize={12} />
              <YAxis yAxisId="right" orientation="right" stroke="#f87171" fontSize={12} />
              <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8 }} />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="weight_lbs" name="Weight (lbs)" stroke="#34d399" strokeWidth={2} dot={{ r: 3 }} />
              <Line yAxisId="right" type="monotone" dataKey="bmi" name="BMI" stroke="#f87171" strokeWidth={2} strokeDasharray="5 4" dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-ink-500 text-sm py-10 text-center">
            Log a workout with a weight entry to see your progress chart.
          </p>
        )}
      </div>

      <div className="rounded-2xl border border-ink-800 bg-ink-900 p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-white font-semibold">Recent Workouts</h2>
          <Link to="/workouts" className="text-sm text-brand-400 hover:text-brand-300">
            View all
          </Link>
        </div>
        {data.recent_workouts.length > 0 ? (
          <div className="space-y-2">
            {data.recent_workouts.map((w) => (
              <div key={w.id} className="flex items-center justify-between text-sm py-2 border-b border-ink-800 last:border-0">
                <div>
                  <span className="text-white font-medium">{w.exercise}</span>
                  <span className="text-ink-500 ml-2">{w.workout_type}</span>
                </div>
                <div className="text-ink-400">
                  {w.sets}×{w.reps}{w.weight_lbs ? ` @ ${w.weight_lbs} lbs` : ''}
                </div>
                <div className="text-ink-500">{w.date.slice(0, 10)}</div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-ink-500 text-sm py-6 text-center">No workouts logged yet.</p>
        )}
      </div>
    </div>
  )
}
