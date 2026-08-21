import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { obterPerfil, comentarFoto, removerComentario } from '../api/profile'
import { useAuth } from '../context/AuthContext'
import Header from '../components/Header'

function FotoComComentarios({ foto, usuarioId, onComentar, onApagarComentario }) {
  const [texto, setTexto] = useState('')
  const [enviando, setEnviando] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!texto.trim() || enviando) return
    setEnviando(true)
    try {
      await onComentar(foto.id, texto)
      setTexto('')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="bg-white border border-sand-dark rounded-2xl overflow-hidden">
      <img src={foto.url} alt="" className="w-full aspect-square object-cover bg-sand-dark/30" />
      <div className="p-4 space-y-3">
        {foto.comentarios.length > 0 && (
          <ul className="space-y-2">
            {foto.comentarios.map((c) => (
              <li key={c.id} className="text-sm flex items-start justify-between gap-2">
                <span>
                  <span className="font-medium text-charcoal">{c.autor_nome}: </span>
                  <span className="text-charcoal-soft">{c.texto}</span>
                </span>
                {usuarioId === c.autor_id && (
                  <button
                    onClick={() => onApagarComentario(foto.id, c.id)}
                    className="text-xs text-charcoal-soft hover:text-coral shrink-0"
                    title="Apagar comentário"
                  >
                    ×
                  </button>
                )}
              </li>
            ))}
          </ul>
        )}
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            placeholder="Comentar..."
            maxLength={500}
            disabled={enviando}
            className="flex-1 rounded-full border border-sand-dark px-3 py-1.5 text-sm focus:border-ink focus:outline-none disabled:opacity-60"
          />
          <button
            type="submit"
            disabled={enviando || !texto.trim()}
            className="text-sm font-medium text-white bg-coral rounded-full px-4 py-1.5 hover:opacity-90 transition-opacity disabled:opacity-40"
          >
            Enviar
          </button>
        </form>
      </div>
    </div>
  )
}

export default function Profile() {
  const { userId } = useParams()
  const { usuario } = useAuth()
  const [perfil, setPerfil] = useState(null)
  const [erro, setErro] = useState('')

  const ehMeuPerfil = usuario && perfil && Number(userId) === usuario.id

  useEffect(() => {
    setPerfil(null)
    obterPerfil(userId)
      .then(setPerfil)
      .catch(() => setErro('Não foi possível carregar esse perfil.'))
  }, [userId])

  async function handleComentar(fotoId, texto) {
    const comentario = await comentarFoto(fotoId, texto)
    setPerfil((p) => ({
      ...p,
      fotos: p.fotos.map((f) => (f.id === fotoId ? { ...f, comentarios: [...f.comentarios, comentario] } : f)),
    }))
  }

  async function handleApagarComentario(fotoId, comentarioId) {
    await removerComentario(comentarioId)
    setPerfil((p) => ({
      ...p,
      fotos: p.fotos.map((f) =>
        f.id === fotoId ? { ...f, comentarios: f.comentarios.filter((c) => c.id !== comentarioId) } : f
      ),
    }))
  }

  return (
    <div className="min-h-screen">
      <Header />

      <main className="max-w-2xl mx-auto px-4 py-10">
        {erro && <p className="text-coral">{erro}</p>}
        {!perfil && !erro && <p className="text-charcoal-soft">Carregando perfil...</p>}

        {perfil && (
          <>
            <div className="bg-white border border-sand-dark rounded-2xl p-6 mb-8">
              <div className="flex items-start gap-4">
                <div className="w-20 h-20 rounded-full bg-sand-dark/40 overflow-hidden shrink-0">
                  {perfil.foto_perfil_url && (
                    <img src={perfil.foto_perfil_url} alt="" className="w-full h-full object-cover" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h1 className="font-display text-2xl font-semibold text-ink">{perfil.nome}</h1>
                    {ehMeuPerfil && (
                      <Link
                        to="/perfil/editar"
                        className="text-xs font-medium text-ink border border-ink/30 rounded-lg px-2.5 py-1 hover:bg-ink hover:text-white transition-colors"
                      >
                        ✏️ Editar perfil
                      </Link>
                    )}
                  </div>
                  <p className="text-sm text-charcoal-soft mt-0.5">
                    Nível {perfil.nivel_atual_ordem} · {perfil.nivel_atual_nome}
                  </p>
                  <p className="text-sm text-charcoal-soft mt-1">
                    {[perfil.curso, perfil.idade && `${perfil.idade} anos`, perfil.signo]
                      .filter(Boolean)
                      .join(' · ')}
                  </p>
                </div>
              </div>

              {perfil.bio && <p className="text-sm text-charcoal mt-4 whitespace-pre-wrap">{perfil.bio}</p>}

              {(perfil.instagram_url || perfil.linkedin_url) && (
                <div className="flex gap-4 mt-4 pt-4 border-t border-sand-dark/60">
                  {perfil.instagram_url && (
                    <a
                      href={perfil.instagram_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-sm font-medium text-coral hover:underline"
                    >
                      📸 Instagram
                    </a>
                  )}
                  {perfil.linkedin_url && (
                    <a
                      href={perfil.linkedin_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-sm font-medium text-coral hover:underline"
                    >
                      💼 LinkedIn
                    </a>
                  )}
                </div>
              )}
            </div>

            {perfil.fotos.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {perfil.fotos.map((foto) => (
                  <FotoComComentarios
                    key={foto.id}
                    foto={foto}
                    usuarioId={usuario?.id}
                    onComentar={handleComentar}
                    onApagarComentario={handleApagarComentario}
                  />
                ))}
              </div>
            ) : (
              <p className="text-sm text-charcoal-soft text-center py-8">
                {ehMeuPerfil ? 'Você ainda não adicionou fotos.' : 'Nenhuma foto ainda.'}
              </p>
            )}
          </>
        )}
      </main>
    </div>
  )
}
