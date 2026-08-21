import client from './client'

export async function obterRanking() {
  const { data } = await client.get('/ranking')
  return data
}