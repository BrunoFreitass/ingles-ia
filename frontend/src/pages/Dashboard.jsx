import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listarNiveis } from '../api/levels'
import Header from '../components/Header'

function IconeCadeado({ className = '' }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={className}>
      <rect x="4" y="10" width="16" height="10" rx="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3" strokeLinecap="round" />
    </svg>
  )
}

function IconeCheck({ className = '' }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={className}>
      <path d="m5 13 4 4L19 7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export default function Dashboard() {
  const [niveis, setNiveis] = useState(null)
  const [erro, setErro] = useState('')

  useEffect(() => {
    listarNiveis()
      .then(setNiveis)
      .catch(() => setErro('Não foi possível carregar seus níveis. Tente recarregar a página.'))
  }, [])

  return (
    <div className="min-h-screen">
      <Header />

      <main className="max-w-3xl mx-auto px-4 py-10">
        <h1 className="font-display text-3xl font-semibold text-ink mb-1">Sua trilha de estudo</h1>
        <p className="text-charcoal-soft mb-10">Siga os níveis em ordem — cada um libera o próximo.</p>

        {erro && <p className="text-coral">{erro}</p>}

        {!niveis && !erro && <p className="text-charcoal-soft">Carregando sua trilha...</p>}

        {niveis && (
          <div className="space-y-14">
            {niveis.map((nivel) => (
              <section key={nivel.id} className={!nivel.liberado ? 'opacity-50' : ''}>
                <div className="flex items-center gap-3 mb-1">
                  <span className="font-mono text-xs text-coral font-medium">
                    NÍVEL {String(nivel.ordem).padStart(2, '0')}
                  </span>
                  <h2 className="font-display text-xl font-semibold text-ink">{nivel.nome}</h2>
                  {nivel.concluido && (
                    <span className="flex items-center gap-1 text-xs font-medium text-leaf bg-leaf/10 rounded-full px-2 py-0.5">
                      <IconeCheck className="w-3 h-3" /> Concluído
                    </span>
                  )}
                  {!nivel.liberado && <IconeCadeado className="w-4 h-4 text-charcoal-soft" />}
                </div>
                {nivel.descricao && (
                  <p className="text-sm text-charcoal-soft mb-6">{nivel.descricao}</p>
                )}

                {!nivel.liberado && (
                  <p className="text-sm text-charcoal-soft mb-4 italic">
                    Complete o nível anterior pra desbloquear.
                  </p>
                )}

                {/* Trilha vertical: linha conectando os nós de cada lição */}
                <ol className="relative border-l-2 border-sand-dark ml-3 space-y-1">
                  {nivel.lessons.map((licao) =>
                    nivel.liberado ? (
                      <li key={licao.id} className="relative pl-6 py-3">
                        <span
                          className="absolute -left-[9px] top-4 w-4 h-4 rounded-full bg-ink border-2 border-sand"
                          aria-hidden="true"
                        />
                        <Link
                          to={`/niveis/${nivel.id}/licoes/${licao.id}`}
                          className="group block rounded-xl border border-sand-dark bg-white px-4 py-3 hover:border-ink transition-colors"
                        >
                          <p className="font-medium text-charcoal group-hover:text-ink transition-colors">
                            {licao.titulo}
                          </p>
                          <p className="text-sm text-charcoal-soft mt-0.5">{licao.tema}</p>
                        </Link>
                      </li>
                    ) : (
                      <li key={licao.id} className="relative pl-6 py-3">
                        <span
                          className="absolute -left-[9px] top-4 w-4 h-4 rounded-full bg-charcoal-soft border-2 border-sand"
                          aria-hidden="true"
                        />
                        <div className="rounded-xl border border-sand-dark bg-white/50 px-4 py-3 cursor-not-allowed">
                          <p className="font-medium text-charcoal-soft">{licao.titulo}</p>
                          <p className="text-sm text-charcoal-soft mt-0.5">{licao.tema}</p>
                        </div>
                      </li>
                    )
                  )}
                </ol>
              </section>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
