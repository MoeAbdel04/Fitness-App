export default function StatCard({ label, value, sub, accent = 'brand' }) {
  const accentClasses = {
    brand: 'text-brand-400',
    amber: 'text-amber-400',
    sky: 'text-sky-400',
    rose: 'text-rose-400',
  }
  return (
    <div className="rounded-2xl border border-ink-800 bg-ink-900 p-5">
      <p className="text-xs uppercase tracking-wide text-ink-400 font-medium">{label}</p>
      <p className={`text-3xl font-bold mt-2 ${accentClasses[accent] || accentClasses.brand}`}>{value}</p>
      {sub && <p className="text-xs text-ink-500 mt-1">{sub}</p>}
    </div>
  )
}
