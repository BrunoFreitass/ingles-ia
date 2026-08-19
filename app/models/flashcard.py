from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Flashcard(Base):
    __tablename__ = "flashcards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    palavra: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    traducao: Mapped[str] = mapped_column(String(200), nullable=False)
    exemplo: Mapped[str | None] = mapped_column(Text, nullable=True)
    truque_memorizacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    nivel_id: Mapped[int | None] = mapped_column(ForeignKey("levels.id"), nullable=True)

    nivel = relationship("Level")


class UserFlashcardProgress(Base):
    """Progresso de repetição espaçada (estilo Anki) por usuário/flashcard."""

    __tablename__ = "user_flashcard_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    flashcard_id: Mapped[int] = mapped_column(ForeignKey("flashcards.id"), nullable=False)
    vezes_revisado: Mapped[int] = mapped_column(Integer, default=0)
    acertos: Mapped[int] = mapped_column(Integer, default=0)
    intervalo_dias: Mapped[int] = mapped_column(Integer, default=1)  # cresce a cada acerto
    ultima_revisao: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    proxima_revisao: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user = relationship("User")
    flashcard = relationship("Flashcard")
