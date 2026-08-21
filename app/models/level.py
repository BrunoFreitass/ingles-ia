from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Capitulo(Base):
    """
    Agrupa 10 níveis + 1 prova final. Passar na prova final desbloqueia o
    próximo capítulo. Ex: Capítulo 1 = níveis 1-10 (o básico do dia a dia),
    Capítulo 2 = níveis 11-20, e assim por diante.
    """

    __tablename__ = "capitulos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ordem: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    nota_minima_prova_final: Mapped[float] = mapped_column(Float, default=7.0)

    niveis = relationship("Level", back_populates="capitulo", order_by="Level.ordem")


class Level(Base):
    __tablename__ = "levels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ordem: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    nota_minima_para_avancar: Mapped[float] = mapped_column(Float, default=7.0)
    capitulo_id: Mapped[int | None] = mapped_column(ForeignKey("capitulos.id"), nullable=True)

    lessons = relationship("Lesson", back_populates="level", order_by="Lesson.ordem")
    capitulo = relationship("Capitulo", back_populates="niveis")


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    level_id: Mapped[int] = mapped_column(ForeignKey("levels.id"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    tema: Mapped[str] = mapped_column(String(120), nullable=False)
    texto_gramatica: Mapped[str | None] = mapped_column(Text, nullable=True)
    erros_comuns_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # lista JSON com os 3 erros mais comuns
    audio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ordem: Mapped[int] = mapped_column(Integer, default=0)

    level = relationship("Level", back_populates="lessons")
    exemplos = relationship("LessonExample", back_populates="lesson")
    exercicios = relationship("Exercise", back_populates="lesson", order_by="Exercise.ordem")


class LessonExample(Base):
    __tablename__ = "lesson_examples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), nullable=False)
    frase_en: Mapped[str] = mapped_column(Text, nullable=False)
    frase_pt: Mapped[str] = mapped_column(Text, nullable=False)

    lesson = relationship("Lesson", back_populates="exemplos")