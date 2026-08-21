from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.conversation import ImmersionText
from app.models.user import User
from app.schemas.immersion import ImmersionTextIn, ImmersionTextListItem, ImmersionTextOut, ImmersionThemeIn
from app.services.auth_service import get_current_user
from app.services.gemini_client import GeminiIndisponivelError
from app.services.immersion_service import gerar_texto_por_tema, processar_texto

router = APIRouter(prefix="/immersion", tags=["motor de imersão"])


@router.post("/texts", response_model=ImmersionTextOut, status_code=status.HTTP_201_CREATED)
def enviar_texto(
    corpo: ImmersionTextIn,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """Recebe um texto em PT-BR, traduz pro inglês e gera perguntas de compreensão."""
    try:
        return processar_texto(db, usuario_atual, corpo.texto_pt)
    except GeminiIndisponivelError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Não foi possível processar o texto agora: {e}",
        ) from e


@router.post("/texts/generate", response_model=ImmersionTextOut, status_code=status.HTTP_201_CREATED)
def gerar_por_tema(
    corpo: ImmersionThemeIn,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """Gera um texto novo em português sobre o tema pedido, já traduzido e com perguntas."""
    try:
        return gerar_texto_por_tema(db, usuario_atual, corpo.tema)
    except GeminiIndisponivelError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Não foi possível gerar um texto sobre esse tema agora: {e}",
        ) from e


@router.get("/texts", response_model=list[ImmersionTextListItem])
def listar_textos(
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """Histórico de textos do usuário, mais recentes primeiro."""
    return (
        db.query(ImmersionText)
        .filter(ImmersionText.user_id == usuario_atual.id)
        .order_by(ImmersionText.criado_em.desc())
        .all()
    )


@router.get("/texts/{text_id}", response_model=ImmersionTextOut)
def obter_texto(
    text_id: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """Detalhe completo de um texto já processado (tradução + perguntas)."""
    registro = (
        db.query(ImmersionText)
        .filter(ImmersionText.id == text_id, ImmersionText.user_id == usuario_atual.id)
        .first()
    )
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Texto não encontrado.")
    return registro