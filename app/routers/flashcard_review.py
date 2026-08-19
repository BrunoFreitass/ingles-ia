from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.flashcard import Flashcard
from app.models.user import User
from app.schemas.flashcard import FlashcardOut, FlashcardProgressOut, FlashcardReviewIn
from app.services.auth_service import get_current_user
from app.services.spaced_repetition_service import buscar_fila_revisao, revisar_flashcard

router = APIRouter(prefix="/flashcards", tags=["revisão de flashcards"])


@router.get("/review", response_model=list[FlashcardOut])
def obter_fila_de_revisao(
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """
    Fila de revisão do dia: cartões vencidos (hora de revisar de novo) +
    cartões novos que o usuário ainda não viu, misturados.
    """
    return buscar_fila_revisao(db, usuario_atual)


@router.post("/{flashcard_id}/review", response_model=FlashcardProgressOut)
def enviar_revisao(
    flashcard_id: int,
    corpo: FlashcardReviewIn,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """Registra se o usuário acertou ou errou o cartão, recalculando o próximo intervalo."""
    existe = db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
    if not existe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard não encontrado.")

    progresso = revisar_flashcard(db, usuario_atual, flashcard_id, corpo.acertou)
    return progresso
