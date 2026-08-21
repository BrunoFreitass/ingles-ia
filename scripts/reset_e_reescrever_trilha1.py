"""
Reseta a Trilha 1 (Capitulo de ordem 1) e reescreve o conteúdo dos 10 níveis
pra seguir o plano "Inglês do Zero" (vocabulário básico, sem gramática
pesada) em vez do roadmap antigo (que pulava direto pra to be / simple
present / simple past etc.).

O QUE ESTE SCRIPT FAZ:
1. Apaga tudo que foi cacheado/gerado a partir do conteúdo antigo dos níveis
   1-10 da Trilha 1: Quiz+QuizQuestion+QuizAttempt (lição e prova final),
   Exercise+ExerciseAttempt, Flashcard+UserFlashcardProgress, e as
   ConversationSession+ConversationMessage que apontavam pra essas lições.
2. Reseta o progresso de TODOS os usuários pro Nível 1 (nivel_atual_id).
3. Reescreve nome/descrição dos 10 Levels e titulo/tema/gramática/erros
   comuns/exemplos das 10 Lessons, seguindo o vocabulário do documento
   original (Objetos, Cores, Números, Pessoas, Corpo, Família, Animais,
   Comida e Bebida, Lugares, Primeiras Frases).

Idempotente: seguro rodar mais de uma vez (sempre parte do estado atual do
banco, não duplica nada).

ATENÇÃO: isso é destrutivo pro progresso da Trilha 1 — é intencional (você
pediu reset completo). Rode com cuidado em produção; faça backup do banco
antes se quiser poder reverter.

Uso:
    python scripts/reset_e_reescrever_trilha1.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal  # noqa: E402
from app.models.conversation import ConversationMessage, ConversationSession  # noqa: E402
from app.models.exercise import Exercise, ExerciseAttempt  # noqa: E402
from app.models.flashcard import Flashcard, UserFlashcardProgress  # noqa: E402
from app.models.level import Capitulo, Lesson, LessonExample, Level  # noqa: E402
from app.models.quiz import Quiz, QuizAttempt, QuizQuestion  # noqa: E402
from app.models.user import User  # noqa: E402

db = SessionLocal()

capitulo1 = db.query(Capitulo).filter(Capitulo.ordem == 1).first()
if not capitulo1:
    print("Capítulo 1 (Trilha 1) não existe ainda — rode os seeds normais primeiro.")
    sys.exit(1)

niveis = db.query(Level).filter(Level.capitulo_id == capitulo1.id).order_by(Level.ordem).all()
if len(niveis) != 10:
    print(f"AVISO: esperado 10 níveis na Trilha 1, encontrei {len(niveis)}. Prosseguindo mesmo assim.")

nivel_ids = [n.id for n in niveis]
lesson_ids = [licao.id for n in niveis for licao in n.lessons]

print(f"Trilha 1 (Capitulo id={capitulo1.id}): {len(niveis)} níveis, {len(lesson_ids)} lições.")

# --- 1. Apaga cache/progresso gerado a partir do conteúdo antigo ---------

if lesson_ids:
    quizzes_licao = db.query(Quiz).filter(Quiz.lesson_id.in_(lesson_ids)).all()
    quiz_ids = [q.id for q in quizzes_licao]
    if quiz_ids:
        n = db.query(QuizAttempt).filter(QuizAttempt.quiz_id.in_(quiz_ids)).delete(synchronize_session=False)
        print(f"  {n} QuizAttempt (lição) apagadas.")
        n = db.query(QuizQuestion).filter(QuizQuestion.quiz_id.in_(quiz_ids)).delete(synchronize_session=False)
        print(f"  {n} QuizQuestion (lição) apagadas.")
        n = db.query(Quiz).filter(Quiz.id.in_(quiz_ids)).delete(synchronize_session=False)
        print(f"  {n} Quiz (lição) apagados.")

    n = db.query(ExerciseAttempt).filter(
        ExerciseAttempt.exercise_id.in_(db.query(Exercise.id).filter(Exercise.lesson_id.in_(lesson_ids)))
    ).delete(synchronize_session=False)
    print(f"  {n} ExerciseAttempt apagadas.")
    n = db.query(Exercise).filter(Exercise.lesson_id.in_(lesson_ids)).delete(synchronize_session=False)
    print(f"  {n} Exercise apagados.")

    sessoes = db.query(ConversationSession).filter(ConversationSession.lesson_id.in_(lesson_ids)).all()
    sessao_ids = [s.id for s in sessoes]
    if sessao_ids:
        n = db.query(ConversationMessage).filter(
            ConversationMessage.session_id.in_(sessao_ids)
        ).delete(synchronize_session=False)
        print(f"  {n} ConversationMessage apagadas.")
        n = db.query(ConversationSession).filter(ConversationSession.id.in_(sessao_ids)).delete(
            synchronize_session=False
        )
        print(f"  {n} ConversationSession apagadas.")

    n = db.query(LessonExample).filter(LessonExample.lesson_id.in_(lesson_ids)).delete(synchronize_session=False)
    print(f"  {n} LessonExample antigos apagados (serão recriados com o novo conteúdo).")

if nivel_ids:
    n = db.query(UserFlashcardProgress).filter(
        UserFlashcardProgress.flashcard_id.in_(db.query(Flashcard.id).filter(Flashcard.nivel_id.in_(nivel_ids)))
    ).delete(synchronize_session=False)
    print(f"  {n} UserFlashcardProgress apagadas.")
    n = db.query(Flashcard).filter(Flashcard.nivel_id.in_(nivel_ids)).delete(synchronize_session=False)
    print(f"  {n} Flashcard apagados.")

prova_final = db.query(Quiz).filter(Quiz.capitulo_id == capitulo1.id).first()
if prova_final:
    n = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == prova_final.id).delete(synchronize_session=False)
    print(f"  {n} QuizAttempt (prova final) apagadas.")
    db.query(QuizQuestion).filter(QuizQuestion.quiz_id == prova_final.id).delete(synchronize_session=False)
    db.query(Quiz).filter(Quiz.id == prova_final.id).delete(synchronize_session=False)
    print("  Prova final da Trilha 1 apagada (será regerada).")

# O plano novo é 1 lição por nível — mas o seed antigo criava 2 lições no
# Nível 1 (ex: "Apresentações e Saudações" + "No Café da Manhã"). Se sobrar
# lição extra, o resto do script só reescreve a primeira (lessons[0]) e a(s)
# outra(s) ficam órfãs com conteúdo velho e sem exemplos. Aqui a gente apaga
# o excedente ANTES de reescrever, mantendo só a lição mais antiga (menor id)
# de cada nível.
db.expire_all()  # garante que nivel.lessons reflete os deletes já commitados acima
for nivel in niveis:
    licoes_do_nivel = db.query(Lesson).filter(Lesson.level_id == nivel.id).order_by(Lesson.id).all()
    if len(licoes_do_nivel) > 1:
        extras = licoes_do_nivel[1:]
        extras_ids = [licao.id for licao in extras]
        print(f"  Nível {nivel.ordem}: {len(extras)} lição(ões) extra encontrada(s), apagando (ids={extras_ids}).")
        db.query(LessonExample).filter(LessonExample.lesson_id.in_(extras_ids)).delete(synchronize_session=False)
        db.query(Lesson).filter(Lesson.id.in_(extras_ids)).delete(synchronize_session=False)
db.commit()

# --- 2. Reseta progresso de todos os usuários pro Nível 1 -----------------

nivel1 = next((n for n in niveis if n.ordem == 1), None)
if nivel1:
    n = db.query(User).update({User.nivel_atual_id: nivel1.id}, synchronize_session=False)
    print(f"  Progresso resetado: {n} usuário(s) voltaram pro Nível 1.")

db.commit()

# --- 3. Reescreve o conteúdo dos 10 níveis --------------------------------


def atualizar_nivel(ordem, nome, descricao):
    nivel = next((n for n in niveis if n.ordem == ordem), None)
    if not nivel:
        print(f"  AVISO: nível de ordem {ordem} não encontrado, pulando.")
        return None
    nivel.nome = nome
    nivel.descricao = descricao
    return nivel


def atualizar_ou_criar_licao(nivel, titulo, tema, texto_gramatica, erros_comuns, exemplos):
    licao = nivel.lessons[0] if nivel.lessons else None
    if licao is None:
        licao = Lesson(level_id=nivel.id, ordem=1)
        db.add(licao)

    licao.titulo = titulo
    licao.tema = tema
    licao.texto_gramatica = texto_gramatica
    licao.erros_comuns_json = json.dumps(erros_comuns, ensure_ascii=False)
    db.flush()  # garante licao.id (pra criar/vincular LessonExample) só depois dos campos obrigatórios setados

    for frase_en, frase_pt in exemplos:
        db.add(LessonExample(lesson_id=licao.id, frase_en=frase_en, frase_pt=frase_pt))

    return licao


nivel1 = atualizar_nivel(1, "Objetos do Dia a Dia", "Reconhecer os nomes dos objetos mais comuns ao seu redor.")
if nivel1:
    atualizar_ou_criar_licao(
        nivel1,
        titulo="Objetos do Dia a Dia",
        tema="Vocabulário: objetos comuns — book, pen, pencil, phone, computer, table, chair, door, window, bag",
        texto_gramatica=(
            "Aqui você só vai aprender os NOMES dos objetos — sem gramática ainda. Em inglês, "
            "assim como em português, cada objeto tem um nome próprio. Pra falar 'isto é um/uma', "
            "usamos 'this is a' + o objeto: 'this is a book' (isto é um livro). Não se preocupe em "
            "decorar regra nenhuma agora, só em reconhecer a palavra."
        ),
        erros_comuns=[
            "Confundir 'chair' (cadeira) com 'table' (mesa) — são parecidas em som pra quem tá "
            "começando, mas totalmente diferentes.",
            "Esquecer o 'a' antes do objeto: dizer 'this is book' em vez de 'this is a book'.",
            "Trocar 'phone' por 'fone' (falso cognato) — 'phone' é o aparelho inteiro, não o fone de ouvido.",
        ],
        exemplos=[
            ("This is a book.", "Isto é um livro."),
            ("This is a phone.", "Isto é um telefone."),
            ("Where is my bag?", "Cadê minha bolsa?"),
            ("Open the door, please.", "Abra a porta, por favor."),
        ],
    )

nivel2 = atualizar_nivel(2, "Cores", "Aprender as cores e começar a combiná-las com os objetos do capítulo anterior.")
if nivel2:
    atualizar_ou_criar_licao(
        nivel2,
        titulo="Cores",
        tema="Vocabulário: cores — red, blue, green, yellow, black, white, orange, pink, purple, brown",
        texto_gramatica=(
            "Agora que você já sabe os nomes de alguns objetos, vamos aprender as cores e "
            "combiná-las: em inglês, a cor vem ANTES do objeto — 'a red book' (um livro vermelho), "
            "nunca 'a book red'. É o contrário da ordem mais comum em português."
        ),
        erros_comuns=[
            "Colocar a cor depois do objeto (ordem do português): dizer 'a book red' em vez de 'a red book'.",
            "Confundir 'blue' com 'black' — parecidas de ouvido no começo.",
            "Esquecer que a cor não muda de forma em inglês (não tem 'vermelha'/'vermelho' — é sempre 'red').",
        ],
        exemplos=[
            ("This is a red book.", "Isto é um livro vermelho."),
            ("My phone is blue.", "Meu telefone é azul."),
            ("The door is white.", "A porta é branca."),
            ("I have a green bag.", "Eu tenho uma bolsa verde."),
        ],
    )

nivel3 = atualizar_nivel(3, "Números", "Contar de 1 a 20 e combinar números com objetos no plural.")
if nivel3:
    atualizar_ou_criar_licao(
        nivel3,
        titulo="Números",
        tema="Vocabulário: números 1-20 combinados com objetos no plural — two books, three pens, five chairs",
        texto_gramatica=(
            "Números de 1 a 20: one, two, three, four, five, six, seven, eight, nine, ten, eleven, "
            "twelve, thirteen, fourteen, fifteen, sixteen, seventeen, eighteen, nineteen, twenty. "
            "Quando o número é maior que 1, o objeto geralmente ganha um 's' no final (plural): "
            "'two books', 'three pens' — igual em português (dois livros, três canetas)."
        ),
        erros_comuns=[
            "Esquecer o 's' do plural depois do número: dizer 'two book' em vez de 'two books'.",
            "Confundir 'thirteen' (13) com 'thirty' (30) — o som é parecido, mas são bem diferentes.",
            "Usar 'a'/'an' junto com o número: dizer 'a two books' (não existe, número já basta).",
        ],
        exemplos=[
            ("I have two books.", "Eu tenho dois livros."),
            ("She has three red pens.", "Ela tem três canetas vermelhas."),
            ("There are five chairs.", "Tem cinco cadeiras."),
            ("I need ten dollars.", "Eu preciso de dez dólares."),
        ],
    )

nivel4 = atualizar_nivel(4, "Pessoas", "Vocabulário sobre pessoas e como descrevê-las com o que você já aprendeu.")
if nivel4:
    atualizar_ou_criar_licao(
        nivel4,
        titulo="Pessoas",
        tema="Vocabulário: pessoas — man, woman, boy, girl, child, baby, friend, teacher, student, family",
        texto_gramatica=(
            "Palavras pra falar sobre pessoas: man (homem), woman (mulher), boy (menino), girl "
            "(menina), child (criança), baby (bebê), friend (amigo/a), teacher (professor/a), "
            "student (aluno/a), family (família). Dá pra combinar com o que você já sabe: 'a boy', "
            "'a young boy' (um menino jovem), 'a blue shirt' (uma camisa azul)."
        ),
        erros_comuns=[
            "Confundir 'boy' (menino) com 'buy' (comprar) — soam parecido pra quem começou agora.",
            "Usar 'children' (plural de child) como se fosse singular: 'a children' está errado, é 'a child'.",
            "Esquecer que 'teacher' e 'student' não mudam de forma pra homem/mulher (não existe 'teachera').",
        ],
        exemplos=[
            ("She is a teacher.", "Ela é professora."),
            ("He is a young boy.", "Ele é um menino jovem."),
            ("This is my friend.", "Este é meu amigo."),
            ("The student has a blue bag.", "O aluno tem uma bolsa azul."),
        ],
    )

nivel5 = atualizar_nivel(5, "Corpo", "Partes do corpo, combinando com cores e objetos já aprendidos.")
if nivel5:
    atualizar_ou_criar_licao(
        nivel5,
        titulo="Corpo",
        tema="Vocabulário: partes do corpo — head, eye, ear, nose, mouth, hand, arm, leg, foot, hair",
        texto_gramatica=(
            "Partes do corpo: head (cabeça), eye (olho), ear (orelha), nose (nariz), mouth (boca), "
            "hand (mão), arm (braço), leg (perna), foot (pé), hair (cabelo). Você já pode combinar "
            "com cores: 'blue eyes' (olhos azuis), 'black hair' (cabelo preto)."
        ),
        erros_comuns=[
            "Confundir 'foot' (pé, singular) com 'feet' (pés, plural) — são formas irregulares.",
            "Trocar 'hair' (cabelo, sem plural em inglês) por 'hairs' — em inglês 'hair' já é tratado como um todo.",
            "Confundir 'mouth' com 'mouse' (rato/mouse de computador) — parecidas de ouvido.",
        ],
        exemplos=[
            ("She has blue eyes.", "Ela tem olhos azuis."),
            ("He has black hair.", "Ele tem cabelo preto."),
            ("My hand hurts.", "Minha mão dói."),
            ("Wash your hands.", "Lave suas mãos."),
        ],
    )

nivel6 = atualizar_nivel(6, "Família", "Membros da família e a primeira estrutura de frase: 'My + pessoa'.")
if nivel6:
    atualizar_ou_criar_licao(
        nivel6,
        titulo="Família",
        tema="Vocabulário: família — mother, father, brother, sister, son, daughter, husband, wife, "
        "grandmother, grandfather. Primeira estrutura: 'My mother.' / 'My father.'",
        texto_gramatica=(
            "Família: mother (mãe), father (pai), brother (irmão), sister (irmã), son (filho), "
            "daughter (filha), husband (marido), wife (esposa), grandmother (avó), grandfather (avô). "
            "Aqui começamos a primeira estrutura de frase de verdade: 'my' (meu/minha) + pessoa da "
            "família — 'My mother.', 'My father.', 'My sister.'"
        ),
        erros_comuns=[
            "Confundir 'brother' com 'bother' (incomodar) — muito parecidas de ouvido.",
            "Esquecer 'my' antes da pessoa: dizer só 'Mother' em vez de 'My mother' pra dizer 'minha mãe'.",
            "Trocar 'son' (filho) com 'sun' (sol) — mesma pronúncia, escrita diferente.",
        ],
        exemplos=[
            ("My mother.", "Minha mãe."),
            ("My father.", "Meu pai."),
            ("This is my sister.", "Esta é minha irmã."),
            ("My grandmother is 70 years old.", "Minha avó tem 70 anos."),
        ],
    )

nivel7 = atualizar_nivel(7, "Animais", "Vocabulário de animais, misturando com cores e números já aprendidos.")
if nivel7:
    atualizar_ou_criar_licao(
        nivel7,
        titulo="Animais",
        tema="Vocabulário: animais — dog, cat, bird, fish, horse, cow, chicken, elephant, lion, monkey",
        texto_gramatica=(
            "Animais: dog (cachorro), cat (gato), bird (pássaro), fish (peixe), horse (cavalo), cow "
            "(vaca), chicken (galinha), elephant (elefante), lion (leão), monkey (macaco). Agora "
            "misturamos tudo que já foi ensinado: 'a black dog' (um cachorro preto), 'three birds' "
            "(três pássaros)."
        ),
        erros_comuns=[
            "Confundir 'chicken' (galinha, o animal) com 'kitchen' (cozinha) — bem parecidas de ouvido.",
            "Usar 'fish' no plural com 's': o plural de 'fish' geralmente continua 'fish' (irregular).",
            "Trocar 'lion' com 'line' (linha) — soam parecido pra iniciante.",
        ],
        exemplos=[
            ("I have a black dog.", "Eu tenho um cachorro preto."),
            ("There are three birds in the tree.", "Tem três pássaros na árvore."),
            ("The cat is white.", "O gato é branco."),
            ("She has two horses.", "Ela tem dois cavalos."),
        ],
    )

nivel8 = atualizar_nivel(8, "Comida e Bebida", "Vocabulário de comida/bebida e a primeira frase com 'I like'.")
if nivel8:
    atualizar_ou_criar_licao(
        nivel8,
        titulo="Comida e Bebida",
        tema="Vocabulário: comida e bebida — water, milk, bread, rice, meat, chicken, apple, banana, "
        "coffee, juice. Primeira frase de gosto: 'I like apples.'",
        texto_gramatica=(
            "Comida e bebida: water (água), milk (leite), bread (pão), rice (arroz), meat (carne), "
            "chicken (frango — repara que é a mesma palavra do animal), apple (maçã), banana (banana), "
            "coffee (café), juice (suco). Aqui aparece a primeira frase de preferência: 'I like' + "
            "comida — 'I like apples.' (Eu gosto de maçãs). Ainda sem se aprofundar em gramática, só "
            "pra já usar de forma natural."
        ),
        erros_comuns=[
            "Esquecer o 's' no final da comida no plural depois de 'like': dizer 'I like apple' em "
            "vez de 'I like apples' quando fala de forma geral.",
            "Confundir 'bread' (pão) com 'bird' (pássaro) — parecidas de ouvido.",
            "Trocar 'juice' (suco) com 'juicy' (suculento) — parecidas mas com sentidos diferentes.",
        ],
        exemplos=[
            ("I like apples.", "Eu gosto de maçãs."),
            ("I drink coffee every morning.", "Eu bebo café toda manhã."),
            ("She likes bananas.", "Ela gosta de bananas."),
            ("Can I have some water?", "Posso beber um pouco de água?"),
        ],
    )

nivel9 = atualizar_nivel(9, "Lugares", "Vocabulário de lugares comuns e como combiná-los com pessoas e comida.")
if nivel9:
    atualizar_ou_criar_licao(
        nivel9,
        titulo="Lugares",
        tema="Vocabulário: lugares — house, school, work, hospital, supermarket, restaurant, park, "
        "bank, airport, store",
        texto_gramatica=(
            "Lugares do dia a dia: house (casa), school (escola), work (trabalho), hospital "
            "(hospital), supermarket (supermercado), restaurant (restaurante), park (parque), bank "
            "(banco), airport (aeroporto), store (loja). Combine com o que já sabe: 'school' + "
            "'student', 'restaurant' + comida."
        ),
        erros_comuns=[
            "Confundir 'house' (casa) com 'horse' (cavalo) — parecidas de ouvido pra iniciante.",
            "Esquecer o artigo antes do lugar quando necessário: 'I'm at the park' (não 'I'm at park').",
            "Trocar 'store' (loja) com 'story' (história) — parecidas em som.",
        ],
        exemplos=[
            ("I'm at the park.", "Eu estou no parque."),
            ("The student is at school.", "O aluno está na escola."),
            ("We eat at the restaurant.", "A gente come no restaurante."),
            ("My mother works at the hospital.", "Minha mãe trabalha no hospital."),
        ],
    )

nivel10 = atualizar_nivel(
    10, "Primeiras Frases", "Juntar tudo: objetos, cores, números, pessoas, corpo, família, animais, comida e lugares."
)
if nivel10:
    atualizar_ou_criar_licao(
        nivel10,
        titulo="Primeiras Frases",
        tema="Revisão geral: montar frases simples usando o vocabulário de todo o capítulo — "
        "'This is a book.', 'This is my mother.', 'I have a dog.', 'I like coffee.'",
        texto_gramatica=(
            "Agora você já sabe: objetos, cores, números, pessoas, corpo, família, animais, comida e "
            "lugares. Chegou a hora de juntar tudo em frases simples. As três estruturas principais "
            "que você já usou informalmente até aqui: 'This is a/my ___' (pra apresentar algo/alguém), "
            "'I have a ___' (pra dizer que você tem algo), e 'I like ___' (pra dizer que gosta de algo)."
        ),
        erros_comuns=[
            "Misturar 'this is' com 'I have': 'this is a dog' apresenta o cachorro, 'I have a dog' diz "
            "que ele é seu — são frases diferentes, não intercambiáveis.",
            "Esquecer o 'a' antes de objetos/animais no singular: 'this is book' em vez de 'this is a book'.",
            "Usar 'my' com 'this is' de forma redundante errada: o certo é 'this is my mother', não "
            "'this is a my mother'.",
        ],
        exemplos=[
            ("This is a book.", "Isto é um livro."),
            ("This is my mother.", "Esta é minha mãe."),
            ("I have a dog.", "Eu tenho um cachorro."),
            ("I like coffee.", "Eu gosto de café."),
        ],
    )

db.commit()
print("\nTrilha 1 reescrita com sucesso (Inglês do Zero: Objetos → Cores → Números → Pessoas → "
      "Corpo → Família → Animais → Comida e Bebida → Lugares → Primeiras Frases).")
print("Próximo acesso de cada usuário vai gerar flashcards/quiz/exercícios novos via Gemini, "
      "já com o conteúdo certo.")

db.close()