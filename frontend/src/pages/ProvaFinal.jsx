import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { obterProvaFinal, submeterProvaFinal } from '../api/capitulos'
import Header from '../components/Header'

export default function ProvaFinal() {
  const { capituloId } = useParams()
  const [prova, setProva] = useState(null)
  const [erro, setErro] = useState('')
  const [respostas, setRespostas] = useState({})
  const [resultado, setResultado] = useState(null)
  const [enviando, setEnviando] = useState(false)
  const resultadoRef = useRef(null)

  useEffect(() => {
    obterProvaFinal(capituloId)
      .then(setProva)
      .catch((err) => {
        const detalhe = err.response?.data?.detail
        setErro(typeof detalhe === 'string' ? detalhe : 'Não foi possível carregar a prova final.')
      })
  }, [capituloId])

  function selecionar(perguntaId, opcao) {
    if (resultado) return
    setRespostas((r) => ({ ...r, [perguntaId]: opcao }))
  }

  // Mesmo motivo do Quiz de nível: o botão de enviar fica no fim da página,
  // então sem isso o aluno não vê o resultado (aprovado/reprovado, capítulo
  // desbloqueado) sem rolar manualmente pra cima.
  useEffect(() => {
    if (resultado) {
      resultadoRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [resultado])

  async function handleSubmit() {
    setEnviando(true)
    try {
      const payload = Object.entries(respostas).map(([pergunta_id, resposta_selecionada]) => ({
        pergunta_id: Number(pergunta_id),
        resposta_selecionada,
      }))
      const data = await submeterProvaFinal(capituloId, payload)
      setResultado(data)
    } catch {
      setErro('Não foi possível enviar suas respostas. Tente novamente.')
    } finally {
      setEnviando(false)
    }
  }

  const todasRespondidas = prova && Object.keys(respostas).length === prova.perguntas.length
  const correcaoPorPergunta = resultado
    ? Object.fromEntries(resultado.correcao.map((c) => [c.pergunta_id, c]))
    : null
  const aprovado = resultado && resultado.nota >= 7

  return (
    <div className="min-h-screen">
      <Header />

      <main className="max-w-xl mx-auto px-4 py-10">
        <Link to="/" className="text-sm text-charcoal-soft hover:text-ink mb-6 inline-block">
          ← Voltar para a trilha
        </Link>

        <h1 className="font-display text-2xl font-semibold text-ink mb-2">🏆 Prova Final</h1>
        <p className="text-charcoal-soft text-sm mb-8">
          {resultado
            ? 'Confira o resultado abaixo.'
            : 'Revisão de tudo que você estudou nesse capítulo — o gabarito só aparece depois que você enviar.'}
        </p>

        {erro && (
          <p className="text-coral bg-coral/10 border border-coral/30 rounded-lg px-4 py-3 mb-6">
            {erro}
          </p>
        )}

        {!prova && !erro && (
          <p className="text-charcoal-soft">
            Gerando sua prova final com IA — isso pode levar alguns segundos...
          </p>
        )}

        {resultado && (
          <div
            ref={resultadoRef}
            className={`rounded-2xl border p-6 mb-8 text-center scroll-mt-6 ${
              aprovado ? 'bg-leaf/5 border-leaf/30' : 'bg-coral/5 border-coral/30'
            }`}
          >
            <p className="font-mono text-xs text-charcoal-soft uppercase mb-1">Sua nota</p>
            <p className={`font-display text-5xl font-semibold ${aprovado ? 'text-leaf' : 'text-coral'}`}>
              {resultado.nota.toFixed(1)}
            </p>
            <p className="text-sm text-charcoal-soft mt-2">
              {resultado.acertos} de {resultado.total_perguntas} corretas
            </p>
            {aprovado ? (
              <p className="text-sm text-leaf font-medium mt-3">
                🎉 Você foi aprovado! Capítulo concluído.
              </p>
            ) : (
              <p className="text-sm text-coral font-medium mt-3">
                Nota mínima é 7.0 — revise os níveis e tente de novo quando quiser.
              </p>
            )}
          </div>
        )}

        {resultado?.capitulo_desbloqueado && (
          <div className="bg-leaf/10 border border-leaf/30 rounded-2xl p-6 mb-8 text-center">
            <p className="font-display text-lg font-semibold text-leaf">🎉 Trilha desbloqueada!</p>
            <p className="text-sm text-charcoal mt-1">
              {resultado.novo_capitulo_nome
                ? (
                  <>Você concluiu esta trilha e liberou <span className="font-medium">{resultado.novo_capitulo_nome}</span>.</>
                )
                : 'Você concluiu esta trilha! A próxima ainda está sendo preparada.'}
            </p>
            <Link to="/" className="inline-block mt-3 text-sm font-medium text-leaf hover:underline">
              Ver na trilha →
            </Link>
          </div>
        )}

        {prova && (
          <div className="space-y-6">
            {prova.perguntas.map((pergunta, i) => {
              const correcao = correcaoPorPergunta?.[pergunta.id]
              return (
                <div key={pergunta.id} className="bg-white border border-sand-dark rounded-2xl p-5">
                  <p className="text-sm font-medium text-charcoal mb-3">
                    <span className="font-mono text-coral">{i + 1}.</span> {pergunta.pergunta}
                  </p>
                  <div className="space-y-2">
                    {pergunta.opcoes.map((opcao) => {
                      const selecionada = respostas[pergunta.id] === opcao
                      let estilo = 'border-sand-dark hover:border-ink/50'

                      if (correcao) {
                        if (opcao === correcao.resposta_correta) {
                          estilo = 'border-leaf bg-leaf/10 text-leaf'
                        } else if (selecionada && !correcao.acertou) {
                          estilo = 'border-coral bg-coral/10 text-coral'
                        } else {
                          estilo = 'border-sand-dark opacity-60'
                        }
                      } else if (selecionada) {
                        estilo = 'border-ink bg-ink/5'
                      }

                      return (
                        <button
                          key={opcao}
                          onClick={() => selecionar(pergunta.id, opcao)}
                          disabled={!!resultado}
                          className={`w-full text-left text-sm rounded-lg border px-4 py-2 transition-colors ${estilo}`}
                        >
                          {opcao}
                        </button>
                      )
                    })}
                  </div>
                </div>
              )
            })}

            {!resultado && (
              <button
                onClick={handleSubmit}
                disabled={!todasRespondidas || enviando}
                className="w-full bg-coral hover:opacity-90 transition-opacity text-white font-medium rounded-lg py-3 text-sm disabled:opacity-40"
              >
                {enviando
                  ? 'Enviando...'
                  : todasRespondidas
                    ? 'Enviar prova final'
                    : `Responda todas as ${prova.perguntas.length} perguntas para enviar`}
              </button>
            )}
          </div>
        )}
      </main>
    </div>
  )
}