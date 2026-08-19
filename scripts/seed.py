"""
Popula o banco com níveis e lições de exemplo, escritas à mão, para validar
o fluxo de ponta a ponta antes de plugar a geração por IA (Fase 3).

Uso:
    python scripts/seed.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.models.level import Lesson, LessonExample, Level  # noqa: E402

Base.metadata.create_all(bind=engine)

db = SessionLocal()

if db.query(Level).count() > 0:
    print("Já existem níveis no banco — nada foi inserido (rode só em banco vazio).")
    db.close()
    sys.exit(0)

# ---------------------------------------------------------------------------
# Nível 1 — Primeiros Passos
# ---------------------------------------------------------------------------
nivel_1 = Level(
    ordem=1,
    nome="Primeiros Passos",
    descricao="O básico para se apresentar e sobreviver numa conversa simples em inglês.",
    nota_minima_para_avancar=7.0,
)
db.add(nivel_1)
db.flush()

licao_1_1 = Lesson(
    level_id=nivel_1.id,
    titulo="Apresentações e Saudações",
    tema="Se apresentar e cumprimentar alguém",
    texto_gramatica=(
        "Em inglês, o verbo 'to be' (ser/estar) muda de forma conforme quem fala: "
        "I am, you are, he/she/it is, we are, they are. No dia a dia, quase sempre "
        "usamos a forma contraída: I'm, you're, he's, we're, they're. Para perguntar "
        "o nome de alguém, usamos 'What's your name?' (What is your name?), e para "
        "responder, 'My name is...' ou simplesmente 'I'm...'."
    ),
    erros_comuns_json=json.dumps(
        [
            "Esquecer o verbo 'to be': dizer 'I from Brazil' em vez de 'I'm from Brazil'.",
            "Confundir 'I'm' com 'I' sozinho em frases como 'I happy' — falta o 'am'.",
            "Traduzir 'Tudo bem?' ao pé da letra ('All well?') em vez de usar 'How are you?'.",
        ]
    ),
    ordem=1,
)
db.add(licao_1_1)
db.flush()

db.add_all(
    [
        LessonExample(lesson_id=licao_1_1.id, frase_en="Hi, I'm Bruno. What's your name?", frase_pt="Oi, eu sou o Bruno. Qual é o seu nome?"),
        LessonExample(lesson_id=licao_1_1.id, frase_en="Nice to meet you!", frase_pt="Prazer em te conhecer!"),
        LessonExample(lesson_id=licao_1_1.id, frase_en="How are you doing today?", frase_pt="Como você está hoje?"),
        LessonExample(lesson_id=licao_1_1.id, frase_en="I'm from Roraima, Brazil.", frase_pt="Eu sou de Roraima, Brasil."),
    ]
)

licao_1_2 = Lesson(
    level_id=nivel_1.id,
    titulo="No Café da Manhã",
    tema="Pedir comida e falar de hábitos simples",
    texto_gramatica=(
        "O Simple Present (presente simples) é usado para hábitos e rotinas. Na "
        "terceira pessoa do singular (he/she/it), o verbo ganha um 's' no final: "
        "'I drink coffee' mas 'She drinks coffee'. Para perguntas e negativas, usamos "
        "o auxiliar 'do'/'does': 'Do you drink coffee?', 'She doesn't drink coffee.'"
    ),
    erros_comuns_json=json.dumps(
        [
            "Esquecer o 's' na terceira pessoa: dizer 'She drink coffee' em vez de 'She drinks coffee'.",
            "Usar 'do' junto com o 's' por engano: 'She does drinks' em vez de 'She does drink' ou 'She drinks'.",
            "Traduzir 'Eu gosto de café' como 'I like of coffee' — em inglês não tem a preposição 'of' aqui.",
        ]
    ),
    ordem=2,
)
db.add(licao_1_2)
db.flush()

db.add_all(
    [
        LessonExample(lesson_id=licao_1_2.id, frase_en="I usually have coffee and bread for breakfast.", frase_pt="Eu geralmente tomo café e como pão no café da manhã."),
        LessonExample(lesson_id=licao_1_2.id, frase_en="Do you want some orange juice?", frase_pt="Você quer um pouco de suco de laranja?"),
        LessonExample(lesson_id=licao_1_2.id, frase_en="She doesn't eat eggs in the morning.", frase_pt="Ela não come ovos de manhã."),
    ]
)

# ---------------------------------------------------------------------------
# Nível 2 — Rotina do Dia a Dia
# ---------------------------------------------------------------------------
nivel_2 = Level(
    ordem=2,
    nome="Rotina do Dia a Dia",
    descricao="Fale sobre sua rotina, seu trabalho e o que fez ontem.",
    nota_minima_para_avancar=7.0,
)
db.add(nivel_2)
db.flush()

licao_2_1 = Lesson(
    level_id=nivel_2.id,
    titulo="Falando Sobre o Seu Dia",
    tema="Descrever o que você fez ontem (passado simples)",
    texto_gramatica=(
        "O Simple Past (passado simples) é usado para ações já concluídas. Verbos "
        "regulares recebem '-ed' no final: 'work' vira 'worked', 'study' vira 'studied'. "
        "Muitos verbos comuns são irregulares e mudam de forma completamente: 'go' vira "
        "'went', 'have' vira 'had'. Para perguntas e negativas, usamos 'did': "
        "'Did you work yesterday?', 'I didn't work yesterday.'"
    ),
    erros_comuns_json=json.dumps(
        [
            "Usar 'did' junto com o verbo no passado: 'I did went' em vez de 'I went' ou 'I did go'.",
            "Regularizar verbos irregulares: dizer 'goed' em vez de 'went'.",
            "Esquecer de mudar o verbo 'to be': dizer 'I was work' em vez de 'I worked' ou 'I was working'.",
        ]
    ),
    ordem=1,
)
db.add(licao_2_1)
db.flush()

db.add_all(
    [
        LessonExample(lesson_id=licao_2_1.id, frase_en="Yesterday I worked until 6pm.", frase_pt="Ontem eu trabalhei até as 18h."),
        LessonExample(lesson_id=licao_2_1.id, frase_en="I went to the gym after work.", frase_pt="Eu fui à academia depois do trabalho."),
        LessonExample(lesson_id=licao_2_1.id, frase_en="Did you have lunch already?", frase_pt="Você já almoçou?"),
        LessonExample(lesson_id=licao_2_1.id, frase_en="I didn't have time to study yesterday.", frase_pt="Eu não tive tempo de estudar ontem."),
    ]
)

db.commit()
db.close()

print("Seed concluído: 2 níveis, 3 lições e exemplos inseridos com sucesso.")
