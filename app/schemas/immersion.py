import json
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ImmersionQuestion(BaseModel):
    pergunta: str
    resposta: str


class ImmersionTextIn(BaseModel):
    texto_pt: str = Field(min_length=10, max_length=3000)


class ImmersionThemeIn(BaseModel):
    tema: str = Field(min_length=2, max_length=200)


class ImmersionTextOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    texto_pt: str
    texto_en: str
    perguntas: list[ImmersionQuestion]
    criado_em: datetime

    @model_validator(mode="before")
    @classmethod
    def _from_orm_model(cls, data):
        # O model ORM guarda as perguntas como perguntas_json (string) — convertemos aqui.
        if hasattr(data, "perguntas_json"):
            return {
                "id": data.id,
                "texto_pt": data.texto_pt,
                "texto_en": data.texto_en,
                "perguntas": json.loads(data.perguntas_json) if data.perguntas_json else [],
                "criado_em": data.criado_em,
            }
        return data


class ImmersionTextListItem(BaseModel):
    """Versão resumida — usada na listagem do histórico."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    texto_pt: str
    criado_em: datetime