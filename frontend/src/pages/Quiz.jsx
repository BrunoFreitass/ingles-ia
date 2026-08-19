import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { obterQuiz, submeterQuiz } from '../api/quiz'
import Header from '../components/Header'

export default function Quiz() {
  const { levelId, lessonId } = useParams()
  const [quiz, setQuiz] = useState(null)
  const [erro, setErro] = useState('')
  const [respostas, setRespostas] = useState({}) // { [pergunta_id]: opcao_selecionada }
  const [resultado, setResultado] = useState(null)
  const [enviando, setEnviando] = useState(false)

  useEffect(() => {
    obterQuiz(levelId, lessonId)
      .then(setQuiz)
      .catch((err) => {
        const detalhe = err.response?.data?.detail
        setErro(typeof detalhe === 'string' ? detalhe : 'Não foi possível carregar o quiz.')
      })
  }, [levelId, lessonId])

  function selecionar(perguntaId, opcao) {
    if (resultado) return // já enviado, não deixa mudar
    setRespostas((r) => ({ ...r, [perguntaId]: opcao }))
  }

  async function handleSubmit() {
    setEnviando(true)
    try {
      const payload = Object.entries(respostas).map(([pergunta_id, resposta_selecionada]) => ({
        pergunta_id: Number(pergunta_id),
        resposta_selecionada,
      }))
      const data = await submeterQuiz(levelId, lessonId, payload)
      setResultado(data)
    } catch {
      setErro('Não foi possível enviar suas respostas. Tente novamente.')
    } finally {
      setEnviando(false)
    }
  }

  const todasRespondidas = quiz && Object.keys(respostas).length === quiz.perguntas.length

  // Depois do resultado, indexamos a correção por pergunta_id pra ser fácil de cruzar na tela
  const correcaoPorPergunta = resultado
    ? Object.fromEntries(resultado.correcao.map((c) => [c.pergunta_id, c]))
    : null

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

        <h1 className="font-display text-2xl font-semibold text-ink mb-2">Quiz</h1>
        <p className="text-charcoal-soft text-sm mb-8">
          {resultado
            ? 'Confira o resultado abaixo.'
            : 'Responda as 10 perguntas — o gabarito só aparece depois que você enviar.'}
        </p>

        {erro && (
          <p className="text-coral bg-coral/10 border border-coral/30 rounded-lg px-4 py-3 mb-6">
            {erro}
          </p>
        )}

        {!quiz && !erro && (
          <p className="text-charcoal-soft">
            Gerando seu quiz com IA — isso pode levar alguns segundos na primeira vez...
          </p>
        )}

        {resultado && (
          <div className="bg-white border border-sand-dark rounded-2xl p-6 mb-8 text-center">
            <p className="font-mono text-xs text-charcoal-soft uppercase mb-1">Sua nota</p>
            <p className="font-display text-5xl font-semibold text-ink">
              {resultado.nota.toFixed(1)}
            </p>
            <p className="text-sm text-charcoal-soft mt-2">
              {resultado.acertos} de {resultado.total_perguntas} corretas
            </p>
          </div>
        )}

        {resultado?.nivel_desbloqueado && (
          <div className="bg-leaf/10 border border-leaf/30 rounded-2xl p-6 mb-8 text-center">
            <p className="font-display text-lg font-semibold text-leaf">
              🎉 Nível desbloqueado!
            </p>
            <p className="text-sm text-charcoal mt-1">
              Você concluiu esse nível e liberou <span className="font-medium">{resultado.novo_nivel_nome}</span>.
            </p>
            <Link to="/" className="inline-block mt-3 text-sm font-medium text-leaf hover:underline">
              Ver na trilha →
            </Link>
          </div>
        )}

        {quiz && (
          <div className="space-y-6">
            {quiz.perguntas.map((pergunta, i) => {
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
                          estilo = 'border-leaf bg-leaf/10 text-leaf' // resposta certa, sempre destacada após envio
                        } else if (selecionada && !correcao.acertou) {
                          estilo = 'border-coral bg-coral/10 text-coral' // o que o usuário errou
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
                    ? 'Enviar respostas'
                    : `Responda todas as ${quiz.perguntas.length} perguntas para enviar`}
              </button>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
