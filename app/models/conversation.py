from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    lesson_id: Mapped[int | None] = mapped_column(ForeignKey("lessons.id"), nullable=True)
    tema: Mapped[str] = mapped_column(String(200), nullable=False)
    iniciado_em: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    lesson = relationship("Lesson")
    mensagens = relationship("ConversationMessage", back_populates="sessao")


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("conversation_sessions.id"), nullable=False)
    autor: Mapped[str] = mapped_column(String(20), nullable=False)  # "usuario" | "ia"
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    erro_corrigido: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    sessao = relationship("ConversationSession", back_populates="mensagens")


class ImmersionText(Base):
    """Motor de imersão: texto em PT-BR enviado pelo usuário, traduzido, com perguntas."""

    __tablename__ = "immersion_texts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    texto_pt: Mapped[str] = mapped_column(Text, nullable=False)
    texto_en: Mapped[str] = mapped_column(Text, nullable=False)
    perguntas_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
