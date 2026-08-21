import json
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


class ExercicioParaResponder(BaseModel):
    """Versão enviada ANTES do envio da resposta — sem o gabarito."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    ordem: int
    tipo: str
    enunciado: str | None
    dados: dict[str, Any]

    @model_validator(mode="before")
    @classmethod
    def _from_orm_model(cls, data):
        # O model ORM (Exercise) guarda o payload como dados_json (string).
        # Aqui convertemos pro formato que o schema expõe (dict), sem incluir
        # resposta_correta_json em nenhum momento.
        if hasattr(data, "dados_json"):
            return {
                "id": data.id,
                "ordem": data.ordem,
                "tipo": data.tipo,
                "enunciado": data.enunciado,
                "dados": json.loads(data.dados_json),
            }
        return data


class ExercicioSubmissao(BaseModel):
    resposta: Any  # formato varia por tipo: string, lista (organizar_frase) ou dict (ligar)


class ResultadoExercicio(BaseModel):
    exercicio_id: int
    acertou: bool
    resposta_correta: Any | None = None  # null pra exercícios de produção livre (sem gabarito fixo)
