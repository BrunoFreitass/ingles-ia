from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.flashcard import FlashcardOut
from app.services.auth_service import get_current_user
from app.services.content_generation_service import obter_ou_gerar_flashcards
from app.services.gemini_client import GeminiIndisponivelError
from app.services.progress_service import buscar_licao_com_acesso

router = APIRouter(prefix="/levels/{level_id}/lessons/{lesson_id}/flashcards", tags=["flashcards"])


@router.get("", response_model=list[FlashcardOut])
def obter_flashcards_da_licao(
    level_id: int,
    lesson_id: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """
    Retorna os flashcards do nível dessa lição. Na primeira chamada, gera
    via IA e salva no banco; nas próximas, reaproveita o que já existe
    (não gera de novo a cada visita).
    """
    licao = buscar_licao_com_acesso(db, usuario_atual, level_id, lesson_id)  # 404/403

    try:
        return obter_ou_gerar_flashcards(db, licao)
    except GeminiIndisponivelError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Não foi possível gerar os flashcards agora: {e}",
        ) from e