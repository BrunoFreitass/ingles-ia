from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), nullable=False, unique=True)

    lesson = relationship("Lesson")
    perguntas = relationship("QuizQuestion", back_populates="quiz")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"), nullable=False)
    pergunta: Mapped[str] = mapped_column(Text, nullable=False)
    opcoes_json: Mapped[str] = mapped_column(Text, nullable=False)  # lista JSON de opções
    resposta_correta: Mapped[str] = mapped_column(String(500), nullable=False)

    quiz = relationship("Quiz", back_populates="perguntas")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"), nullable=False)
    nota: Mapped[float] = mapped_column(Float, nullable=False)
    respostas_json: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    quiz = relationship("Quiz")
