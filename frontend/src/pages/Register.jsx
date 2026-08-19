import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Brand from '../components/Brand'

export default function Register() {
  const { registrar } = useAuth()
  const navigate = useNavigate()
  const [nome, setNome] = useState('')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [enviando, setEnviando] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setErro('')
    setEnviando(true)
    try {
      await registrar({ nome, email, senha })
      navigate('/')
    } catch (err) {
      const detalhe = err.response?.data?.detail
      if (Array.isArray(detalhe)) {
        // Erro de validação do Pydantic (422) — pega a primeira mensagem
        setErro(detalhe[0]?.msg ?? 'Confira os dados informados.')
      } else if (typeof detalhe === 'string') {
        setErro(detalhe)
      } else {
        setErro('Não foi possível criar a conta.')
      }
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="mb-10 flex justify-center">
          <Brand size="lg" />
        </div>

        <div className="bg-white rounded-2xl border border-sand-dark shadow-sm p-8">
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Criar conta</h1>
          <p className="text-charcoal-soft text-sm mb-6">Comece sua jornada no inglês hoje.</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="nome" className="block text-sm font-medium text-charcoal mb-1">
                Nome
              </label>
              <input
                id="nome"
                type="text"
                required
                minLength={2}
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                className="w-full rounded-lg border border-sand-dark px-3 py-2 text-sm focus:border-ink focus:outline-none"
                placeholder="Seu nome"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-charcoal mb-1">
                E-mail
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-lg border border-sand-dark px-3 py-2 text-sm focus:border-ink focus:outline-none"
                placeholder="voce@email.com"
              />
            </div>

            <div>
              <label htmlFor="senha" className="block text-sm font-medium text-charcoal mb-1">
                Senha
              </label>
              <input
                id="senha"
                type="password"
                required
                minLength={8}
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                className="w-full rounded-lg border border-sand-dark px-3 py-2 text-sm focus:border-ink focus:outline-none"
                placeholder="Mínimo 8 caracteres"
              />
            </div>

            {erro && (
              <p className="text-sm text-coral bg-coral/10 border border-coral/30 rounded-lg px-3 py-2">
                {erro}
              </p>
            )}

            <button
              type="submit"
              disabled={enviando}
              className="w-full bg-coral hover:opacity-90 transition-opacity text-white font-medium rounded-lg py-2.5 text-sm disabled:opacity-60"
            >
              {enviando ? 'Criando conta...' : 'Criar conta'}
            </button>
          </form>
        </div>

        <p className="text-center text-sm text-charcoal-soft mt-6">
          Já tem conta?{' '}
          <Link to="/login" className="text-ink font-medium hover:underline">
            Entrar
          </Link>
        </p>
      </div>
    </div>
  )
}
