from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.conversation import ConversationSession
from app.models.user import User
from app.schemas.conversation import ConversationMessageOut, ConversationSessionOut, MensagemEnviada
from app.services.auth_service import get_current_user
from app.services.conversation_service import enviar_mensagem, iniciar_sessao
from app.services.gemini_client import GeminiIndisponivelError
from app.services.progress_service import buscar_licao_com_acesso

router = APIRouter(prefix="/levels/{level_id}/lessons/{lesson_id}/conversation", tags=["conversa"])


def _buscar_sessao(db: Session, session_id: int, lesson_id: int, user_id: int) -> ConversationSession:
    sessao = (
        db.query(ConversationSession)
        .filter(
            ConversationSession.id == session_id,
            ConversationSession.lesson_id == lesson_id,
            ConversationSession.user_id == user_id,
        )
        .first()
    )
    if not sessao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sessão de conversa não encontrada.")
    return sessao


@router.post("/start", response_model=ConversationSessionOut, status_code=status.HTTP_201_CREATED)
def iniciar_conversa(
    level_id: int,
    lesson_id: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """Inicia uma nova sessão de conversa — a IA puxa assunto sozinha sobre o tema da lição."""
    licao = buscar_licao_com_acesso(db, usuario_atual, level_id, lesson_id)
    try:
        sessao = iniciar_sessao(db, usuario_atual, licao)
    except GeminiIndisponivelError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Não foi possível iniciar a conversa agora: {e}",
        ) from e

    sessao = (
        db.query(ConversationSession)
        .options(joinedload(ConversationSession.mensagens))
        .filter(ConversationSession.id == sessao.id)
        .first()
    )
    return sessao


@router.post("/{session_id}/message", response_model=ConversationMessageOut)
def enviar_mensagem_da_conversa(
    level_id: int,
    lesson_id: int,
    session_id: int,
    corpo: MensagemEnviada,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """
    Envia uma mensagem do aluno e retorna a resposta da IA (com possível
    correção de erro no campo erro_corrigido).
    """
    buscar_licao_com_acesso(db, usuario_atual, level_id, lesson_id)  # 404/403
    sessao = _buscar_sessao(db, session_id, lesson_id, usuario_atual.id)

    try:
        return enviar_mensagem(db, sessao, corpo.texto)
    except GeminiIndisponivelError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Não foi possível responder agora: {e}",
        ) from e