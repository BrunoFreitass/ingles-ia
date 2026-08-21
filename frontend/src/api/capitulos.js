import client from './client'

export async function listarCapitulos() {
  const { data } = await client.get('/capitulos')
  return data
}

export async function obterProvaFinal(capituloId) {
  const { data } = await client.get(`/capitulos/${capituloId}/prova-final`)
  return data
}

export async function submeterProvaFinal(capituloId, respostas) {
  const { data } = await client.post(`/capitulos/${capituloId}/prova-final/submit`, { respostas })
  return data
}