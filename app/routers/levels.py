from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.level import Lesson, Level
from app.models.user import User
from app.schemas.level import LessonOut, LevelListItem
from app.services.auth_service import get_current_user
from app.services.progress_service import (
    buscar_licao_com_acesso,
    nivel_esta_completo,
    ordem_do_nivel_do_usuario,
)

router = APIRouter(prefix="/levels", tags=["níveis e lições"])


def _serializar_nivel(db: Session, user: User, nivel: Level) -> LevelListItem:
    ordem_usuario = ordem_do_nivel_do_usuario(db, user)
    item = LevelListItem.model_validate(nivel)
    item.liberado = nivel.ordem <= ordem_usuario
    # Só vale a pena calcular "concluido" pra níveis liberados — os
    # bloqueados nunca têm quiz feito, seria sempre False mesmo.
    item.concluido = item.liberado and nivel_esta_completo(db, user, nivel)
    return item


@router.get("", response_model=list[LevelListItem])
def listar_niveis(
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """Lista todos os níveis, com liberado/concluido calculados pra esse usuário."""
    niveis = (
        db.query(Level)
        .options(joinedload(Level.lessons))
        .order_by(Level.ordem)
        .all()
    )
    return [_serializar_nivel(db, usuario_atual, nivel) for nivel in niveis]


@router.get("/{level_id}", response_model=LevelListItem)
def obter_nivel(
    level_id: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """Detalhe de um nível específico, com suas lições resumidas."""
    nivel = (
        db.query(Level)
        .options(joinedload(Level.lessons))
        .filter(Level.id == level_id)
        .first()
    )
    if not nivel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nível não encontrado.")
    return _serializar_nivel(db, usuario_atual, nivel)


@router.get("/{level_id}/lessons/{lesson_id}", response_model=LessonOut)
def obter_licao(
    level_id: int,
    lesson_id: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """Detalhe completo de uma lição: gramática, erros comuns e exemplos."""
    buscar_licao_com_acesso(db, usuario_atual, level_id, lesson_id)  # 403 se nível bloqueado

    licao = (
        db.query(Lesson)
        .options(joinedload(Lesson.exemplos))
        .filter(Lesson.id == lesson_id, Lesson.level_id == level_id)
        .first()
    )
    # Personaliza o conteúdo com o primeiro nome de quem está logado (ex:
    # frases de exemplo tipo "Hi, I'm {nome}" usam o placeholder '{nome}').
    return LessonOut.from_orm_model(licao, usuario_atual.nome)