import client from './client'

export async function obterMeuPerfil() {
  const { data } = await client.get('/users/me/profile')
  return data
}

export async function obterPerfil(userId) {
  const { data } = await client.get(`/users/${userId}/profile`)
  return data
}

export async function editarMeuPerfil(dados) {
  const { data } = await client.put('/users/me/profile', dados)
  return data
}

export async function adicionarFoto(url) {
  const { data } = await client.post('/users/me/profile/fotos', { url })
  return data
}

export async function removerFoto(fotoId) {
  await client.delete(`/users/me/profile/fotos/${fotoId}`)
}

export async function comentarFoto(fotoId, texto) {
  const { data } = await client.post(`/fotos/${fotoId}/comentarios`, { texto })
  return data
}

export async function removerComentario(comentarioId) {
  await client.delete(`/fotos/comentarios/${comentarioId}`)
}
