import { useEffect, useState } from 'react'
import { enviarTexto, gerarPorTema, listarHistorico, obterTexto } from '../api/immersion'
import Header from '../components/Header'

export default function Immersion() {
  const [modo, setModo] = useState('colar') // 'colar' | 'gerar'
  const [textoPt, setTextoPt] = useState('')
  const [tema, setTema] = useState('')
  const [resultado, setResultado] = useState(null)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState('')
  const [respostasReveladas, setRespostasReveladas] = useState({})
  const [historico, setHistorico] = useState([])

  useEffect(() => {
    listarHistorico().then(setHistorico).catch(() => {})
  }, [])

  function revelar(i) {
    setRespostasReveladas((r) => ({ ...r, [i]: true }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setErro('')
    setCarregando(true)
    setRespostasReveladas({})
    try {
      const data = modo === 'colar' ? await enviarTexto(textoPt) : await gerarPorTema(tema)
      setResultado(data)
      setHistorico((h) => [{ id: data.id, texto_pt: data.texto_pt, criado_em: data.criado_em }, ...h])
      setTextoPt('')
      setTema('')
    } catch (err) {
      const detalhe = err.response?.data?.detail
      setErro(typeof detalhe === 'string' ? detalhe : 'Não foi possível processar agora.')
    } finally {
      setCarregando(false)
    }
  }

  async function abrirDoHistorico(id) {
    setErro('')
    setRespostasReveladas({})
    try {
      const data = await obterTexto(id)
      setResultado(data)
    } catch {
      setErro('Não foi possível carregar esse texto.')
    }
  }

  return (
    <div className="min-h-screen">
      <Header />

      <main className="max-w-3xl mx-auto px-4 py-10 grid md:grid-cols-[1fr_220px] gap-8">
        <div>
          <h1 className="font-display text-3xl font-semibold text-ink mb-1">Motor de imersão</h1>
          <p className="text-charcoal-soft mb-6">
            Cole um texto em português ou peça pra IA escrever um sobre um tema — você recebe a
            tradução e perguntas de compreensão.
          </p>

          <div className="flex gap-2 mb-4">
            <button
              onClick={() => setModo('colar')}
              className={`text-sm font-medium rounded-lg px-4 py-2 transition-colors ${
                modo === 'colar' ? 'bg-ink text-white' : 'border border-ink/30 text-ink'
              }`}
            >
              Colar meu texto
            </button>
            <button
              onClick={() => setModo('gerar')}
              className={`text-sm font-medium rounded-lg px-4 py-2 transition-colors ${
                modo === 'gerar' ? 'bg-ink text-white' : 'border border-ink/30 text-ink'
              }`}
            >
              Gerar por tema
            </button>
          </div>

          <form onSubmit={handleSubmit} className="mb-8">
            {modo === 'colar' ? (
              <textarea
                value={textoPt}
                onChange={(e) => setTextoPt(e.target.value)}
                required
                minLength={10}
                rows={5}
                placeholder="Cole aqui um texto em português..."
                className="w-full rounded-lg border border-sand-dark px-3 py-2 text-sm focus:border-ink focus:outline-none resize-none"
              />
            ) : (
              <input
                type="text"
                value={tema}
                onChange={(e) => setTema(e.target.value)}
                required
                minLength={2}
                placeholder="Ex: viagens, tecnologia, culinária..."
                className="w-full rounded-lg border border-sand-dark px-3 py-2 text-sm focus:border-ink focus:outline-none"
              />
            )}

            <button
              type="submit"
              disabled={carregando}
              className="mt-3 bg-coral hover:opacity-90 transition-opacity text-white font-medium rounded-lg px-5 py-2.5 text-sm disabled:opacity-50"
            >
              {carregando ? 'Processando...' : modo === 'colar' ? 'Traduzir e gerar perguntas' : 'Gerar texto'}
            </button>
          </form>

          {erro && (
            <p className="text-coral bg-coral/10 border border-coral/30 rounded-lg px-4 py-3 mb-6">
              {erro}
            </p>
          )}

          {resultado && (
            <article className="space-y-6">
              <section className="bg-white border border-sand-dark rounded-2xl p-5">
                <p className="font-mono text-xs text-coral uppercase mb-2">Original (PT-BR)</p>
                <p className="text-charcoal text-sm leading-relaxed">{resultado.texto_pt}</p>
              </section>

              <section className="bg-white border border-sand-dark rounded-2xl p-5">
                <p className="font-mono text-xs text-coral uppercase mb-2">Tradução (EN)</p>
                <p className="font-mono text-ink text-sm leading-relaxed">{resultado.texto_en}</p>
              </section>

              {resultado.perguntas?.length > 0 && (
                <section>
                  <h2 className="font-display text-lg font-semibold text-ink mb-3">
                    Perguntas de compreensão
                  </h2>
                  <div className="space-y-2">
                    {resultado.perguntas.map((p, i) => (
                      <div key={i} className="bg-white border border-sand-dark rounded-xl px-4 py-3">
                        <p className="text-sm text-charcoal font-medium">{p.pergunta}</p>
                        {respostasReveladas[i] ? (
                          <p className="text-sm text-leaf mt-1.5">{p.resposta}</p>
                        ) : (
                          <button
                            onClick={() => revelar(i)}
                            className="text-xs text-charcoal-soft hover:text-ink mt-1.5 underline"
                          >
                            Ver resposta
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </section>
              )}
            </article>
          )}
        </div>

        <aside>
          <h2 className="font-mono text-xs text-charcoal-soft uppercase mb-3">Histórico</h2>
          {historico.length === 0 && (
            <p className="text-sm text-charcoal-soft">Nada por aqui ainda.</p>
          )}
          <ul className="space-y-2">
            {historico.map((h) => (
              <li key={h.id}>
                <button
                  onClick={() => abrirDoHistorico(h.id)}
                  className="text-left text-sm text-charcoal-soft hover:text-ink w-full truncate"
                  title={h.texto_pt}
                >
                  {h.texto_pt.slice(0, 40)}...
                </button>
              </li>
            ))}
          </ul>
        </aside>
      </main>
    </div>
  )
}