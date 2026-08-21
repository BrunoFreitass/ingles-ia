import client from './client'

export async function obterFilaRevisao() {
  const { data } = await client.get('/flashcards/review')
  return data
}

export async function enviarRevisao(flashcardId, acertou) {
  const { data } = await client.post(`/flashcards/${flashcardId}/review`, { acertou })
  return data
}