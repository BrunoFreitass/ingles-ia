"""
Orquestra a geração de flashcards e quiz via Gemini, com cache em banco:
se o conteúdo já foi gerado antes para essa lição/nível, reaproveita em vez
de chamar a IA de novo (economiza cota, evita gerar conteúdo diferente a
cada visita).
"""

import json

from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.models.flashcard import Flashcard
from app.models.level import Capitulo, Lesson, Level
from app.models.quiz import Quiz, QuizQuestion
from app.services.gemini_client import GeminiIndisponivelError, gemini_client
from app.services.prompts import prompt_exercicios, prompt_flashcards, prompt_prova_final, prompt_quiz

# Progressão de variedade de tipos de exercício por trilha (Capitulo.ordem).
# Trilhas iniciais só usam reconhecimento simples; a variedade cresce junto
# com a dificuldade do conteúdo, terminando em produção livre nas trilhas
# avançadas. Trilhas além da 10 reaproveitam a última faixa.
_FAIXAS_TIPOS_POR_TRILHA: list[tuple[int, list[str], str]] = [
    (2, ["imagem_palavra", "palavra_imagem", "ligar", "completar"], "iniciante absoluto (nível infantil)"),
    (4, ["imagem_palavra", "palavra_imagem", "ligar", "completar", "organizar_frase", "escolha_multipla"], "básico"),
    (6, ["completar", "organizar_frase", "escolha_multipla", "ouvir_escolher"], "básico-intermediário"),
    (8, ["organizar_frase", "escolha_multipla", "ouvir_escolher", "interpretacao"], "intermediário"),
    (10, ["escolha_multipla", "ouvir_escolher", "interpretacao", "producao"], "avançado"),
]


def _tipos_e_dificuldade_para_trilha(ordem_trilha: int) -> tuple[list[str], str]:
    for limite, tipos, dificuldade in _FAIXAS_TIPOS_POR_TRILHA:
        if ordem_trilha <= limite:
            return tipos, dificuldade
    return _FAIXAS_TIPOS_POR_TRILHA[-1][1], _FAIXAS_TIPOS_POR_TRILHA[-1][2]


def _vocabulario_reforco(db: Session, lesson: Lesson) -> list[str]:
    """
    Palavras de flashcards de níveis ANTERIORES (ordem menor) dentro do
    mesmo capítulo, pra reforçar vocabulário já ensinado. Se o nível ainda
    não tem capítulo definido (dado legado), não reforça nada.
    """
    nivel = lesson.level
    if not nivel or not nivel.capitulo_id:
        return []

    niveis_anteriores = (
        db.query(Level)
        .filter(Level.capitulo_id == nivel.capitulo_id, Level.ordem < nivel.ordem)
        .all()
    )
    if not niveis_anteriores:
        return []

    ids_niveis_anteriores = [n.id for n in niveis_anteriores]
    palavras = (
        db.query(Flashcard.palavra)
        .filter(Flashcard.nivel_id.in_(ids_niveis_anteriores))
        .all()
    )
    return [p[0] for p in palavras]


def obter_ou_gerar_flashcards(db: Session, lesson: Lesson) -> list[Flashcard]:
    """Retorna os flashcards do nível dessa lição, gerando via IA na primeira vez."""
    existentes = db.query(Flashcard).filter(Flashcard.nivel_id == lesson.level_id).all()
    if existentes:
        return existentes

    dados = gemini_client.generate_json(prompt_flashcards(lesson))
    flashcards_gerados = dados.get("flashcards", [])

    if not flashcards_gerados:
        raise GeminiIndisponivelError("O Gemini respondeu sem gerar nenhum flashcard.")

    novos = [
        Flashcard(
            palavra=item["palavra"],
            traducao=item["traducao"],
            exemplo=item.get("exemplo"),
            truque_memorizacao=item.get("truque_memorizacao"),
            nivel_id=lesson.level_id,
        )
        for item in flashcards_gerados
    ]
    db.add_all(novos)
    db.commit()
    for f in novos:
        db.refresh(f)
    return novos


def obter_ou_gerar_quiz(db: Session, lesson: Lesson) -> Quiz:
    """Retorna o quiz dessa lição, gerando via IA na primeira vez."""
    existente = db.query(Quiz).filter(Quiz.lesson_id == lesson.id).first()
    if existente:
        return existente

    dados = gemini_client.generate_json(prompt_quiz(lesson))
    perguntas_geradas = dados.get("perguntas", [])

    if len(perguntas_geradas) < 5:
        # Aceita alguma variação (a IA às vezes gera 8-9), mas rejeita se vier
        # muito abaixo do esperado — sinal de resposta malformada/incompleta.
        raise GeminiIndisponivelError(
            f"O Gemini gerou apenas {len(perguntas_geradas)} perguntas (esperado ~10)."
        )

    quiz = Quiz(lesson_id=lesson.id)
    db.add(quiz)
    db.flush()  # garante quiz.id sem precisar commitar ainda

    for item in perguntas_geradas:
        db.add(
            QuizQuestion(
                quiz_id=quiz.id,
                pergunta=item["pergunta"],
                opcoes_json=json.dumps(item["opcoes"], ensure_ascii=False),
                resposta_correta=item["resposta_correta"],
            )
        )

    db.commit()
    db.refresh(quiz)
    return quiz


def obter_ou_gerar_exercicios(db: Session, lesson: Lesson) -> list[Exercise]:
    """
    Retorna os exercícios de prática da lição, gerando via IA na primeira
    vez. A variedade de tipos e a dificuldade dependem da trilha (Capitulo)
    em que a lição está; vocabulário de níveis anteriores da mesma trilha é
    passado pra IA reforçar quando fizer sentido.
    """
    existentes = (
        db.query(Exercise).filter(Exercise.lesson_id == lesson.id).order_by(Exercise.ordem).all()
    )
    if existentes:
        return existentes

    nivel = lesson.level
    ordem_trilha = nivel.capitulo.ordem if nivel and nivel.capitulo else 1
    tipos_permitidos, dificuldade = _tipos_e_dificuldade_para_trilha(ordem_trilha)
    vocabulario_reforco = _vocabulario_reforco(db, lesson)

    dados = gemini_client.generate_json(
        prompt_exercicios(lesson, tipos_permitidos, vocabulario_reforco, dificuldade)
    )
    exercicios_gerados = dados.get("exercicios", [])

    if len(exercicios_gerados) < 8:
        raise GeminiIndisponivelError(
            f"O Gemini gerou apenas {len(exercicios_gerados)} exercícios (esperado ~10)."
        )

    novos = [
        Exercise(
            lesson_id=lesson.id,
            ordem=indice + 1,
            tipo=item["tipo"],
            enunciado=item.get("enunciado"),
            dados_json=json.dumps(item["dados"], ensure_ascii=False),
            resposta_correta_json=json.dumps(item.get("resposta_correta"), ensure_ascii=False),
        )
        for indice, item in enumerate(exercicios_gerados)
    ]
    db.add_all(novos)
    db.commit()
    for e in novos:
        db.refresh(e)
    return novos


def obter_ou_gerar_prova_final(db: Session, capitulo: Capitulo) -> Quiz:
    """Retorna a prova final do capítulo, gerando via IA na primeira vez (15 perguntas)."""
    existente = db.query(Quiz).filter(Quiz.capitulo_id == capitulo.id).first()
    if existente:
        return existente

    niveis = db.query(Level).filter(Level.capitulo_id == capitulo.id).order_by(Level.ordem).all()
    licoes = [licao for nivel in niveis for licao in nivel.lessons]

    if not licoes:
        raise GeminiIndisponivelError("Este capítulo ainda não tem lições com conteúdo pra revisar.")

    dados = gemini_client.generate_json(prompt_prova_final(capitulo, licoes))
    perguntas_geradas = dados.get("perguntas", [])

    if len(perguntas_geradas) < 8:
        raise GeminiIndisponivelError(
            f"O Gemini gerou apenas {len(perguntas_geradas)} perguntas pra prova final (esperado ~15)."
        )

    quiz = Quiz(capitulo_id=capitulo.id)
    db.add(quiz)
    db.flush()

    for item in perguntas_geradas:
        db.add(
            QuizQuestion(
                quiz_id=quiz.id,
                pergunta=item["pergunta"],
                opcoes_json=json.dumps(item["opcoes"], ensure_ascii=False),
                resposta_correta=item["resposta_correta"],
            )
        )

    db.commit()
    db.refresh(quiz)
    return quiz