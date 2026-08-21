import client from './client'

export async function iniciarConversa(levelId, lessonId) {
  const { data } = await client.post(`/levels/${levelId}/lessons/${lessonId}/conversation/start`)
  return data
}

export async function enviarMensagem(levelId, lessonId, sessionId, texto) {
  const { data } = await client.post(
    `/levels/${levelId}/lessons/${lessonId}/conversation/${sessionId}/message`,
    { texto }
  )
  return data
}