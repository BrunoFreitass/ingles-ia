import client from './client'

export async function listarNiveis() {
  const { data } = await client.get('/levels')
  return data
}

export async function obterLicao(levelId, lessonId) {
  const { data } = await client.get(`/levels/${levelId}/lessons/${lessonId}`)
  return data
}