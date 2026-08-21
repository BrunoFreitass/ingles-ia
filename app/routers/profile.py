from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.profile import PhotoComment, ProfilePhoto, UserProfile
from app.models.user import User
from app.schemas.profile import ComentarioCreate, ComentarioOut, FotoCreate, FotoOut, PerfilOut, PerfilUpdate
from app.services.auth_service import get_current_user
from app.services.profile_service import (
    adicionar_comentario,
    adicionar_foto,
    atualizar_perfil,
    montar_perfil_out,
    obter_ou_criar_perfil,
    remover_comentario,
    remover_foto,
)

router = APIRouter(tags=["perfil"])


def _buscar_usuario(db: Session, user_id: int) -> User:
    usuario = db.query(User).filter(User.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return usuario


# IMPORTANTE: as rotas fixas "/users/me/..." precisam vir ANTES de
# "/users/{user_id}/profile" neste arquivo. O FastAPI/Starlette casa rotas
# na ordem em que foram registradas — se a rota com parâmetro vier primeiro,
# ela captura "me" como se fosse um user_id (e quebra tentando converter
# "me" pra inteiro, com 422).


@router.get("/users/me/profile", response_model=PerfilOut)
def obter_meu_perfil(
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """Atalho pro próprio perfil — equivalente a GET /users/{seu_id}/profile."""
    perfil = obter_ou_criar_perfil(db, usuario_atual)
    return montar_perfil_out(db, perfil, usuario_atual)


@router.put("/users/me/profile", response_model=PerfilOut)
def editar_meu_perfil(
    dados: PerfilUpdate,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """Atualização parcial do próprio perfil — só os campos enviados são alterados."""
    perfil = obter_ou_criar_perfil(db, usuario_atual)
    perfil = atualizar_perfil(db, perfil, dados)
    return montar_perfil_out(db, perfil, usuario_atual)


@router.post("/users/me/profile/fotos", response_model=FotoOut, status_code=status.HTTP_201_CREATED)
def adicionar_foto_do_perfil(
    dados: FotoCreate,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """Adiciona uma foto ao próprio perfil (máximo 4, além da foto de perfil)."""
    perfil = obter_ou_criar_perfil(db, usuario_atual)
    return adicionar_foto(db, perfil, dados.url)


@router.delete("/users/me/profile/fotos/{foto_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_foto_do_perfil(
    foto_id: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """Remove uma foto do próprio perfil (e os comentários dela, em cascata)."""
    perfil = obter_ou_criar_perfil(db, usuario_atual)
    remover_foto(db, perfil, foto_id)


@router.post("/fotos/{foto_id}/comentarios", response_model=ComentarioOut, status_code=status.HTTP_201_CREATED)
def comentar_foto(
    foto_id: int,
    dados: ComentarioCreate,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """Comenta numa foto — de QUALQUER perfil, não só do próprio usuário."""
    foto = db.query(ProfilePhoto).filter(ProfilePhoto.id == foto_id).first()
    if not foto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto não encontrada.")

    comentario = adicionar_comentario(db, foto, usuario_atual, dados.texto)
    return ComentarioOut.from_orm_model(comentario)


@router.delete("/fotos/comentarios/{comentario_id}", status_code=status.HTTP_204_NO_CONTENT)
def apagar_comentario(
    comentario_id: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """Apaga um comentário — só quem escreveu pode apagar."""
    remover_comentario(db, comentario_id, usuario_atual)


@router.get("/users/{user_id}/profile", response_model=PerfilOut)
def obter_perfil(
    user_id: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """Perfil público de qualquer usuário — visível por qualquer um que esteja logado."""
    dono = _buscar_usuario(db, user_id)
    perfil = obter_ou_criar_perfil(db, dono)
    return montar_perfil_out(db, perfil, dono)
