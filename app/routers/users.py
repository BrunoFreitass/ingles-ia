from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.user import UserOut
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/users", tags=["usuários"])


@router.get("/me", response_model=UserOut)
def perfil(usuario_atual: User = Depends(get_current_user)):
    """
    Endpoint de exemplo protegido — qualquer rota futura (níveis, lições,
    flashcards, quiz, conversa) segue esse mesmo padrão de Depends(get_current_user).
    """
    return usuario_atual
