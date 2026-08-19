import client from './client'

export async function obterFlashcards(levelId, lessonId) {
  const { data } = await client.get(`/levels/${levelId}/lessons/${lessonId}/flashcards`)
  return data
}
