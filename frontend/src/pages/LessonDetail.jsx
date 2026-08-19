import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { obterLicao } from '../api/levels'
import Header from '../components/Header'
import SpeakerButton from '../components/SpeakerButton'

export default function LessonDetail() {
  const { levelId, lessonId } = useParams()
  const [licao, setLicao] = useState(null)
  const [erro, setErro] = useState('')

  useEffect(() => {
    setLicao(null)
    setErro('')
    obterLicao(levelId, lessonId)
      .then(setLicao)
      .catch((err) => {
        const detalhe = err.response?.data?.detail
        setErro(typeof detalhe === 'string' ? detalhe : 'Não foi possível carregar esta lição.')
      })
  }, [levelId, lessonId])

  return (
    <div className="min-h-screen">
      <Header />

      <main className="max-w-2xl mx-auto px-4 py-10">
        <Link to="/" className="text-sm text-charcoal-soft hover:text-ink mb-6 inline-block">
          ← Voltar para a trilha
        </Link>

        {erro && <p className="text-coral">{erro}</p>}
        {!licao && !erro && <p className="text-charcoal-soft">Carregando lição...</p>}

        {licao && (
          <article className="space-y-8">
            <header>
              <p className="font-mono text-xs text-coral font-medium mb-2 uppercase">{licao.tema}</p>
              <h1 className="font-display text-3xl font-semibold text-ink">{licao.titulo}</h1>

              <div className="flex gap-3 mt-4">
                <Link
                  to={`/niveis/${levelId}/licoes/${lessonId}/flashcards`}
                  className="text-sm font-medium text-ink border border-ink/30 rounded-lg px-4 py-2 hover:bg-ink hover:text-white transition-colors"
                >
                  Flashcards
                </Link>
                <Link
                  to={`/niveis/${levelId}/licoes/${lessonId}/conversation`}
                  className="text-sm font-medium text-ink border border-ink/30 rounded-lg px-4 py-2 hover:bg-ink hover:text-white transition-colors"
                >
                  Conversar
                </Link>
                <Link
                  to={`/niveis/${levelId}/licoes/${lessonId}/fala`}
                  className="text-sm font-medium text-ink border border-ink/30 rounded-lg px-4 py-2 hover:bg-ink hover:text-white transition-colors"
                >
                  Praticar fala
                </Link>
                <Link
                  to={`/niveis/${levelId}/licoes/${lessonId}/quiz`}
                  className="text-sm font-medium text-white bg-coral rounded-lg px-4 py-2 hover:opacity-90 transition-opacity"
                >
                  Fazer quiz
                </Link>
              </div>
            </header>

            {licao.texto_gramatica && (
              <section className="bg-white rounded-2xl border border-sand-dark p-6">
                <h2 className="font-display text-lg font-semibold text-ink mb-3">Gramática</h2>
                <p className="text-charcoal leading-relaxed">{licao.texto_gramatica}</p>
              </section>
            )}

            {licao.exemplos?.length > 0 && (
              <section>
                <h2 className="font-display text-lg font-semibold text-ink mb-3">Exemplos</h2>
                <div className="space-y-2">
                  {licao.exemplos.map((ex) => (
                    <div
                      key={ex.id}
                      className="bg-white rounded-xl border border-sand-dark px-4 py-3 flex items-start justify-between gap-3"
                    >
                      <div>
                        <p className="font-mono text-sm text-ink">{ex.frase_en}</p>
                        <p className="text-sm text-charcoal-soft mt-1">{ex.frase_pt}</p>
                      </div>
                      <SpeakerButton texto={ex.frase_en} className="mt-0.5" />
                    </div>
                  ))}
                </div>
              </section>
            )}

            {licao.erros_comuns?.length > 0 && (
              <section className="bg-coral/5 border border-coral/20 rounded-2xl p-6">
                <h2 className="font-display text-lg font-semibold text-coral mb-3">
                  Os 3 erros mais comuns
                </h2>
                <ul className="space-y-2">
                  {licao.erros_comuns.map((erro, i) => (
                    <li key={i} className="text-charcoal text-sm leading-relaxed flex gap-2">
                      <span className="text-coral font-mono">{i + 1}.</span>
                      <span>{erro}</span>
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </article>
        )}
      </main>
    </div>
  )
}
