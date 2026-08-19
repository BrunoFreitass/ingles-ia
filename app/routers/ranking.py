from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.ranking import RankingItem
from app.services.auth_service import get_current_user
from app.services.ranking_service import calcular_ranking

router = APIRouter(prefix="/ranking", tags=["ranking"])


@router.get("", response_model=list[RankingItem])
def obter_ranking(
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """Ranking competitivo entre todos os usuários — nível, nota média e erros."""
    return calcular_ranking(db, usuario_atual)
