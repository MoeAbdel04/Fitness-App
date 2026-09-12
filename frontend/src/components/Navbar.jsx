import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useState } from 'react'

const links = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/workouts', label: 'Workouts' },
  { to: '/goals', label: 'Goals' },
  { to: '/exercises', label: 'Exercises' },
  { to: '/nutrition', label: 'Nutrition' },
  { to: '/profile', label: 'Profile' },
]

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)

  if (!user) return null

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const linkClass = ({ isActive }) =>
    `px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
      isActive ? 'bg-brand-500/15 text-brand-400' : 'text-ink-300 hover:text-white hover:bg-ink-800'
    }`

  return (
    <header className="sticky top-0 z-40 border-b border-ink-800 bg-ink-950/90 backdrop-blur">
      <div className="max-w-6xl mx-auto px-4 flex items-center justify-between h-16">
        <div className="flex items-center gap-6">
          <span className="text-lg font-bold text-white tracking-tight">
            Fit<span className="text-brand-400">Fusion</span>
          </span>
          <nav className="hidden md:flex items-center gap-1">
            {links.map((l) => (
              <NavLink key={l.to} to={l.to} className={linkClass}>
                {l.label}
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="hidden md:flex items-center gap-3">
          <span className="text-sm text-ink-400">Hi, {user.username}</span>
          <button
            onClick={handleLogout}
            className="px-3 py-2 rounded-lg text-sm font-medium bg-ink-800 text-ink-200 hover:bg-ink-700 transition-colors"
          >
            Log out
          </button>
        </div>
        <button
          className="md:hidden text-ink-200 p-2"
          onClick={() => setOpen((o) => !o)}
          aria-label="Toggle menu"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 6h16M4 12h16M4 18h16" strokeLinecap="round" />
          </svg>
        </button>
      </div>
      {open && (
        <div className="md:hidden border-t border-ink-800 px-4 py-3 flex flex-col gap-1">
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} className={linkClass} onClick={() => setOpen(false)}>
              {l.label}
            </NavLink>
          ))}
          <button
            onClick={handleLogout}
            className="mt-2 px-3 py-2 rounded-lg text-sm font-medium bg-ink-800 text-ink-200 text-left"
          >
            Log out
          </button>
        </div>
      )}
    </header>
  )
}
