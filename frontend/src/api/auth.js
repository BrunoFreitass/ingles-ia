import client from './client'

export async function registrar({ nome, email, senha }) {
  const { data } = await client.post('/auth/register', { nome, email, senha })
  return data
}

export async function login({ email, senha }) {
  // O backend usa OAuth2PasswordRequestForm: espera form-urlencoded,
  // com username/password (não JSON, não email/senha).
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', senha)

  const { data } = await client.post('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data // { access_token, token_type }
}

export async function meusDados() {
  const { data } = await client.get('/auth/me')
  return data
}