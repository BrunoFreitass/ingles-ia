export default function Brand({ size = 'md' }) {
  const dimensions = size === 'lg' ? 'w-20 h-20 text-sm' : 'w-14 h-14 text-xs'

  return (
    <div className="flex items-center gap-3">
      <div
        className={`${dimensions} shrink-0 rounded-full border-2 border-coral flex items-center justify-center -rotate-6 text-coral font-display font-semibold uppercase tracking-wide text-center leading-tight`}
        aria-hidden="true"
      >
        English
        <br />
        IA
      </div>
      <div>
        <p className="font-display text-2xl font-semibold text-ink leading-none">Inglês IA</p>
        <p className="font-mono text-[11px] text-charcoal-soft tracking-wide uppercase mt-1">
          seu caderno de estudos
        </p>
      </div>
    </div>
  )
}