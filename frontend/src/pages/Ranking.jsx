import { useEffect, useState } from 'react'
import { obterRanking } from '../api/ranking'
import Header from '../components/Header'

const MEDALHAS = { 1: '🥇', 2: '🥈', 3: '🥉' }

export default function Ranking() {
  const [ranking, setRanking] = useState(null)
  const [erro, setErro] = useState('')

  useEffect(() => {
    obterRanking()
      .then(setRanking)
      .catch(() => setErro('Não foi possível carregar o ranking.'))
  }, [])

  return (
    <div className="min-h-screen">
      <Header />

      <main className="max-w-2xl mx-auto px-4 py-10">
        <h1 className="font-display text-3xl font-semibold text-ink mb-1">🏆 Ranking</h1>
        <p className="text-charcoal-soft mb-8">Quem está mais avançado na trilha.</p>

        {erro && <p className="text-coral">{erro}</p>}
        {!ranking && !erro && <p className="text-charcoal-soft">Carregando ranking...</p>}

        {ranking && (
          <div className="bg-white border border-sand-dark rounded-2xl overflow-hidden">
            {ranking.map((item) => (
              <div
                key={item.posicao}
                className={`flex items-center gap-4 px-5 py-4 border-b border-sand-dark last:border-b-0 ${
                  item.eh_voce ? 'bg-coral/5' : ''
                }`}
              >
                <span className="font-mono text-lg text-charcoal-soft w-8 text-center shrink-0">
                  {MEDALHAS[item.posicao] || item.posicao}
                </span>

                <div className="flex-1 min-w-0">
                  <p className="font-medium text-charcoal truncate">
                    {item.nome} {item.eh_voce && <span className="text-coral text-xs">(você)</span>}
                  </p>
                  <p className="text-xs text-charcoal-soft mt-0.5">
                    Nível {item.nivel_atual_ordem} · {item.nivel_atual_nome}
                  </p>
                </div>

                <div className="text-right shrink-0">
                  <p className="font-mono text-sm text-ink font-medium">{item.nota_media.toFixed(1)}</p>
                  <p className="text-xs text-charcoal-soft">
                    {item.total_tentativas} tent. · {item.total_erros} erros
                  </p>
                </div>
              </div>
            ))}

            {ranking.length === 0 && (
              <p className="text-sm text-charcoal-soft text-center py-8">Ninguém no ranking ainda.</p>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
