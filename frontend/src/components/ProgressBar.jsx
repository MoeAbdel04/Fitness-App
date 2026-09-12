export default function ProgressBar({ percent = 0, color = 'bg-brand-500' }) {
  const clamped = Math.max(0, Math.min(100, percent))
  return (
    <div className="w-full h-2 rounded-full bg-ink-800 overflow-hidden">
      <div
        className={`h-full ${color} rounded-full transition-all duration-500`}
        style={{ width: `${clamped}%` }}
      />
    </div>
  )
}
