import { Link } from 'react-router-dom'

export default function AuthLayout({ title, subtitle, children }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-ink-950 px-4 py-10">
      <div className="w-full max-w-md">
        <Link to="/" className="block text-center mb-8 text-2xl font-bold text-white">
          Fit<span className="text-brand-400">Fusion</span>
        </Link>
        <div className="rounded-2xl border border-ink-800 bg-ink-900 p-8">
          <h1 className="text-xl font-semibold text-white mb-1">{title}</h1>
          {subtitle && <p className="text-sm text-ink-400 mb-6">{subtitle}</p>}
          {children}
        </div>
      </div>
    </div>
  )
}
