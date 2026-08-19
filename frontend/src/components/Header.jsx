import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Brand from './Brand'

export default function Header() {
  const { usuario, sair } = useAuth()

  return (
    <header className="border-b border-sand-dark bg-white/60 backdrop-blur-sm sticky top-0 z-10">
      <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/">
          <Brand />
        </Link>
        <div className="flex items-center gap-4">
          <Link to="/ranking" className="text-sm font-medium text-ink hidden sm:inline hover:underline">
            🏆 Ranking
          </Link>
          <Link to="/revisao" className="text-sm font-medium text-ink hidden sm:inline hover:underline">
            Revisão
          </Link>
          <Link to="/imersao" className="text-sm font-medium text-ink hidden sm:inline hover:underline">
            Motor de imersão
          </Link>
          {usuario && (
            <span className="text-sm text-charcoal-soft hidden sm:inline">
              Olá, <span className="text-charcoal font-medium">{usuario.nome.split(' ')[0]}</span>
            </span>
          )}
          <button
            onClick={sair}
            className="text-sm font-medium text-ink border border-ink/30 rounded-lg px-3 py-1.5 hover:bg-ink hover:text-white transition-colors"
          >
            Sair
          </button>
        </div>
      </div>
    </header>
  )
}
