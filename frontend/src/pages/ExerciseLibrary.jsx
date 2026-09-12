import { useEffect, useState } from 'react'
import client from '../api/client'

const difficultyColor = {
  Beginner: 'bg-brand-500/15 text-brand-400',
  Intermediate: 'bg-amber-500/15 text-amber-400',
  Advanced: 'bg-rose-500/15 text-rose-400',
}

export default function ExerciseLibrary() {
  const [exercises, setExercises] = useState([])
  const [categories, setCategories] = useState([])
  const [muscleGroups, setMuscleGroups] = useState([])
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [muscleGroup, setMuscleGroup] = useState('')

  useEffect(() => {
    const params = new URLSearchParams()
    if (search) params.set('search', search)
    if (category) params.set('category', category)
    if (muscleGroup) params.set('muscle_group', muscleGroup)
    const timeout = setTimeout(() => {
      client.get(`/exercises?${params.toString()}`).then((res) => {
        setExercises(res.data.exercises)
        setCategories(res.data.categories)
        setMuscleGroups(res.data.muscle_groups)
      })
    }, 200)
    return () => clearTimeout(timeout)
  }, [search, category, muscleGroup])

  const selectClass = 'bg-ink-800 border border-ink-700 rounded-lg px-3 py-2 text-sm text-white outline-none focus:ring-2 focus:ring-brand-500'

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      <h1 className="text-2xl font-bold text-white">Exercise Library</h1>

      <div className="flex flex-wrap gap-3">
        <input
          placeholder="Search exercises..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 min-w-[200px] bg-ink-800 border border-ink-700 rounded-lg px-3 py-2 text-sm text-white placeholder-ink-500 outline-none focus:ring-2 focus:ring-brand-500"
        />
        <select className={selectClass} value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">All Categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
        <select className={selectClass} value={muscleGroup} onChange={(e) => setMuscleGroup(e.target.value)}>
          <option value="">All Muscle Groups</option>
          {muscleGroups.map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {exercises.map((ex) => (
          <div key={ex.id} className="rounded-2xl border border-ink-800 bg-ink-900 p-5">
            <div className="flex items-start justify-between gap-2">
              <h3 className="text-white font-semibold">{ex.name}</h3>
              {ex.difficulty && (
                <span className={`text-xs px-2 py-1 rounded-full whitespace-nowrap ${difficultyColor[ex.difficulty] || 'bg-ink-800 text-ink-300'}`}>
                  {ex.difficulty}
                </span>
              )}
            </div>
            <p className="text-xs text-ink-500 mt-1">{ex.category} · {ex.muscle_group} · {ex.equipment}</p>
            {ex.instructions && <p className="text-sm text-ink-400 mt-3">{ex.instructions}</p>}
          </div>
        ))}
        {exercises.length === 0 && <p className="text-ink-500 text-sm col-span-full text-center py-10">No exercises found.</p>}
      </div>
    </div>
  )
}
