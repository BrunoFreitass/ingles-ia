from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# Tipos de exercício suportados, na ordem em que costumam ser introduzidos
# ao aluno (do reconhecimento simples até a produção livre). Mantido aqui
# (e não só documentado) pra servir de fonte única de verdade — usado tanto
# na geração via IA (prompts.py) quanto em validações futuras.
TIPOS_EXERCICIO = [
    "imagem_palavra",   # 🖼️ -> escolher a palavra certa entre 4 opções
    "palavra_imagem",   # palavra -> escolher a imagem (emoji) certa entre 4 opções
    "ligar",             # ligar cada palavra ao emoji correspondente (pares)
    "completar",         # frase com lacuna -> escolher a palavra que completa
    "organizar_frase",   # palavras embaralhadas -> montar a frase correta
    "escolha_multipla",  # pergunta com 4 alternativas (estilo quiz, mas isolado)
    "ouvir_escolher",    # ouve uma frase (TTS) -> escolhe a opção correspondente
    "interpretacao",     # texto curto + pergunta de compreensão
    "producao",          # produção livre (ex: "conte sobre sua rotina") — sem gabarito fixo
]


class Exercise(Base):
    """
    Um exercício de prática dentro de uma lição (capítulo). Cada lição tem
    até 10 exercícios, com tipos variados conforme a progressão de
    dificuldade da trilha (ver services/content_generation_service.py).

    `dados_json` guarda o payload PÚBLICO do exercício (o que o aluno vê:
    opções, frase com lacuna, palavras embaralhadas, texto pra ouvir/ler
    etc.) — nunca inclui a resposta certa. `resposta_correta_json` guarda o
    gabarito separado, só usado no momento da correção (mesmo padrão de
    esconder gabarito já usado em Quiz/QuizQuestion).
    """

    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    enunciado: Mapped[str | None] = mapped_column(Text, nullable=True)
    dados_json: Mapped[str] = mapped_column(Text, nullable=False)
    resposta_correta_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    lesson = relationship("Lesson", back_populates="exercicios")


class ExerciseAttempt(Base):
    """Registro de cada tentativa do usuário num exercício (prática, não gera nota de prova)."""

    __tablename__ = "exercise_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), nullable=False)
    resposta_dada_json: Mapped[str] = mapped_column(Text, nullable=False)
    acertou: Mapped[bool] = mapped_column(Boolean, nullable=False)
    data: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    exercise = relationship("Exercise")
