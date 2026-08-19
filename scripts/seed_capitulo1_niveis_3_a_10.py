"""
Cria o Capítulo 1 (se ainda não existir), vincula os níveis 1 e 2 já
existentes a ele (sem alterar nome/conteúdo/progresso de ninguém), e
adiciona os níveis 3 a 10 com conteúdo novo escrito à mão.

Idempotente: seguro rodar mais de uma vez, e seguro rodar em produção
(não apaga nada, só adiciona o que ainda não existe).

Uso:
    python scripts/seed_capitulo1_niveis_3_a_10.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.models.level import Capitulo, Lesson, LessonExample, Level  # noqa: E402

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# --- 1. Cria o Capítulo 1, se ainda não existir ---
capitulo1 = db.query(Capitulo).filter(Capitulo.ordem == 1).first()
if not capitulo1:
    capitulo1 = Capitulo(
        ordem=1,
        nome="O Básico do Dia a Dia",
        descricao="10 níveis para você se virar em inglês nas situações mais comuns do cotidiano.",
        nota_minima_prova_final=7.0,
    )
    db.add(capitulo1)
    db.flush()
    print(f"Capítulo 1 criado (id={capitulo1.id}).")
else:
    print(f"Capítulo 1 já existe (id={capitulo1.id}), reaproveitando.")

# --- 2. Vincula os níveis 1 e 2 já existentes ao Capítulo 1 (sem mexer em mais nada) ---
for ordem_existente in (1, 2):
    nivel_existente = db.query(Level).filter(Level.ordem == ordem_existente).first()
    if nivel_existente and nivel_existente.capitulo_id is None:
        nivel_existente.capitulo_id = capitulo1.id
        print(f"Nível {ordem_existente} ('{nivel_existente.nome}') vinculado ao Capítulo 1.")
    elif nivel_existente:
        print(f"Nível {ordem_existente} já estava vinculado a um capítulo, não mexi.")
    else:
        print(f"AVISO: nível de ordem {ordem_existente} não encontrado — rode scripts/seed.py primeiro.")

db.commit()


def criar_nivel_se_nao_existir(ordem, nome, descricao):
    existente = db.query(Level).filter(Level.ordem == ordem).first()
    if existente:
        print(f"Nível {ordem} ('{existente.nome}') já existe, pulando.")
        return None
    nivel = Level(
        ordem=ordem,
        nome=nome,
        descricao=descricao,
        nota_minima_para_avancar=7.0,
        capitulo_id=capitulo1.id,
    )
    db.add(nivel)
    db.flush()
    print(f"Nível {ordem} ('{nome}') criado (id={nivel.id}).")
    return nivel


def criar_licao(nivel, titulo, tema, texto_gramatica, erros_comuns, exemplos):
    licao = Lesson(
        level_id=nivel.id,
        titulo=titulo,
        tema=tema,
        texto_gramatica=texto_gramatica,
        erros_comuns_json=json.dumps(erros_comuns, ensure_ascii=False),
        ordem=1,
    )
    db.add(licao)
    db.flush()
    for frase_en, frase_pt in exemplos:
        db.add(LessonExample(lesson_id=licao.id, frase_en=frase_en, frase_pt=frase_pt))
    return licao


# ---------------------------------------------------------------------------
# Nível 3 — O Que Está Acontecendo (Present Continuous)
# ---------------------------------------------------------------------------
nivel3 = criar_nivel_se_nao_existir(
    3, "O Que Está Acontecendo", "Descrever ações acontecendo agora, lugares e situações do momento."
)
if nivel3:
    criar_licao(
        nivel3,
        titulo="Ações Acontecendo Agora",
        tema="Present Continuous — descrever o que está rolando neste momento",
        texto_gramatica=(
            "O Present Continuous (be + verbo-ando) descreve ações acontecendo NESTE momento, "
            "diferente do Simple Present (que descreve hábitos). Formamos com o verbo 'to be' "
            "(am/is/are) + o verbo principal com '-ing': 'I am working', 'She is studying', "
            "'They are watching TV'. Também usamos pra planos já combinados no futuro próximo: "
            "'I'm meeting her tomorrow' (já está marcado)."
        ),
        erros_comuns=[
            "Esquecer o verbo 'to be': dizer 'I working' em vez de 'I am working'.",
            "Usar Present Continuous pra hábitos: dizer 'I am waking up at 7am every day' em vez de 'I wake up at 7am every day' (isso é rotina, não algo acontecendo agora).",
            "Errar a grafia do '-ing': 'runing' em vez de 'running' (dobra a consoante), ou 'writeing' em vez de 'writing' (tira o 'e').",
        ],
        exemplos=[
            ("What are you doing right now?", "O que você está fazendo agora?"),
            ("I'm cooking dinner.", "Estou cozinhando o jantar."),
            ("She's not listening to me.", "Ela não está me escutando."),
            ("We're meeting some friends tonight.", "Vamos nos encontrar com uns amigos hoje à noite."),
        ],
    )

# ---------------------------------------------------------------------------
# Nível 4 — O Que Aconteceu (Simple Past, mais a fundo)
# ---------------------------------------------------------------------------
nivel4 = criar_nivel_se_nao_existir(
    4, "O Que Aconteceu", "Contar acontecimentos passados com mais detalhe — verbos regulares e irregulares."
)
if nivel4:
    criar_licao(
        nivel4,
        titulo="Verbos Irregulares no Passado",
        tema="Simple Past — verbos que não seguem a regra do '-ed'",
        texto_gramatica=(
            "Verbos regulares ganham '-ed' no passado (work → worked). Mas muitos verbos comuns "
            "são irregulares e mudam de forma completamente: go → went, have → had, see → saw, "
            "eat → ate, make → made. Não tem fórmula — é decorar mesmo, mas os mais usados no dia "
            "a dia valem a pena memorizar primeiro. Pra perguntas/negativas, o verbo volta pra "
            "forma base: 'Did you go?' (não 'Did you went?'), 'I didn't go' (não 'I didn't went')."
        ),
        erros_comuns=[
            "Regularizar verbo irregular: dizer 'goed' em vez de 'went', ou 'eated' em vez de 'ate'.",
            "Conjugar o verbo depois de 'did': dizer 'Did you went?' em vez de 'Did you go?' — o 'did' já carrega o passado, o verbo fica na forma base.",
            "Confundir 'was/were' (passado de 'to be') com o passado de verbos de ação: dizer 'I was go' em vez de 'I went'.",
        ],
        exemplos=[
            ("I went to the doctor yesterday.", "Eu fui ao médico ontem."),
            ("She saw an old friend at the mall.", "Ela viu uma amiga antiga no shopping."),
            ("We had a great time at the party.", "A gente se divertiu muito na festa."),
            ("Did you eat breakfast this morning?", "Você tomou café da manhã hoje?"),
        ],
    )

# ---------------------------------------------------------------------------
# Nível 5 — Meus Planos (Going to / Will)
# ---------------------------------------------------------------------------
nivel5 = criar_nivel_se_nao_existir(
    5, "Meus Planos", "Falar sobre o futuro — planos, desejos e objetivos."
)
if nivel5:
    criar_licao(
        nivel5,
        titulo="Planos e Decisões no Futuro",
        tema="Going to vs. Will — duas formas de falar do futuro",
        texto_gramatica=(
            "'Going to' (be + going to + verbo) é pra planos já decididos: 'I'm going to travel "
            "next month' (já está decidido). 'Will' é pra decisões espontâneas, promessas, ou "
            "previsões: 'I think it will rain' (previsão), 'I'll help you' (decisão na hora, "
            "oferecendo ajuda). Na prática, os dois às vezes se misturam no uso cotidiano, mas "
            "essa é a diferença central: plano já pensado = going to; decisão do momento = will."
        ),
        erros_comuns=[
            "Esquecer o 'to' no 'going to': dizer 'I'm going travel' em vez de 'I'm going to travel'.",
            "Usar 'will' pra planos já combinados: dizer 'I will travel next month' quando na verdade já estava tudo decidido — o natural seria 'going to'.",
            "Contrair errado o 'will': escrever 'I'll'll' ou esquecer o apóstrofo, ou confundir 'I'll' (I will) com 'I'd' (I would).",
        ],
        exemplos=[
            ("I'm going to study abroad next year.", "Eu vou estudar fora ano que vem."),
            ("I think I'll call her later.", "Acho que vou ligar pra ela mais tarde."),
            ("What are you going to do this weekend?", "O que você vai fazer neste fim de semana?"),
            ("Don't worry, I'll take care of it.", "Não se preocupa, eu cuido disso."),
        ],
    )

# ---------------------------------------------------------------------------
# Nível 6 — Minha Opinião
# ---------------------------------------------------------------------------
nivel6 = criar_nivel_se_nao_existir(
    6, "Minha Opinião", "Opiniões, preferências, comparações, concordar e discordar."
)
if nivel6:
    criar_licao(
        nivel6,
        titulo="Dando Sua Opinião",
        tema="Expressar opinião, comparar coisas, concordar e discordar",
        texto_gramatica=(
            "Pra dar opinião: 'I think...', 'In my opinion...', 'I believe...'. Pra comparar duas "
            "coisas, use o comparativo: adjetivos curtos ganham '-er' ('cheaper', 'faster'), "
            "adjetivos longos usam 'more' ('more expensive', 'more interesting'). Pra concordar: "
            "'I agree', 'That's true', 'Exactly'. Pra discordar educadamente: 'I see your point, "
            "but...', 'I'm not sure I agree', 'Actually, I think...'."
        ),
        erros_comuns=[
            "Misturar as duas formas de comparativo: dizer 'more cheaper' em vez de só 'cheaper' ou só 'more expensive'.",
            "Traduzir 'Eu acho que' como 'I find that' — o natural em inglês é 'I think that'.",
            "Discordar de forma direta demais ('You're wrong') em vez de suavizar ('I see it differently' / 'I'm not sure about that').",
        ],
        exemplos=[
            ("In my opinion, this movie is better than the book.", "Na minha opinião, esse filme é melhor que o livro."),
            ("I think remote work is more productive.", "Eu acho que trabalho remoto é mais produtivo."),
            ("I agree with you on that.", "Eu concordo com você nisso."),
            ("I see your point, but I still prefer the original.", "Entendo seu ponto, mas ainda prefiro o original."),
        ],
    )

# ---------------------------------------------------------------------------
# Nível 7 — Situações Reais
# ---------------------------------------------------------------------------
nivel7 = criar_nivel_se_nao_existir(
    7, "Situações Reais", "Se virar em inglês: restaurante, trabalho, viagem, compras, telefone, problemas."
)
if nivel7:
    criar_licao(
        nivel7,
        titulo="No Restaurante e Fazendo Compras",
        tema="Frases práticas pra pedir comida e comprar coisas",
        texto_gramatica=(
            "Situações do dia a dia têm frases prontas que vale decorar como bloco, sem precisar "
            "montar gramática do zero na hora. No restaurante: 'Could I see the menu, please?', "
            "'I'll have the...', 'Can I get the check, please?'. Fazendo compras: 'How much is "
            "this?', 'Do you have this in a different size?', 'I'm just looking, thanks' (quando "
            "não quer ajuda do vendedor ainda)."
        ),
        erros_comuns=[
            "Traduzir 'Eu vou querer' ao pé da letra como 'I go want' — o certo é 'I'll have...' ou 'I'd like...'.",
            "Esquecer o 'please' em pedidos, que em inglês soa mais educado/esperado do que em português em situações formais.",
            "Confundir 'check' (a conta, no inglês americano) com 'bill' (mais comum no inglês britânico) — os dois funcionam, mas variam por região.",
        ],
        exemplos=[
            ("Could I see the menu, please?", "Poderia me trazer o cardápio, por favor?"),
            ("I'll have the grilled chicken, please.", "Eu vou querer o frango grelhado, por favor."),
            ("How much is this?", "Quanto custa isso?"),
            ("Can I get the check, please?", "Pode trazer a conta, por favor?"),
        ],
    )

# ---------------------------------------------------------------------------
# Nível 8 — Contar Histórias
# ---------------------------------------------------------------------------
nivel8 = criar_nivel_se_nao_existir(
    8, "Contar Histórias", "Falar com mais naturalidade — tempos verbais combinados, conectores, experiências."
)
if nivel8:
    criar_licao(
        nivel8,
        titulo="Narrando uma Experiência",
        tema="Combinar tempos verbais e usar conectores pra contar uma história",
        texto_gramatica=(
            "Contar uma história bem em inglês combina tempos verbais: Simple Past pra ação "
            "principal ('I went to the beach'), Past Continuous pro cenário/contexto ('It was "
            "raining when I arrived'). Conectores dão fluidez: 'then', 'after that', 'suddenly', "
            "'in the end'. 'While' conecta duas ações acontecendo ao mesmo tempo no passado: "
            "'While I was walking, I saw an old friend.'"
        ),
        erros_comuns=[
            "Usar só Simple Past pra tudo, sem o Past Continuous de contexto: 'It rained when I arrived' soa menos natural que 'It was raining when I arrived'.",
            "Esquecer conectores e falar frases soltas sem ligação, o que deixa a história truncada.",
            "Confundir 'while' (durante, ação em andamento) com 'when' (no momento em que algo aconteceu) — 'While I was cooking, the phone rang' (não 'When I was cooking...').",
        ],
        exemplos=[
            ("While I was walking home, it started to rain.", "Enquanto eu voltava pra casa andando, começou a chover."),
            ("Suddenly, I heard a strange noise.", "De repente, eu ouvi um barulho estranho."),
            ("After that, we decided to leave early.", "Depois disso, decidimos ir embora cedo."),
            ("In the end, everything worked out fine.", "No final, tudo deu certo."),
        ],
    )

# ---------------------------------------------------------------------------
# Nível 9 — Inglês Profissional
# ---------------------------------------------------------------------------
nivel9 = criar_nivel_se_nao_existir(
    9, "Inglês Profissional", "Usar inglês no trabalho e nos estudos — e-mails, reuniões, entrevistas."
)
if nivel9:
    criar_licao(
        nivel9,
        titulo="E-mails e Reuniões",
        tema="Frases formais pra ambiente profissional",
        texto_gramatica=(
            "E-mails profissionais têm estrutura própria: abrir com 'Dear [Nome]' ou 'Hi [Nome]' "
            "(mais informal), explicar o motivo logo no início ('I'm writing to...'), e fechar com "
            "'Best regards' ou 'Best'. Em reuniões, frases úteis: 'Could you clarify that?', "
            "'I'd like to add something', 'Let's move on to the next point'. O inglês profissional "
            "tende a ser mais indireto/educado que o cotidiano: 'Would it be possible to...?' em "
            "vez de 'Can you...?'."
        ),
        erros_comuns=[
            "Ser direto demais em contextos formais: 'I want' soa mais abrupto que 'I would like' ou 'I was hoping to'.",
            "Traduzir 'Att' (usado em português) direto — em inglês o fechamento padrão é 'Best regards' ou 'Sincerely', não existe equivalente literal de 'Att'.",
            "Misturar registro formal e informal na mesma mensagem, como abrir com 'Dear Mr. Smith' e fechar com 'See ya!'.",
        ],
        exemplos=[
            ("I'm writing to follow up on our last conversation.", "Estou escrevendo pra dar continuidade à nossa última conversa."),
            ("Would it be possible to reschedule our meeting?", "Seria possível remarcar nossa reunião?"),
            ("I'd like to add something to that point.", "Eu gostaria de acrescentar algo a esse ponto."),
            ("Thank you for your time. Best regards,", "Obrigado pelo seu tempo. Atenciosamente,"),
        ],
    )

# ---------------------------------------------------------------------------
# Nível 10 — Fluência e Naturalidade
# ---------------------------------------------------------------------------
nivel10 = criar_nivel_se_nao_existir(
    10, "Fluência e Naturalidade", "Pensar e se comunicar em inglês — expressões, phrasal verbs, argumentação."
)
if nivel10:
    criar_licao(
        nivel10,
        titulo="Phrasal Verbs do Dia a Dia",
        tema="Expressões com dois ou mais verbos que mudam de sentido",
        texto_gramatica=(
            "Phrasal verbs são combinações de verbo + preposição/advérbio que criam um sentido "
            "novo, diferente do verbo sozinho: 'give up' (desistir, não 'dar pra cima'), 'look "
            "forward to' (ansiar por algo), 'run into' (encontrar por acaso), 'figure out' "
            "(descobrir/entender algo). São essenciais pra soar natural — falantes nativos usam "
            "constantemente no dia a dia, muito mais do que os verbos formais equivalentes."
        ),
        erros_comuns=[
            "Traduzir phrasal verb ao pé da letra: 'give up' não é 'dar pra cima', é 'desistir' — precisa decorar o sentido do bloco todo, não das palavras separadas.",
            "Separar errado quando o phrasal verb é separável: 'give up it' está errado, o certo é 'give it up' (o pronome vai no meio).",
            "Usar a versão formal em contexto casual, o que soa meio estranho: dizer 'I will investigate' com amigos em vez do mais natural 'I'll look into it'.",
        ],
        exemplos=[
            ("I'm looking forward to seeing you again.", "Estou ansioso pra te ver de novo."),
            ("I ran into an old classmate yesterday.", "Encontrei um ex-colega de classe por acaso ontem."),
            ("Don't give up, you're almost there!", "Não desiste, você tá quase lá!"),
            ("Let me figure out what's wrong.", "Deixa eu descobrir o que está errado."),
        ],
    )

db.commit()
db.close()

print("\nSeed do Capítulo 1 (níveis 1-10) concluído com sucesso.")
