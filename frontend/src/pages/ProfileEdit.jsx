import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { obterMeuPerfil, editarMeuPerfil, adicionarFoto, removerFoto } from '../api/profile'
import { useAuth } from '../context/AuthContext'
import Header from '../components/Header'

const SIGNOS = [
  'Áries', 'Touro', 'Gêmeos', 'Câncer', 'Leão', 'Virgem',
  'Libra', 'Escorpião', 'Sagitário', 'Capricórnio', 'Aquário', 'Peixes',
]

export default function ProfileEdit() {
  const { usuario } = useAuth()
  const navigate = useNavigate()

  const [perfil, setPerfil] = useState(null)
  const [form, setForm] = useState(null)
  const [erro, setErro] = useState('')
  const [salvando, setSalvando] = useState(false)
  const [salvo, setSalvo] = useState(false)

  const [novaFotoUrl, setNovaFotoUrl] = useState('')
  const [adicionandoFoto, setAdicionandoFoto] = useState(false)

  useEffect(() => {
    obterMeuPerfil()
      .then((p) => {
        setPerfil(p)
        setForm({
          foto_perfil_url: p.foto_perfil_url || '',
          bio: p.bio || '',
          curso: p.curso || '',
          idade: p.idade ?? '',
          signo: p.signo || '',
          instagram_url: p.instagram_url || '',
          linkedin_url: p.linkedin_url || '',
        })
      })
      .catch(() => setErro('Não foi possível carregar seu perfil.'))
  }, [])

  function atualizarCampo(campo, valor) {
    setForm((f) => ({ ...f, [campo]: valor }))
    setSalvo(false)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSalvando(true)
    setErro('')
    try {
      const payload = { ...form, idade: form.idade === '' ? null : Number(form.idade) }
      const atualizado = await editarMeuPerfil(payload)
      setPerfil(atualizado)
      setSalvo(true)
    } catch (err) {
      const detalhe = err.response?.data?.detail
      setErro(typeof detalhe === 'string' ? detalhe : 'Não foi possível salvar as alterações.')
    } finally {
      setSalvando(false)
    }
  }

  async function handleAdicionarFoto(e) {
    e.preventDefault()
    if (!novaFotoUrl.trim() || adicionandoFoto) return
    setAdicionandoFoto(true)
    setErro('')
    try {
      const foto = await adicionarFoto(novaFotoUrl.trim())
      setPerfil((p) => ({ ...p, fotos: [...p.fotos, foto] }))
      setNovaFotoUrl('')
    } catch (err) {
      const detalhe = err.response?.data?.detail
      setErro(typeof detalhe === 'string' ? detalhe : 'Não foi possível adicionar a foto.')
    } finally {
      setAdicionandoFoto(false)
    }
  }

  async function handleRemoverFoto(fotoId) {
    try {
      await removerFoto(fotoId)
      setPerfil((p) => ({ ...p, fotos: p.fotos.filter((f) => f.id !== fotoId) }))
    } catch {
      setErro('Não foi possível remover a foto.')
    }
  }

  const inputClass =
    'w-full rounded-lg border border-sand-dark px-3 py-2 text-sm focus:border-ink focus:outline-none'

  return (
    <div className="min-h-screen">
      <Header />

      <main className="max-w-xl mx-auto px-4 py-10">
        {usuario && (
          <Link to={`/perfil/${usuario.id}`} className="text-sm text-charcoal-soft hover:text-ink mb-6 inline-block">
            ← Voltar para o perfil
          </Link>
        )}

        <h1 className="font-display text-2xl font-semibold text-ink mb-6">Editar perfil</h1>

        {erro && (
          <p className="text-sm text-coral bg-coral/10 border border-coral/30 rounded-lg px-3 py-2 mb-4">{erro}</p>
        )}

        {!form && !erro && <p className="text-charcoal-soft">Carregando...</p>}

        {form && (
          <>
            <form onSubmit={handleSubmit} className="bg-white border border-sand-dark rounded-2xl p-6 space-y-4 mb-8">
              <div>
                <label className="block text-sm font-medium text-charcoal mb-1">URL da foto de perfil</label>
                <input
                  type="text"
                  value={form.foto_perfil_url}
                  onChange={(e) => atualizarCampo('foto_perfil_url', e.target.value)}
                  placeholder="https://..."
                  className={inputClass}
                />
                <p className="text-xs text-charcoal-soft mt-1">
                  Cole o link da foto — pode ser o link normal de compartilhamento do Imgur, ibb.co
                  ou similar (o sistema tenta converter sozinho pro link direto). Google Fotos/Drive
                  ainda não funciona.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-charcoal mb-1">Bio</label>
                <textarea
                  value={form.bio}
                  onChange={(e) => atualizarCampo('bio', e.target.value)}
                  maxLength={1000}
                  rows={3}
                  placeholder="Conte um pouco sobre você..."
                  className={inputClass}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-charcoal mb-1">Curso</label>
                <input
                  type="text"
                  value={form.curso}
                  onChange={(e) => atualizarCampo('curso', e.target.value)}
                  placeholder="Ex: Design Gráfico"
                  className={inputClass}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-charcoal mb-1">Idade</label>
                  <input
                    type="number"
                    min={13}
                    max={120}
                    value={form.idade}
                    onChange={(e) => atualizarCampo('idade', e.target.value)}
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-charcoal mb-1">Signo</label>
                  <select
                    value={form.signo}
                    onChange={(e) => atualizarCampo('signo', e.target.value)}
                    className={inputClass}
                  >
                    <option value="">—</option>
                    {SIGNOS.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-charcoal mb-1">Instagram</label>
                <input
                  type="text"
                  value={form.instagram_url}
                  onChange={(e) => atualizarCampo('instagram_url', e.target.value)}
                  placeholder="https://instagram.com/..."
                  className={inputClass}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-charcoal mb-1">LinkedIn</label>
                <input
                  type="text"
                  value={form.linkedin_url}
                  onChange={(e) => atualizarCampo('linkedin_url', e.target.value)}
                  placeholder="https://linkedin.com/in/..."
                  className={inputClass}
                />
              </div>

              <button
                type="submit"
                disabled={salvando}
                className="w-full bg-coral hover:opacity-90 transition-opacity text-white font-medium rounded-lg py-2.5 text-sm disabled:opacity-60"
              >
                {salvando ? 'Salvando...' : salvo ? 'Salvo ✓' : 'Salvar alterações'}
              </button>
            </form>

            <div className="bg-white border border-sand-dark rounded-2xl p-6">
              <h2 className="font-display text-lg font-semibold text-ink mb-1">Fotos</h2>
              <p className="text-sm text-charcoal-soft mb-4">Até 4 fotos — outros alunos podem comentar nelas.</p>

              {perfil.fotos.length > 0 && (
                <div className="grid grid-cols-2 gap-3 mb-4">
                  {perfil.fotos.map((foto) => (
                    <div key={foto.id} className="relative group">
                      <img
                        src={foto.url}
                        alt=""
                        className="w-full aspect-square object-cover rounded-lg bg-sand-dark/30"
                      />
                      <button
                        onClick={() => handleRemoverFoto(foto.id)}
                        className="absolute top-2 right-2 text-xs font-medium text-white bg-coral rounded-full w-6 h-6 flex items-center justify-center hover:opacity-90"
                        title="Remover foto"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {perfil.fotos.length < 4 ? (
                <>
                  <form onSubmit={handleAdicionarFoto} className="flex gap-2">
                    <input
                      type="text"
                      value={novaFotoUrl}
                      onChange={(e) => setNovaFotoUrl(e.target.value)}
                      placeholder="URL direta da imagem (ex: https://i.imgur.com/xxxx.jpg)"
                      disabled={adicionandoFoto}
                      className={`flex-1 ${inputClass}`}
                    />
                    <button
                      type="submit"
                      disabled={adicionandoFoto || !novaFotoUrl.trim()}
                      className="text-sm font-medium text-white bg-ink rounded-lg px-4 py-2 hover:opacity-90 transition-opacity disabled:opacity-40"
                    >
                      Adicionar
                    </button>
                  </form>
                  <p className="text-xs text-charcoal-soft mt-2">
                    Cole o link normal de compartilhamento (Imgur, ibb.co...) — o sistema tenta
                    converter sozinho. Google Fotos/Drive ainda não funciona.
                  </p>
                </>
              ) : (
                <p className="text-xs text-charcoal-soft italic">
                  Limite de 4 fotos atingido — remova uma pra adicionar outra.
                </p>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  )
}
