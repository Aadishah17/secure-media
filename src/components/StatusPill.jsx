export function StatusPill({ tone, text }) {
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-semibold ${
        tone === 'positive'
          ? 'bg-emerald-100 text-emerald-800'
          : tone === 'negative'
            ? 'bg-rose-100 text-rose-800'
            : 'bg-slate-100 text-slate-700'
      }`}
    >
      <span
        className={`h-2.5 w-2.5 rounded-full ${
          tone === 'positive'
            ? 'bg-emerald-500'
            : tone === 'negative'
              ? 'bg-rose-500'
              : 'bg-slate-400'
        }`}
      />
      {text}
    </span>
  )
}
