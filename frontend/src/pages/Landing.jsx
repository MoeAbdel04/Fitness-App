import { Link } from 'react-router-dom'

const features = [
  { title: 'Workout Tracking', desc: 'Log sets, reps, and weight with an exercise library at your fingertips.' },
  { title: 'Goal Setting', desc: 'Set weight, strength, or custom goals and watch your progress bar fill up.' },
  { title: 'Nutrition Logging', desc: 'Track meals and calories against your personalized TDEE target.' },
  { title: 'Interactive Charts', desc: 'Visualize your weight and BMI trends over time.' },
  { title: 'Fit Bot', desc: 'Get quick, friendly AI-powered fitness and nutrition advice.' },
  { title: 'Exercise Library', desc: 'Browse exercises by muscle group, equipment, and difficulty.' },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-ink-950">
      <header className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <span className="text-lg font-bold text-white">
          Fit<span className="text-brand-400">Fusion</span>
        </span>
        <div className="flex items-center gap-3">
          <Link to="/login" className="text-sm text-ink-300 hover:text-white px-3 py-2">
            Log in
          </Link>
          <Link
            to="/register"
            className="text-sm font-medium text-white bg-brand-500 hover:bg-brand-600 px-4 py-2 rounded-lg transition-colors"
          >
            Get Started
          </Link>
        </div>
      </header>

      <section className="max-w-4xl mx-auto px-4 pt-16 pb-20 text-center">
        <h1 className="text-4xl sm:text-5xl font-bold text-white tracking-tight">
          Fitness tracking, <span className="text-brand-400">fully fused</span>.
        </h1>
        <p className="mt-4 text-lg text-ink-400 max-w-2xl mx-auto">
          Track workouts, hit your goals, log nutrition, and chat with Fit Bot — all in one modern dashboard.
        </p>
        <div className="mt-8 flex items-center justify-center gap-4">
          <Link
            to="/register"
            className="px-6 py-3 rounded-lg bg-brand-500 hover:bg-brand-600 text-white font-semibold transition-colors"
          >
            Start for free
          </Link>
          <Link
            to="/login"
            className="px-6 py-3 rounded-lg border border-ink-700 text-ink-200 hover:bg-ink-800 font-semibold transition-colors"
          >
            I have an account
          </Link>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-4 pb-24 grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {features.map((f) => (
          <div key={f.title} className="rounded-2xl border border-ink-800 bg-ink-900 p-6">
            <h3 className="text-white font-semibold mb-2">{f.title}</h3>
            <p className="text-sm text-ink-400">{f.desc}</p>
          </div>
        ))}
      </section>
    </div>
  )
}
