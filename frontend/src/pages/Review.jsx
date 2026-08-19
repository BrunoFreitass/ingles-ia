import { useEffect, useState } from 'react'
import { enviarRevisao, obterFilaRevisao } from '../api/flashcardReview'
import Header from '../components/Header'
import SpeakerButton from '../components/SpeakerButton'

export default function Review() {
  const [fila, setFila] = useState(null)
  const [indice, setIndice] = useState(0)
  const [virado, setVirado] = useState(false)
  const [erro, setErro] = useState('')
  const [ultimoResultado, setUltimoResultado] = useState(null) // { intervalo_dias } — feedback rápido após responder

  useEffect(() => {
    obterFilaRevisao()
      .then(setFila)
      .catch(() => setErro('Não foi possível carregar sua fila de revisão.'))
  }, [])

  async function responder(acertou) {
    const cartaoAtual = fila[indice]
    try {
      const progresso = await enviarRevisao(cartaoAtual.id, acertou)
      setUltimoResultado({ acertou, intervalo_dias: progresso.intervalo_dias })
      setTimeout(() => {
        setUltimoResultado(null)
        setVirado(false)
        setIndice((i) => i + 1)
      }, 900)
    } catch {
      setErro('Não foi possível registrar sua resposta. Tente novamente.')
    }
  }

  const acabou = fila && indice >= fila.length

  return (
    <div className="min-h-screen">
      <Header />

      <main className="max-w-xl mx-auto px-4 py-10">
        <h1 className="font-display text-2xl font-semibold text-ink mb-2">Revisão</h1>
        <p className="text-charcoal-soft text-sm mb-8">
          Cartões vencidos e novos, um de cada vez — responda com honestidade pra o sistema
          ajustar quando te mostrar de novo.
        </p>

        {erro && (
          <p className="text-coral bg-coral/10 border border-coral/30 rounded-lg px-4 py-3">
            {erro}
          </p>
        )}

        {!fila && !erro && <p className="text-charcoal-soft">Carregando sua fila de revisão...</p>}

        {fila && fila.length === 0 && (
          <div className="bg-white border border-sand-dark rounded-2xl p-8 text-center">
            <p className="font-display text-lg text-ink">Nenhum cartão pra revisar agora 🎉</p>
            <p className="text-sm text-charcoal-soft mt-2">
              Volte mais tarde, ou gere novos flashcards estudando uma lição.
            </p>
          </div>
        )}

        {fila && fila.length > 0 && !acabou && (
          <div>
            <p className="text-sm text-charcoal-soft mb-3 font-mono">
              {indice + 1} / {fila.length}
            </p>

            {/* div+role em vez de <button> porque contém o SpeakerButton dentro
                (button dentro de button é HTML inválido) */}
            <div
              role="button"
              tabIndex={0}
              onClick={() => !ultimoResultado && setVirado((v) => !v)}
              onKeyDown={(e) => {
                if ((e.key === 'Enter' || e.key === ' ') && !ultimoResultado) {
                  e.preventDefault()
                  setVirado((v) => !v)
                }
              }}
              className="w-full text-left bg-white border border-sand-dark rounded-2xl p-8 min-h-[280px] flex flex-col justify-center hover:border-ink transition-colors cursor-pointer"
            >
              {ultimoResultado ? (
                <div className="text-center">
                  <p className={`font-display text-2xl font-semibold ${ultimoResultado.acertou ? 'text-leaf' : 'text-coral'}`}>
                    {ultimoResultado.acertou ? 'Certo!' : 'Não foi dessa vez'}
                  </p>
                  <p className="text-sm text-charcoal-soft mt-2">
                    Próxima revisão em {ultimoResultado.intervalo_dias}{' '}
                    {ultimoResultado.intervalo_dias === 1 ? 'dia' : 'dias'}
                  </p>
                </div>
              ) : !virado ? (
                <div className="text-center">
                  <div className="flex items-center justify-center gap-2">
                    <p className="font-mono text-3xl text-ink font-medium">{fila[indice].palavra}</p>
                    <SpeakerButton texto={fila[indice].palavra} />
                  </div>
                  <p className="text-sm text-charcoal-soft mt-4">Toque para ver a tradução</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <p className="font-mono text-xs text-coral uppercase mb-1">Tradução</p>
                    <p className="text-lg text-charcoal">{fila[indice].traducao}</p>
                  </div>
                  {fila[indice].exemplo && (
                    <div>
                      <p className="font-mono text-xs text-coral uppercase mb-1">Exemplo</p>
                      <div className="flex items-center gap-2">
                        <p className="font-mono text-sm text-ink">{fila[indice].exemplo}</p>
                        <SpeakerButton texto={fila[indice].exemplo} />
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {virado && !ultimoResultado && (
              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => responder(false)}
                  className="flex-1 text-sm font-medium text-coral border border-coral/40 rounded-lg py-2.5 hover:bg-coral hover:text-white transition-colors"
                >
                  Errei
                </button>
                <button
                  onClick={() => responder(true)}
                  className="flex-1 text-sm font-medium text-white bg-leaf rounded-lg py-2.5 hover:opacity-90 transition-opacity"
                >
                  Acertei
                </button>
              </div>
            )}
          </div>
        )}

        {acabou && (
          <div className="bg-white border border-sand-dark rounded-2xl p-8 text-center">
            <p className="font-display text-lg text-ink">Fila concluída! 🎉</p>
            <p className="text-sm text-charcoal-soft mt-2">Você revisou todos os cartões de hoje.</p>
          </div>
        )}
      </main>
    </div>
  )
}
