"""
Orquestra a geração de flashcards e quiz via Gemini, com cache em banco:
se o conteúdo já foi gerado antes para essa lição/nível, reaproveita em vez
de chamar a IA de novo (economiza cota, evita gerar conteúdo diferente a
cada visita).
"""

import json

from sqlalchemy.orm import Session

from app.models.flashcard import Flashcard
from app.models.level import Lesson
from app.models.quiz import Quiz, QuizQuestion
from app.services.gemini_client import GeminiIndisponivelError, gemini_client
from app.services.prompts import prompt_flashcards, prompt_quiz


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
