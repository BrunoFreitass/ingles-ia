import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { obterFlashcards } from '../api/flashcards'
import Header from '../components/Header'
import SpeakerButton from '../components/SpeakerButton'

export default function Flashcards() {
  const { levelId, lessonId } = useParams()
  const [cartoes, setCartoes] = useState(null)
  const [erro, setErro] = useState('')
  const [indice, setIndice] = useState(0)
  const [virado, setVirado] = useState(false)

  useEffect(() => {
    obterFlashcards(levelId, lessonId)
      .then(setCartoes)
      .catch((err) => {
        const detalhe = err.response?.data?.detail
        setErro(typeof detalhe === 'string' ? detalhe : 'Não foi possível carregar os flashcards.')
      })
  }, [levelId, lessonId])

  function proximo() {
    setVirado(false)
    setIndice((i) => Math.min(i + 1, cartoes.length - 1))
  }

  function anterior() {
    setVirado(false)
    setIndice((i) => Math.max(i - 1, 0))
  }

  return (
    <div className="min-h-screen">
      <Header />

      <main className="max-w-xl mx-auto px-4 py-10">
        <Link
          to={`/niveis/${levelId}/licoes/${lessonId}`}
          className="text-sm text-charcoal-soft hover:text-ink mb-6 inline-block"
        >
          ← Voltar para a lição
        </Link>

        <h1 className="font-display text-2xl font-semibold text-ink mb-6">Flashcards</h1>

        {erro && (
          <p className="text-coral bg-coral/10 border border-coral/30 rounded-lg px-4 py-3">
            {erro}
          </p>
        )}

        {!cartoes && !erro && (
          <p className="text-charcoal-soft">
            Gerando seus flashcards com IA — isso pode levar alguns segundos na primeira vez...
          </p>
        )}

        {cartoes && cartoes.length > 0 && (
          <div>
            <p className="text-sm text-charcoal-soft mb-3 font-mono">
              {indice + 1} / {cartoes.length}
            </p>

            {/* Cartão clicável — clique vira e mostra tradução/exemplo/truque.
                Usa div+role em vez de <button> porque contém o SpeakerButton
                dentro (button dentro de button é HTML inválido). */}
            <div
              role="button"
              tabIndex={0}
              onClick={() => setVirado((v) => !v)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  setVirado((v) => !v)
                }
              }}
              className="w-full text-left bg-white border border-sand-dark rounded-2xl p-8 min-h-[280px] flex flex-col justify-center hover:border-ink transition-colors cursor-pointer"
            >
              {!virado ? (
                <div className="text-center">
                  <div className="flex items-center justify-center gap-2">
                    <p className="font-mono text-3xl text-ink font-medium">{cartoes[indice].palavra}</p>
                    <SpeakerButton texto={cartoes[indice].palavra} />
                  </div>
                  <p className="text-sm text-charcoal-soft mt-4">Toque para ver a tradução</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <p className="font-mono text-xs text-coral uppercase mb-1">Tradução</p>
                    <p className="text-lg text-charcoal">{cartoes[indice].traducao}</p>
                  </div>
                  {cartoes[indice].exemplo && (
                    <div>
                      <p className="font-mono text-xs text-coral uppercase mb-1">Exemplo</p>
                      <div className="flex items-center gap-2">
                        <p className="font-mono text-sm text-ink">{cartoes[indice].exemplo}</p>
                        <SpeakerButton texto={cartoes[indice].exemplo} />
                      </div>
                    </div>
                  )}
                  {cartoes[indice].truque_memorizacao && (
                    <div>
                      <p className="font-mono text-xs text-coral uppercase mb-1">
                        Truque pra memorizar
                      </p>
                      <p className="text-sm text-charcoal-soft">
                        {cartoes[indice].truque_memorizacao}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="flex justify-between mt-6">
              <button
                onClick={anterior}
                disabled={indice === 0}
                className="text-sm font-medium text-ink border border-ink/30 rounded-lg px-4 py-2 hover:bg-ink hover:text-white transition-colors disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-ink"
              >
                ← Anterior
              </button>
              <button
                onClick={proximo}
                disabled={indice === cartoes.length - 1}
                className="text-sm font-medium text-white bg-ink rounded-lg px-4 py-2 hover:bg-ink-light transition-colors disabled:opacity-30"
              >
                Próximo →
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
