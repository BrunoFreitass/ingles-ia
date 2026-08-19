import client from './client'

export async function obterQuiz(levelId, lessonId) {
  const { data } = await client.get(`/levels/${levelId}/lessons/${lessonId}/quiz`)
  return data
}

export async function submeterQuiz(levelId, lessonId, respostas) {
  const { data } = await client.post(`/levels/${levelId}/lessons/${lessonId}/quiz/submit`, {
    respostas,
  })
  return data
}
