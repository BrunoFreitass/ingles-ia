import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Brand from '../components/Brand'

export default function Login() {
  const { entrar } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [enviando, setEnviando] = useState(false)
  const [demorando, setDemorando] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    if (enviando) return // guarda extra contra duplo clique antes do botão desabilitar de vez
    setErro('')
    setEnviando(true)
    setDemorando(false)

    // Se passar de alguns segundos, provavelmente é o servidor "acordando"
    // (plano gratuito de hospedagem) — avisa em vez de deixar parecer travado.
    const timer = setTimeout(() => setDemorando(true), 4000)

    try {
      await entrar({ email, senha })
      navigate('/')
    } catch (err) {
      const detalhe = err.response?.data?.detail
      setErro(typeof detalhe === 'string' ? detalhe : 'Não foi possível entrar. Confira e-mail e senha.')
    } finally {
      clearTimeout(timer)
      setEnviando(false)
      setDemorando(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="mb-10 flex justify-center">
          <Brand size="lg" />
        </div>

        <div className="bg-white rounded-2xl border border-sand-dark shadow-sm p-8">
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Bem-vindo de volta</h1>
          <p className="text-charcoal-soft text-sm mb-6">Entre para continuar seus estudos.</p>

          <form onSubmit={handleSubmit} className="space-y-4">
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
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                className="w-full rounded-lg border border-sand-dark px-3 py-2 text-sm focus:border-ink focus:outline-none"
                placeholder="••••••••"
              />
            </div>

            {erro && (
              <p className="text-sm text-coral bg-coral/10 border border-coral/30 rounded-lg px-3 py-2">
                {erro}
              </p>
            )}

            {demorando && (
              <p className="text-xs text-charcoal-soft bg-sand-dark/40 rounded-lg px-3 py-2">
                O servidor estava "dormindo" (economia de recursos) e está acordando agora —
                pode levar até 1 minuto na primeira vez, aguenta aí...
              </p>
            )}

            <button
              type="submit"
              disabled={enviando}
              className="w-full bg-ink hover:bg-ink-light transition-colors text-white font-medium rounded-lg py-2.5 text-sm disabled:opacity-60"
            >
              {enviando ? (demorando ? 'Acordando o servidor...' : 'Entrando...') : 'Entrar'}
            </button>
          </form>
        </div>

        <p className="text-center text-sm text-charcoal-soft mt-6">
          Ainda não tem conta?{' '}
          <Link to="/registro" className="text-ink font-medium hover:underline">
            Criar conta
          </Link>
        </p>
      </div>
    </div>
  )
}