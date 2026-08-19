"""
Repetição espaçada simplificada (estilo Leitner/Anki): a cada acerto, o
intervalo até a próxima revisão dobra (1 → 2 → 4 → 8... dias, até um teto);
a cada erro, volta pro intervalo mínimo (1 dia). Não é o algoritmo SM-2
completo (sem "fator de facilidade" por cartão), mas captura a ideia central
— cartões que você já sabe bem aparecem cada vez mais espaçados, cartões que
você erra voltam a aparecer logo.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.flashcard import Flashcard, UserFlashcardProgress
from app.models.user import User

INTERVALO_INICIAL_DIAS = 1
FATOR_CRESCIMENTO = 2
INTERVALO_MAXIMO_DIAS = 60


def buscar_fila_revisao(db: Session, user: User, limite: int = 20) -> list[Flashcard]:
    """
    Monta a fila de revisão: cartões já vistos que estão vencidos (proxima_revisao
    no passado) + cartões novos (o usuário nunca revisou) que existem no sistema,
    até o limite pedido. Vencidos vêm primeiro.
    """
    agora = datetime.now(timezone.utc)

    vencidos = (
        db.query(Flashcard)
        .join(
            UserFlashcardProgress,
            and_(
                UserFlashcardProgress.flashcard_id == Flashcard.id,
                UserFlashcardProgress.user_id == user.id,
            ),
        )
        .filter(UserFlashcardProgress.proxima_revisao <= agora)
        .limit(limite)
        .all()
    )

    if len(vencidos) >= limite:
        return vencidos

    ids_ja_revisados = db.query(UserFlashcardProgress.flashcard_id).filter(
        UserFlashcardProgress.user_id == user.id
    )
    novos = (
        db.query(Flashcard)
        .filter(~Flashcard.id.in_(ids_ja_revisados))
        .limit(limite - len(vencidos))
        .all()
    )

    return vencidos + novos


def revisar_flashcard(db: Session, user: User, flashcard_id: int, acertou: bool) -> UserFlashcardProgress:
    """Registra o resultado da revisão e recalcula o próximo intervalo."""
    progresso = (
        db.query(UserFlashcardProgress)
        .filter(
            UserFlashcardProgress.user_id == user.id,
            UserFlashcardProgress.flashcard_id == flashcard_id,
        )
        .first()
    )

    if not progresso:
        progresso = UserFlashcardProgress(
            user_id=user.id, flashcard_id=flashcard_id, vezes_revisado=0, acertos=0, intervalo_dias=INTERVALO_INICIAL_DIAS
        )
        db.add(progresso)

    agora = datetime.now(timezone.utc)
    progresso.vezes_revisado += 1

    if acertou:
        progresso.acertos += 1
        progresso.intervalo_dias = min(
            INTERVALO_MAXIMO_DIAS, max(INTERVALO_INICIAL_DIAS, progresso.intervalo_dias * FATOR_CRESCIMENTO)
        )
    else:
        progresso.intervalo_dias = INTERVALO_INICIAL_DIAS

    progresso.ultima_revisao = agora
    progresso.proxima_revisao = agora + timedelta(days=progresso.intervalo_dias)

    db.commit()
    db.refresh(progresso)
    return progresso
