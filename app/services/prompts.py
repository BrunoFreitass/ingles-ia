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
- Inclua também a tradução da SUA resposta (a que você escreveu em inglês) para português do
  Brasil, no campo "resposta_pt" — é essencial pra alunos iniciantes que ainda não conseguem
  ler inglês sozinhos. A tradução deve ser natural, não literal palavra por palavra.

Histórico da conversa até agora:
{linhas_historico if linhas_historico else "(nenhuma mensagem ainda)"}

{instrucao}

Responda APENAS com um JSON no formato:
{{"resposta": "sua resposta em inglês aqui", "resposta_pt": "a tradução dessa resposta em português",
  "erro_corrigido": "explicação em português do erro, ou null"}}
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


_DESCRICAO_TIPO_EXERCICIO = {
    "imagem_palavra": (
        'Mostra um emoji representando um objeto/coisa e o aluno escolhe a palavra certa. '
        'dados: {"imagem_emoji": "📱", "opcoes": ["book", "phone", "table", "chair"]}. '
        'resposta_correta: a string da opção certa (ex: "phone").'
    ),
    "palavra_imagem": (
        'Mostra uma palavra em inglês e o aluno escolhe o emoji certo entre 4 opções. '
        'dados: {"palavra": "phone", "opcoes_emoji": ["📖", "📱", "🪑", "🚪"]}. '
        'resposta_correta: a string do emoji certo (ex: "📱").'
    ),
    "ligar": (
        'O aluno liga cada palavra ao emoji correspondente (3 ou 4 pares). '
        'dados: {"palavras": ["book", "phone", "chair"], "emojis_embaralhados": ["🪑", "📱", "📖"]}. '
        'resposta_correta: objeto mapeando cada palavra ao emoji certo, ex: '
        '{"book": "📖", "phone": "📱", "chair": "🪑"}.'
    ),
    "completar": (
        'Frase com uma lacuna "___" e 4 opções pra completar. '
        'dados: {"frase": "This is a ___.", "opcoes": ["phone", "blue", "run", "yesterday"]}. '
        'resposta_correta: a string da opção certa (ex: "phone").'
    ),
    "organizar_frase": (
        'Palavras embaralhadas que o aluno organiza pra formar a frase correta. '
        'dados: {"palavras_embaralhadas": ["is", "This", "a", "phone"]}. '
        'resposta_correta: a frase correta como string (ex: "This is a phone.").'
    ),
    "escolha_multipla": (
        'Pergunta com 4 alternativas, só uma correta (alternativas erradas plausíveis, '
        'erros comuns de quem está aprendendo). '
        'dados: {"pergunta": "What is this?", "opcoes": ["It\'s a phone.", "I\'m a phone.", '
        '"It are phone.", "Phone yesterday."]}. resposta_correta: a string da opção certa.'
    ),
    "ouvir_escolher": (
        'Uma frase curta que o aluno vai OUVIR (via texto-pra-voz no frontend) e depois escolhe '
        'a opção que corresponde ao que ouviu. '
        'dados: {"texto_audio": "This is my phone.", "opcoes": ["This is my phone.", '
        '"This is my phony.", "This is my food.", "This is my form."]}. '
        'resposta_correta: a string da opção certa.'
    ),
    "interpretacao": (
        'Um texto curto (2-4 frases) seguido de uma pergunta de compreensão com 4 alternativas. '
        'dados: {"texto": "John works at a hospital. He is a doctor.", '
        '"pergunta": "Where does John work?", "opcoes": ["School", "Hospital", "Restaurant", "Bank"]}. '
        'resposta_correta: a string da opção certa.'
    ),
    "producao": (
        'Produção livre — o aluno escreve uma resposta aberta, sem gabarito fixo (é só prática, '
        'não é corrigido automaticamente). '
        'dados: {"prompt": "Tell me about your daily routine."}. resposta_correta: null.'
    ),
}


def prompt_exercicios(
    lesson,
    tipos_permitidos: list[str],
    vocabulario_reforco: list[str],
    nivel_dificuldade: str,
) -> str:
    """
    Gera até 10 exercícios de prática variados pra uma lição, restritos aos
    `tipos_permitidos` (a variedade de tipos cresce conforme a trilha avança
    — ver content_generation_service.py) e reforçando, quando possível,
    palavras de `vocabulario_reforco` (vocabulário já ensinado em capítulos
    anteriores da mesma trilha, pra criar a progressão em que palavras
    antigas voltam em frases mais complexas).
    """
    exemplos_texto = "\n".join(f"- {e.frase_en} ({e.frase_pt})" for e in lesson.exemplos)
    tipos_descricao = "\n".join(f'- "{t}": {_DESCRICAO_TIPO_EXERCICIO[t]}' for t in tipos_permitidos)
    reforco_texto = (
        ", ".join(vocabulario_reforco)
        if vocabulario_reforco
        else "(nenhum ainda — este é um dos primeiros capítulos)"
    )

    return f"""Você é um professor de inglês criando exercícios de PRÁTICA (não é a prova, é o
treino antes dela) para um aluno brasileiro, nível de dificuldade: {nivel_dificuldade}.

Contexto da lição:
Título: {lesson.titulo}
Tema: {lesson.tema}
Gramática ensinada: {lesson.texto_gramatica}
Frases de exemplo da lição:
{exemplos_texto}

Vocabulário de capítulos anteriores pra reforçar quando fizer sentido (não é obrigatório usar
todas, mas aproveite quando encaixar naturalmente, misturado ao vocabulário novo desta lição):
{reforco_texto}

Tarefa: crie exatamente 10 exercícios, usando SOMENTE os tipos abaixo (pode repetir tipos,
mas varie ao longo dos 10 — não use o mesmo tipo mais de 3 vezes seguidas):

{tipos_descricao}

REGRA CRÍTICA sobre emojis (campos "imagem_emoji", "opcoes_emoji", "emojis_embaralhados"):
use SEMPRE um emoji Unicode de verdade (ex: 📱🪑📖🚪), NUNCA texto, palavra ou letras de
qualquer idioma/alfabeto no lugar do emoji. Nem toda palavra tem um emoji perfeito — nesses
casos, escolha o emoji mais parecido visualmente em vez de inventar um símbolo ou escrever a
palavra. Exemplos de aproximação aceitável: "table" → 🍽️ (ou 🛋️), "bag" → 🎒 (ou 💼), "pencil"
→ ✏️, "pen" → 🖊️, "window" → 🪟, "door" → 🚪, "computer" → 💻, "chair" → 🪑, "book" → 📖,
"phone" → 📱. Se realmente não houver nenhum emoji razoável pra uma palavra do vocabulário
desta lição, NÃO use os tipos "imagem_palavra", "palavra_imagem" ou "ligar" pra essa palavra —
use outro tipo (ex: "completar" ou "escolha_multipla") no lugar.

Para cada exercício, retorne:
- "tipo": um dos tipos listados acima, exatamente como escrito
- "enunciado": uma instrução curta em português pro aluno (ex: "Escolha a palavra certa")
- "dados": o objeto conforme o formato descrito pra esse tipo (SEM revelar a resposta certa)
- "resposta_correta": a resposta certa conforme o formato descrito pra esse tipo (string, objeto,
  ou null pra "producao")

Responda APENAS com um JSON no formato:
{{"exercicios": [
  {{"tipo": "...", "enunciado": "...", "dados": {{...}}, "resposta_correta": ...}}
]}}
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