import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listarCapitulos } from '../api/capitulos'
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

function IconeTrofeu({ className = '' }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={className}>
      <path d="M8 4h8v4a4 4 0 0 1-8 0V4Z" />
      <path d="M8 5H5a2 2 0 0 0 0 4h1M16 5h3a2 2 0 0 1 0 4h-1" />
      <path d="M12 12v4M9 20h6M10 16h4v4h-4z" />
    </svg>
  )
}

export default function Dashboard() {
  const [capitulos, setCapitulos] = useState(null)
  const [erro, setErro] = useState('')

  useEffect(() => {
    listarCapitulos()
      .then(setCapitulos)
      .catch(() => setErro('Não foi possível carregar sua trilha. Tente recarregar a página.'))
  }, [])

  return (
    <div className="min-h-screen">
      <Header />

      <main className="max-w-3xl mx-auto px-4 py-10">
        <h1 className="font-display text-3xl font-semibold text-ink mb-1">Sua trilha de estudo</h1>
        <p className="text-charcoal-soft mb-10">Siga os níveis em ordem — cada um libera o próximo.</p>

        {erro && <p className="text-coral">{erro}</p>}

        {!capitulos && !erro && <p className="text-charcoal-soft">Carregando sua trilha...</p>}

        {capitulos && (
          <div className="space-y-20">
            {capitulos.map((capitulo) => (
              <div key={capitulo.id} className={!capitulo.liberado ? 'opacity-50' : ''}>
                {/* Cabeçalho do capítulo */}
                <div className="mb-8 pb-4 border-b-2 border-ink/10">
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs text-white bg-ink rounded-full px-2.5 py-1">
                      CAPÍTULO {capitulo.ordem}
                    </span>
                    <h2 className="font-display text-2xl font-semibold text-ink">{capitulo.nome}</h2>
                    {capitulo.prova_final_aprovada && (
                      <span className="flex items-center gap-1 text-xs font-medium text-leaf bg-leaf/10 rounded-full px-2 py-0.5">
                        <IconeCheck className="w-3 h-3" /> Capítulo concluído
                      </span>
                    )}
                  </div>
                  {capitulo.descricao && (
                    <p className="text-sm text-charcoal-soft mt-1">{capitulo.descricao}</p>
                  )}
                </div>

                <div className="space-y-14">
                  {capitulo.niveis.map((nivel) => (
                    <section key={nivel.id} className={!nivel.liberado ? 'opacity-50' : ''}>
                      <div className="flex items-center gap-3 mb-1">
                        <span className="font-mono text-xs text-coral font-medium">
                          NÍVEL {String(nivel.ordem).padStart(2, '0')}
                        </span>
                        <h3 className="font-display text-xl font-semibold text-ink">{nivel.nome}</h3>
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

                      <ol className="relative border-l-2 border-sand-dark ml-3 space-y-1">
                        {nivel.lessons.map((licao) =>
                          nivel.liberado ? (
                            <li key={licao.id} className="relative pl-6 py-3">
                              <span
                                className="absolute -left-[9px] top-4 w-4 h-4 rounded-full bg-ink border-2 border-sand"
                                aria-hidden="true"
                              />
                              <div className="rounded-xl border border-sand-dark bg-white px-4 py-3 hover:border-ink transition-colors">
                                <Link to={`/niveis/${nivel.id}/licoes/${licao.id}`} className="group block">
                                  <p className="font-medium text-charcoal group-hover:text-ink transition-colors">
                                    {licao.titulo}
                                  </p>
                                  <p className="text-sm text-charcoal-soft mt-0.5">{licao.tema}</p>
                                </Link>

                                <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-sand-dark/60">
                                  <Link
                                    to={`/niveis/${nivel.id}/licoes/${licao.id}/flashcards`}
                                    className="text-xs font-medium text-ink border border-ink/30 rounded-lg px-2.5 py-1 hover:bg-ink hover:text-white transition-colors"
                                  >
                                    🗂️ Flashcards
                                  </Link>
                                  <Link
                                    to={`/niveis/${nivel.id}/licoes/${licao.id}/conversation`}
                                    className="text-xs font-medium text-ink border border-ink/30 rounded-lg px-2.5 py-1 hover:bg-ink hover:text-white transition-colors"
                                  >
                                    💬 Conversar
                                  </Link>
                                  <Link
                                    to={`/niveis/${nivel.id}/licoes/${licao.id}/fala`}
                                    className="text-xs font-medium text-ink border border-ink/30 rounded-lg px-2.5 py-1 hover:bg-ink hover:text-white transition-colors"
                                  >
                                    🎤 Praticar fala
                                  </Link>
                                  <Link
                                    to={`/niveis/${nivel.id}/licoes/${licao.id}/quiz`}
                                    className="text-xs font-medium text-white bg-coral rounded-lg px-2.5 py-1 hover:opacity-90 transition-opacity"
                                  >
                                    ✅ Quiz
                                  </Link>
                                </div>
                              </div>
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

                  {/* Prova final do capítulo */}
                  {capitulo.liberado && (
                    <div
                      className={`rounded-2xl border-2 px-6 py-5 flex items-center justify-between gap-4 ${
                        capitulo.prova_final_aprovada
                          ? 'border-leaf/40 bg-leaf/5'
                          : capitulo.prova_final_disponivel
                            ? 'border-coral bg-coral/5'
                            : 'border-sand-dark bg-white/50'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <IconeTrofeu
                          className={`w-8 h-8 shrink-0 ${
                            capitulo.prova_final_aprovada
                              ? 'text-leaf'
                              : capitulo.prova_final_disponivel
                                ? 'text-coral'
                                : 'text-charcoal-soft'
                          }`}
                        />
                        <div>
                          <p className="font-display text-lg font-semibold text-ink">
                            Prova Final — {capitulo.nome}
                          </p>
                          <p className="text-sm text-charcoal-soft">
                            {capitulo.prova_final_aprovada
                              ? 'Aprovado! Você concluiu este capítulo.'
                              : capitulo.prova_final_disponivel
                                ? '15 perguntas revisando tudo que você estudou aqui.'
                                : 'Complete todos os níveis acima pra desbloquear.'}
                          </p>
                        </div>
                      </div>
                      {capitulo.prova_final_disponivel && (
                        <Link
                          to={`/capitulos/${capitulo.id}/prova-final`}
                          className="shrink-0 text-sm font-medium text-white bg-coral rounded-lg px-4 py-2 hover:opacity-90 transition-opacity"
                        >
                          {capitulo.prova_final_aprovada ? 'Refazer' : 'Fazer prova'}
                        </Link>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
