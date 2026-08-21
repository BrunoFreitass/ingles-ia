// Wrapper fino sobre a Web Speech API (SpeechSynthesis), nativa do navegador.
// Não depende de nenhum serviço externo nem gasta cota de IA — funciona
// offline, para qualquer texto (inclusive o que a IA gera na hora).

export function ttsDisponivel() {
  return typeof window !== 'undefined' && 'speechSynthesis' in window
}

let vozInglesCache = null

function escolherVozIngles() {
  if (vozInglesCache) return vozInglesCache
  const vozes = window.speechSynthesis.getVoices()
  // Prioriza vozes en-US, depois qualquer voz en-*
  vozInglesCache =
    vozes.find((v) => v.lang === 'en-US') || vozes.find((v) => v.lang?.startsWith('en')) || null
  return vozInglesCache
}

export function falarIngles(texto) {
  if (!ttsDisponivel() || !texto) return

  // Cancela qualquer fala em andamento antes de começar uma nova
  window.speechSynthesis.cancel()

  const utterance = new SpeechSynthesisUtterance(texto)
  utterance.lang = 'en-US'
  utterance.rate = 0.95 // um pouco mais devagar, ajuda quem está aprendendo

  const voz = escolherVozIngles()
  if (voz) utterance.voice = voz

  window.speechSynthesis.speak(utterance)
}

// As vozes carregam de forma assíncrona em alguns navegadores — isso garante
// que o cache seja preenchido assim que ficarem disponíveis.
if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
  window.speechSynthesis.onvoiceschanged = () => {
    vozInglesCache = null
  }
}

// ---------------------------------------------------------------------------
// Reconhecimento de fala (STT) — usado na prática de pronúncia
// ---------------------------------------------------------------------------

function getSpeechRecognitionClass() {
  if (typeof window === 'undefined') return null
  return window.SpeechRecognition || window.webkitSpeechRecognition || null
}

export function sttDisponivel() {
  return getSpeechRecognitionClass() !== null
}

/**
 * Grava uma única fala do usuário em inglês e retorna a transcrição via callback.
 * Retorna a instância do reconhecimento (para poder cancelar, se precisar).
 */
export function reconhecerFala({ onResult, onError, onEnd }) {
  const SpeechRecognitionClass = getSpeechRecognitionClass()
  if (!SpeechRecognitionClass) {
    onError?.('Reconhecimento de fala não é suportado neste navegador.')
    return null
  }

  const recognition = new SpeechRecognitionClass()
  recognition.lang = 'en-US'
  recognition.interimResults = false
  recognition.maxAlternatives = 1

  recognition.onresult = (event) => {
    const transcricao = event.results[0][0].transcript
    onResult?.(transcricao)
  }
  recognition.onerror = (event) => {
    onError?.(event.error)
  }
  recognition.onend = () => {
    onEnd?.()
  }

  recognition.start()
  return recognition
}

/** Normaliza texto para comparação tolerante (ignora maiúsculas, pontuação, espaços extras). */
function normalizar(texto) {
  return texto
    .toLowerCase()
    .replace(/[.,!?;:'"]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}

/** Compara a fala do usuário com a frase alvo. Retorna 'certo' | 'quase' | 'errado'. */
export function avaliarPronuncia(transcricao, fraseAlvo) {
  const a = normalizar(transcricao)
  const b = normalizar(fraseAlvo)

  if (a === b) return 'certo'

  // "Quase": a maioria das palavras da frase alvo apareceu na transcrição
  const palavrasAlvo = b.split(' ').filter(Boolean)
  const palavrasDitas = new Set(a.split(' ').filter(Boolean))
  const acertadas = palavrasAlvo.filter((p) => palavrasDitas.has(p)).length
  const proporcao = palavrasAlvo.length ? acertadas / palavrasAlvo.length : 0

  if (proporcao >= 0.7) return 'quase'
  return 'errado'
}