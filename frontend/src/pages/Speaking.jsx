import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { obterLicao } from '../api/levels'
import Header from '../components/Header'
import SpeakerButton from '../components/SpeakerButton'
import { avaliarPronuncia, reconhecerFala, sttDisponivel } from '../utils/speech'

const FEEDBACK = {
  certo: { texto: 'Perfeito!', cor: 'text-leaf', fundo: 'bg-leaf/10 border-leaf/30' },
  quase: { texto: 'Quase lá — tente de novo', cor: 'text-coral', fundo: 'bg-coral/10 border-coral/30' },
  errado: { texto: 'Não reconheci — tente de novo', cor: 'text-coral', fundo: 'bg-coral/10 border-coral/30' },
}

export default function Speaking() {
  const { levelId, lessonId } = useParams()
  const [licao, setLicao] = useState(null)
  const [erro, setErro] = useState('')
  const [indice, setIndice] = useState(0)
  const [gravando, setGravando] = useState(false)
  const [transcricao, setTranscricao] = useState('')
  const [resultado, setResultado] = useState(null) // 'certo' | 'quase' | 'errado'

  useEffect(() => {
    obterLicao(levelId, lessonId)
      .then(setLicao)
      .catch((err) => {
        const detalhe = err.response?.data?.detail
        setErro(typeof detalhe === 'string' ? detalhe : 'Não foi possível carregar esta lição.')
      })
  }, [levelId, lessonId])

  const exemplos = licao?.exemplos ?? []
  const exemploAtual = exemplos[indice]

  function gravar() {
    setTranscricao('')
    setResultado(null)
    setGravando(true)

    reconhecerFala({
      onResult: (texto) => {
        setTranscricao(texto)
        setResultado(avaliarPronuncia(texto, exemploAtual.frase_en))
      },
      onError: () => {
        setErro('Não consegui te ouvir — verifique a permissão do microfone e tente de novo.')
      },
      onEnd: () => setGravando(false),
    })
  }

  function proximo() {
    setTranscricao('')
    setResultado(null)
    setIndice((i) => Math.min(i + 1, exemplos.length - 1))
  }

  function anterior() {
    setTranscricao('')
    setResultado(null)
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

        <h1 className="font-display text-2xl font-semibold text-ink mb-2">Praticar fala</h1>
        <p className="text-charcoal-soft text-sm mb-6">
          Ouça a frase, depois grave você falando ela em inglês.
        </p>

        {!sttDisponivel() && (
          <p className="text-coral bg-coral/10 border border-coral/30 rounded-lg px-4 py-3 mb-6">
            Reconhecimento de fala não é suportado neste navegador. Tente pelo Google Chrome no
            computador ou Android.
          </p>
        )}

        {erro && (
          <p className="text-coral bg-coral/10 border border-coral/30 rounded-lg px-4 py-3 mb-6">
            {erro}
          </p>
        )}

        {!licao && !erro && <p className="text-charcoal-soft">Carregando...</p>}

        {exemploAtual && (
          <div>
            <p className="text-sm text-charcoal-soft mb-3 font-mono">
              {indice + 1} / {exemplos.length}
            </p>

            <div className="bg-white border border-sand-dark rounded-2xl p-8 min-h-[200px] flex flex-col justify-center items-center text-center">
              <div className="flex items-center gap-2 mb-2">
                <p className="font-mono text-xl text-ink font-medium">{exemploAtual.frase_en}</p>
                <SpeakerButton texto={exemploAtual.frase_en} />
              </div>
              <p className="text-sm text-charcoal-soft">{exemploAtual.frase_pt}</p>
            </div>

            <div className="flex flex-col items-center mt-6 gap-3">
              <button
                onClick={gravar}
                disabled={gravando || !sttDisponivel()}
                className={`w-16 h-16 rounded-full flex items-center justify-center transition-colors ${
                  gravando ? 'bg-coral animate-pulse' : 'bg-ink hover:bg-ink-light'
                } disabled:opacity-40`}
                title="Gravar"
                aria-label="Gravar sua fala"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" className="w-6 h-6">
                  <rect x="9" y="2" width="6" height="12" rx="3" />
                  <path d="M5 10a7 7 0 0 0 14 0M12 19v3" strokeLinecap="round" />
                </svg>
              </button>
              <p className="text-xs text-charcoal-soft">
                {gravando ? 'Ouvindo...' : 'Toque para falar'}
              </p>
            </div>

            {transcricao && (
              <div className="mt-6 space-y-3">
                <p className="text-sm text-charcoal-soft text-center">
                  Você disse: <span className="text-charcoal font-medium">"{transcricao}"</span>
                </p>
                {resultado && (
                  <p
                    className={`text-center text-sm font-medium rounded-lg border px-4 py-2 ${FEEDBACK[resultado].cor} ${FEEDBACK[resultado].fundo}`}
                  >
                    {FEEDBACK[resultado].texto}
                  </p>
                )}
              </div>
            )}

            <div className="flex justify-between mt-8">
              <button
                onClick={anterior}
                disabled={indice === 0}
                className="text-sm font-medium text-ink border border-ink/30 rounded-lg px-4 py-2 hover:bg-ink hover:text-white transition-colors disabled:opacity-30"
              >
                ← Anterior
              </button>
              <button
                onClick={proximo}
                disabled={indice === exemplos.length - 1}
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
