import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { enviarMensagem, iniciarConversa } from '../api/conversation'
import Header from '../components/Header'
import SpeakerButton from '../components/SpeakerButton'

export default function Conversation() {
  const { levelId, lessonId } = useParams()
  const [sessionId, setSessionId] = useState(null)
  const [mensagens, setMensagens] = useState([])
  const [erro, setErro] = useState('')
  const [texto, setTexto] = useState('')
  const [enviando, setEnviando] = useState(false)
  const fimDaListaRef = useRef(null)

  useEffect(() => {
    iniciarConversa(levelId, lessonId)
      .then((sessao) => {
        setSessionId(sessao.id)
        setMensagens(sessao.mensagens)
      })
      .catch((err) => {
        const detalhe = err.response?.data?.detail
        setErro(typeof detalhe === 'string' ? detalhe : 'Não foi possível iniciar a conversa.')
      })
  }, [levelId, lessonId])

  useEffect(() => {
    fimDaListaRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [mensagens])

  async function handleEnviar(e) {
    e.preventDefault()
    if (!texto.trim() || enviando) return

    const textoEnviado = texto
    setTexto('')
    setEnviando(true)

    // Mostra a mensagem do aluno na hora (otimista), a resposta da IA chega depois
    setMensagens((m) => [...m, { id: `temp-${Date.now()}`, autor: 'usuario', texto: textoEnviado, erro_corrigido: null }])

    try {
      const respostaIA = await enviarMensagem(levelId, lessonId, sessionId, textoEnviado)
      setMensagens((m) => [...m, respostaIA])
    } catch (err) {
      const detalhe = err.response?.data?.detail
      setErro(typeof detalhe === 'string' ? detalhe : 'Não foi possível enviar sua mensagem.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <div className="max-w-xl w-full mx-auto px-4 pt-6 flex-1 flex flex-col">
        <Link
          to={`/niveis/${levelId}/licoes/${lessonId}`}
          className="text-sm text-charcoal-soft hover:text-ink mb-4 inline-block"
        >
          ← Voltar para a lição
        </Link>

        <h1 className="font-display text-2xl font-semibold text-ink mb-4">Conversa</h1>

        {erro && (
          <p className="text-coral bg-coral/10 border border-coral/30 rounded-lg px-4 py-3 mb-4">
            {erro}
          </p>
        )}

        {!sessionId && !erro && (
          <p className="text-charcoal-soft">Iniciando a conversa com IA...</p>
        )}

        <div className="flex-1 overflow-y-auto space-y-4 pb-4">
          {mensagens.map((msg) => (
            <div key={msg.id} className={`flex ${msg.autor === 'usuario' ? 'justify-end' : 'justify-start'}`}>
              <div className="max-w-[80%]">
                <div
                  className={`flex items-start gap-2 rounded-2xl px-4 py-2.5 text-sm ${
                    msg.autor === 'usuario'
                      ? 'bg-ink text-white rounded-br-sm'
                      : 'bg-white border border-sand-dark text-charcoal rounded-bl-sm font-mono'
                  }`}
                >
                  <span className="flex-1">{msg.texto}</span>
                  {msg.autor === 'ia' && <SpeakerButton texto={msg.texto} className="mt-0.5" />}
                </div>
                {msg.autor === 'ia' && msg.texto_pt && (
                  <p className="mt-1 px-1 text-xs text-charcoal-soft italic">{msg.texto_pt}</p>
                )}
                {msg.erro_corrigido && (
                  <div className="mt-1.5 bg-coral/10 border border-coral/30 rounded-xl px-3 py-2 text-xs text-charcoal">
                    <span className="text-coral font-medium">Dica de gramática: </span>
                    {msg.erro_corrigido}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={fimDaListaRef} />
        </div>

        {sessionId && (
          <form onSubmit={handleEnviar} className="flex gap-2 pb-6 pt-2 sticky bottom-0 bg-sand">
            <input
              type="text"
              value={texto}
              onChange={(e) => setTexto(e.target.value)}
              placeholder="Escreva em inglês..."
              disabled={enviando}
              className="flex-1 rounded-full border border-sand-dark px-4 py-2.5 text-sm focus:border-ink focus:outline-none disabled:opacity-60"
            />
            <button
              type="submit"
              disabled={enviando || !texto.trim()}
              className="bg-coral hover:opacity-90 transition-opacity text-white font-medium rounded-full px-5 py-2.5 text-sm disabled:opacity-40"
            >
              {enviando ? '...' : 'Enviar'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}