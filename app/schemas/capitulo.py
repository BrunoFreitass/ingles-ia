from pydantic import BaseModel, ConfigDict

from app.schemas.level import LessonListItem


class NivelResumoNoCapitulo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ordem: int
    nome: str
    descricao: str | None
    liberado: bool = True
    concluido: bool = False
    lessons: list[LessonListItem] = []


class CapituloListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ordem: int
    nome: str
    descricao: str | None
    liberado: bool = True
    concluido: bool = False
    prova_final_disponivel: bool = False
    prova_final_aprovada: bool = False
    niveis: list[NivelResumoNoCapitulo] = []