import { ttsDisponivel, falarIngles } from '../utils/speech'

/**
 * Botão pequeno de alto-falante — toca o texto em inglês ao clicar.
 * Renderiza null silenciosamente se o navegador não suportar TTS,
 * em vez de mostrar um botão quebrado.
 */
export default function SpeakerButton({ texto, className = '' }) {
  if (!ttsDisponivel() || !texto) return null

  return (
    <button
      type="button"
      onClick={(e) => {
        e.stopPropagation() // evita disparar cliques do elemento pai (ex: virar flashcard)
        falarIngles(texto)
      }}
      title="Ouvir pronúncia"
      aria-label="Ouvir pronúncia em inglês"
      className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-ink hover:bg-ink hover:text-white transition-colors shrink-0 ${className}`}
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
        <path d="M11 5 6 9H3v6h3l5 4V5Z" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M15.5 8.5a5 5 0 0 1 0 7" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M18 6a9 9 0 0 1 0 12" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </button>
  )
}