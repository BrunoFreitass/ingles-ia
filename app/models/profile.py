from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserProfile(Base):
    """
    Perfil público de um usuário — 1 por usuário (relação 1:1 com User).
    Criado sob demanda na primeira vez que o usuário acessa/edita o perfil
    (mesmo padrão de "obter_ou_gerar" já usado pra flashcards/quiz/exercícios).
    """

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    foto_perfil_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    curso: Mapped[str | None] = mapped_column(String(120), nullable=True)
    idade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    signo: Mapped[str | None] = mapped_column(String(20), nullable=True)
    instagram_url: Mapped[str | None] = mapped_column(String(300), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(300), nullable=True)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User")
    fotos = relationship(
        "ProfilePhoto", back_populates="perfil", order_by="ProfilePhoto.ordem", cascade="all, delete-orphan"
    )


class ProfilePhoto(Base):
    """Uma das até 4 fotos adicionais do perfil (além da foto de perfil)."""

    __tablename__ = "profile_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("user_profiles.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    perfil = relationship("UserProfile", back_populates="fotos")
    comentarios = relationship(
        "PhotoComment", back_populates="foto", order_by="PhotoComment.criado_em", cascade="all, delete-orphan"
    )


class PhotoComment(Base):
    """Comentário de QUALQUER usuário logado numa foto de perfil (a de qualquer um, não só a própria)."""

    __tablename__ = "photo_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    photo_id: Mapped[int] = mapped_column(ForeignKey("profile_photos.id"), nullable=False)
    autor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    texto: Mapped[str] = mapped_column(String(500), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    foto = relationship("ProfilePhoto", back_populates="comentarios")
    autor = relationship("User")
