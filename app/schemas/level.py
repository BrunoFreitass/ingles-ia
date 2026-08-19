import json

from pydantic import BaseModel, ConfigDict, field_validator


class LessonExampleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    frase_en: str
    frase_pt: str


class LessonListItem(BaseModel):
    """Versão resumida — usada quando a lição aparece dentro da lista de um nível."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    tema: str
    ordem: int


class LessonOut(BaseModel):
    """Versão completa — usada no detalhe de uma lição específica."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    level_id: int
    titulo: str
    tema: str
    texto_gramatica: str | None
    erros_comuns: list[str] = []
    audio_url: str | None
    ordem: int
    exemplos: list[LessonExampleOut] = []

    @field_validator("erros_comuns", mode="before")
    @classmethod
    def _parse_erros_comuns(cls, v):
        # erros_comuns_json vem do banco como uma string JSON; convertemos pra lista aqui
        if v is None:
            return []
        if isinstance(v, str):
            return json.loads(v)
        return v

    @classmethod
    def from_orm_model(cls, lesson):
        """Monta o schema a partir do model, mapeando erros_comuns_json -> erros_comuns."""
        return cls(
            id=lesson.id,
            level_id=lesson.level_id,
            titulo=lesson.titulo,
            tema=lesson.tema,
            texto_gramatica=lesson.texto_gramatica,
            erros_comuns=lesson.erros_comuns_json,
            audio_url=lesson.audio_url,
            ordem=lesson.ordem,
            exemplos=[LessonExampleOut.model_validate(e) for e in lesson.exemplos],
        )


class LevelListItem(BaseModel):
    """Nível na listagem geral — sem o conteúdo completo das lições."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    ordem: int
    nome: str
    descricao: str | None
    nota_minima_para_avancar: float
    lessons: list[LessonListItem] = []
    liberado: bool = True
    concluido: bool = False
