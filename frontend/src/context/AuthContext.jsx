import { createContext, useContext, useEffect, useState } from 'react'
import * as authApi from '../api/auth'

const AuthContext = createContext(null)

const TOKEN_KEY = 'ingles_ia_token'

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null)
  const [carregando, setCarregando] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) {
      setCarregando(false)
      return
    }
    // Já tem token salvo — valida buscando os dados do usuário.
    authApi
      .meusDados()
      .then(setUsuario)
      .catch(() => localStorage.removeItem(TOKEN_KEY))
      .finally(() => setCarregando(false))
  }, [])

  async function entrar({ email, senha }) {
    const { access_token } = await authApi.login({ email, senha })
    localStorage.setItem(TOKEN_KEY, access_token)
    const dados = await authApi.meusDados()
    setUsuario(dados)
    return dados
  }

  async function registrar({ nome, email, senha }) {
    await authApi.registrar({ nome, email, senha })
    // Após criar a conta, já loga automaticamente.
    return entrar({ email, senha })
  }

  function sair() {
    localStorage.removeItem(TOKEN_KEY)
    setUsuario(null)
  }

  const value = { usuario, carregando, entrar, registrar, sair }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth precisa ser usado dentro de um <AuthProvider>')
  }
  return ctx
}