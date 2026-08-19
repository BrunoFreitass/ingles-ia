import client from './client'

export async function enviarTexto(textoPt) {
  const { data } = await client.post('/immersion/texts', { texto_pt: textoPt })
  return data
}

export async function gerarPorTema(tema) {
  const { data } = await client.post('/immersion/texts/generate', { tema })
  return data
}

export async function listarHistorico() {
  const { data } = await client.get('/immersion/texts')
  return data
}

export async function obterTexto(id) {
  const { data } = await client.get(`/immersion/texts/${id}`)
  return data
}
