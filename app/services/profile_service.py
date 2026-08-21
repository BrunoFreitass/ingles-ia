"""
Perfil público de usuário — estilo rede social simples: bio, curso, idade,
signo, links, foto de perfil e até 4 fotos adicionais que QUALQUER usuário
logado pode comentar (não só o dono do perfil).
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.level import Level
from app.models.profile import PhotoComment, ProfilePhoto, UserProfile
from app.models.user import User
from app.schemas.profile import PerfilOut, PerfilUpdate
from app.services.image_url_service import resolver_url_imagem
from app.services.progress_service import ordem_do_nivel_do_usuario

MAX_FOTOS_ADICIONAIS = 4


def obter_ou_criar_perfil(db: Session, user: User) -> UserProfile:
    """Cria um perfil vazio na primeira vez que o usuário mexe nele (visualiza ou edita)."""
    perfil = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if perfil:
        return perfil

    perfil = UserProfile(user_id=user.id)
    db.add(perfil)
    db.commit()
    db.refresh(perfil)
    return perfil


def montar_perfil_out(db: Session, perfil: UserProfile, dono: User) -> PerfilOut:
    """Monta a versão pública do perfil, incluindo o nível atual do dono na trilha."""
    ordem_nivel = ordem_do_nivel_do_usuario(db, dono)
    nivel = db.query(Level).filter(Level.ordem == ordem_nivel).first()

    return PerfilOut(
        user_id=dono.id,
        nome=dono.nome,
        foto_perfil_url=perfil.foto_perfil_url,
        bio=perfil.bio,
        curso=perfil.curso,
        idade=perfil.idade,
        signo=perfil.signo,
        instagram_url=perfil.instagram_url,
        linkedin_url=perfil.linkedin_url,
        fotos=perfil.fotos,
        nivel_atual_ordem=ordem_nivel,
        nivel_atual_nome=nivel.nome if nivel else "—",
    )


def atualizar_perfil(db: Session, perfil: UserProfile, dados: PerfilUpdate) -> UserProfile:
    """Atualização parcial — só sobrescreve os campos que vieram preenchidos na requisição."""
    campos = dados.model_dump(exclude_unset=True)
    if "foto_perfil_url" in campos and campos["foto_perfil_url"]:
        campos["foto_perfil_url"] = resolver_url_imagem(campos["foto_perfil_url"])
    for campo, valor in campos.items():
        setattr(perfil, campo, valor)
    db.commit()
    db.refresh(perfil)
    return perfil


def adicionar_foto(db: Session, perfil: UserProfile, url: str) -> ProfilePhoto:
    if len(perfil.fotos) >= MAX_FOTOS_ADICIONAIS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Você já tem {MAX_FOTOS_ADICIONAIS} fotos — remova uma antes de adicionar outra.",
        )

    url_resolvida = resolver_url_imagem(url)
    proxima_ordem = max((f.ordem for f in perfil.fotos), default=-1) + 1
    foto = ProfilePhoto(profile_id=perfil.id, url=url_resolvida, ordem=proxima_ordem)
    db.add(foto)
    db.commit()
    db.refresh(foto)
    return foto


def remover_foto(db: Session, perfil: UserProfile, foto_id: int) -> None:
    foto = db.query(ProfilePhoto).filter(ProfilePhoto.id == foto_id, ProfilePhoto.profile_id == perfil.id).first()
    if not foto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto não encontrada.")
    db.delete(foto)
    db.commit()


def adicionar_comentario(db: Session, foto: ProfilePhoto, autor: User, texto: str) -> PhotoComment:
    comentario = PhotoComment(photo_id=foto.id, autor_id=autor.id, texto=texto)
    db.add(comentario)
    db.commit()
    db.refresh(comentario)
    return comentario


def remover_comentario(db: Session, comentario_id: int, usuario_atual: User) -> None:
    """Só o autor do comentário pode apagar — não é moderação do dono da foto, é autoral."""
    comentario = db.query(PhotoComment).filter(PhotoComment.id == comentario_id).first()
    if not comentario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comentário não encontrado.")
    if comentario.autor_id != usuario_atual.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Você só pode apagar os seus próprios comentários."
        )
    db.delete(comentario)
    db.commit()
