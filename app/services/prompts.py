"""
Prompts enviados ao Gemini. Mantidos separados do resto da lógica pra
facilitar ajuste fino sem mexer no código de orquestração/cache.
"""

from app.models.level import Lesson


def prompt_flashcards(lesson: Lesson) -> str:
    exemplos_texto = "\n".join(f"- {e.frase_en} ({e.frase_pt})" for e in lesson.exemplos)

    return f"""Você é um professor de inglês criando cartões de vocabulário (flashcards)
para um aluno brasileiro iniciante.

Contexto da lição:
Título: {lesson.titulo}
Tema: {lesson.tema}
Gramática ensinada: {lesson.texto_gramatica}
Frases de exemplo da lição:
{exemplos_texto}

Tarefa: extraia de 6 a 8 palavras ou expressões em inglês relevantes para essa
lição (podem vir das frases de exemplo ou serem palavras-chave do tema) e crie
um flashcard para cada uma.

Para cada flashcard, forneça:
- "palavra": a palavra ou expressão em inglês
- "traducao": a tradução para português do Brasil
- "exemplo": uma frase de exemplo NOVA (diferente das já mostradas) usando a palavra, em inglês
- "truque_memorizacao": um truque simples e curto (1-2 frases) para um iniciante memorizar essa palavra —
  pode ser associação sonora, visual, ou com uma palavra parecida em português

Responda APENAS com um JSON no formato:
{{"flashcards": [{{"palavra": "...", "traducao": "...", "exemplo": "...", "truque_memorizacao": "..."}}]}}
"""


def prompt_quiz(lesson: Lesson) -> str:
    exemplos_texto = "\n".join(f"- {e.frase_en} ({e.frase_pt})" for e in lesson.exemplos)

    return f"""Você é um professor de inglês criando um quiz de múltipla escolha
para um aluno brasileiro iniciante, baseado no conteúdo que ele acabou de estudar.

Contexto da lição:
Título: {lesson.titulo}
Tema: {lesson.tema}
Gramática ensinada: {lesson.texto_gramatica}
Frases de exemplo da lição:
{exemplos_texto}

Tarefa: crie exatamente 10 perguntas de múltipla escolha testando a gramática e
o vocabulário dessa lição especificamente (não conteúdo genérico de inglês).
Cada pergunta deve ter 4 alternativas, sendo só uma correta. As alternativas
erradas devem ser plausíveis (erros comuns de quem está aprendendo), não
absurdas.

Responda APENAS com um JSON no formato:
{{"perguntas": [
  {{
    "pergunta": "...",
    "opcoes": ["...", "...", "...", "..."],
    "resposta_correta": "..."
  }}
]}}

O campo "resposta_correta" deve ser IDÊNTICO a uma das strings em "opcoes".
"""


def prompt_conversa(lesson: Lesson, historico: list) -> str:
    """
    Monta o prompt de conversa. `historico` é a lista de ConversationMessage
    já salvos nessa sessão, em ordem cronológica (pode estar vazia, no caso
    da primeira mensagem — aí a IA inicia a conversa sozinha).
    """
    linhas_historico = "\n".join(
        f"{'Aluno' if m.autor == 'usuario' else 'Você'}: {m.texto}" for m in historico
    )

    if not historico:
        instrucao = (
            "Esta é a primeira mensagem da conversa. Inicie você mesmo, cumprimentando "
            "o aluno de forma calorosa e fazendo uma pergunta simples relacionada ao tema "
            "da lição, pra puxar assunto."
        )
    else:
        instrucao = (
            "Responda à ÚLTIMA mensagem do aluno, dando continuidade natural à conversa "
            "(pode fazer uma pergunta de volta pra manter o diálogo fluindo)."
        )

    return f"""Você está desempenhando o papel de um falante nativo de inglês batendo papo
casualmente com um aluno brasileiro iniciante, sobre o tema "{lesson.tema}"
(contexto da lição: {lesson.titulo} — {lesson.texto_gramatica}).

Regras:
- Responda SEMPRE em inglês simples, nível iniciante/intermediário, tom amigável e natural.
- Mantenha as respostas curtas (2-4 frases), como uma conversa real por mensagem, não um texto longo.
- Se a ÚLTIMA mensagem do aluno (não as anteriores) tiver algum erro claro de gramática
  ou vocabulário, aponte isso no campo "erro_corrigido": explique em português, de forma
  breve e encorajadora, qual foi o erro e a forma correta. Se não houver erro perceptível
  ou for a primeira mensagem, deixe "erro_corrigido" como null.

Histórico da conversa até agora:
{linhas_historico if linhas_historico else "(nenhuma mensagem ainda)"}

{instrucao}

Responda APENAS com um JSON no formato:
{{"resposta": "sua resposta em inglês aqui", "erro_corrigido": "explicação em português do erro, ou null"}}
"""


def prompt_traduzir_e_gerar_perguntas(texto_pt: str) -> str:
    return f"""Você é um professor de inglês. O aluno colou o texto abaixo, em português,
para usar como material de estudo (motor de imersão).

Texto do aluno:
\"\"\"
{texto_pt}
\"\"\"

Tarefa:
1. Traduza o texto para o inglês, de forma natural (não precisa ser literal palavra por
   palavra, mas deve manter o sentido e o tom do original).
2. Crie de 4 a 6 perguntas em português testando vocabulário, frases-chave e compreensão
   do texto traduzido — perguntas que só quem entendeu o texto em inglês consegue responder.
   Inclua a resposta correta de cada uma.

Responda APENAS com um JSON no formato:
{{"texto_en": "...", "perguntas": [{{"pergunta": "...", "resposta": "..."}}]}}
"""


def prompt_gerar_texto_por_tema(tema: str) -> str:
    return f"""Você é um professor de inglês criando material de leitura para um aluno
brasileiro iniciante/intermediário.

Tema solicitado pelo aluno: "{tema}"

Escreva um texto curto (4 a 6 frases), em português do Brasil, sobre esse tema — algo
simples, didático e neutro, adequado para depois virar exercício de tradução e
compreensão em inglês.

Responda APENAS com um JSON no formato:
{{"texto_pt": "..."}}
"""


def prompt_prova_final(capitulo, licoes: list) -> str:
    """
    Prova final de um capítulo: revisa o conteúdo de TODAS as lições dos
    níveis desse capítulo, misturando os temas em vez de focar em um só.
    """
    resumo_licoes = "\n\n".join(
        f"--- {licao.titulo} ({licao.tema}) ---\n{licao.texto_gramatica}"
        for licao in licoes
    )

    return f"""Você é um professor de inglês criando a PROVA FINAL do capítulo
"{capitulo.nome}" para um aluno brasileiro. Essa prova revisa TUDO que foi
estudado nos níveis desse capítulo — não é sobre um tema só, é uma mistura.

Conteúdo estudado no capítulo (resumo de cada nível):
{resumo_licoes}

Tarefa: crie exatamente 15 perguntas de múltipla escolha, misturando os
diferentes temas/tempos verbais estudados ao longo do capítulo (não
concentre todas as perguntas em um único nível — distribua entre os
temas). Cada pergunta com 4 alternativas, só uma correta, alternativas
erradas plausíveis (erros comuns de quem está aprendendo).

Responda APENAS com um JSON no formato:
{{"perguntas": [
  {{
    "pergunta": "...",
    "opcoes": ["...", "...", "...", "..."],
    "resposta_correta": "..."
  }}
]}}

O campo "resposta_correta" deve ser IDÊNTICO a uma das strings em "opcoes".
"""
