import axios from 'axios'

// Em dev, o Vite faz proxy de /api -> http://127.0.0.1:8000 (ver vite.config.js),
// então o padrão '/api' funciona sem configurar nada. Em produção, frontend e
// backend ficam em domínios diferentes — defina VITE_API_URL no ambiente de
// build (ex: https://sua-api.onrender.com) pra apontar pro backend de verdade.
const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('ingles_ia_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Se o token expirou ou é inválido, o backend responde 401 — nesse caso,
// limpamos a sessão local e mandamos de volta pro login.
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('ingles_ia_token')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default client
