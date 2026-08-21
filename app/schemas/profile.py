from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SIGNOS_VALIDOS = [
    "Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem",
    "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes",
]


class ComentarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    autor_id: int
    autor_nome: str
    texto: str
    criado_em: datetime

    @model_validator(mode="before")
    @classmethod
    def _from_orm_model(cls, data):
        # O model ORM (PhotoComment) não tem "autor_nome" direto — vem de autor.nome.
        if hasattr(data, "autor_id") and not isinstance(data, dict):
            return {
                "id": data.id,
                "autor_id": data.autor_id,
                "autor_nome": data.autor.nome,
                "texto": data.texto,
                "criado_em": data.criado_em,
            }
        return data

    @classmethod
    def from_orm_model(cls, comentario):
        return cls(
            id=comentario.id,
            autor_id=comentario.autor_id,
            autor_nome=comentario.autor.nome,
            texto=comentario.texto,
            criado_em=comentario.criado_em,
        )


class ComentarioCreate(BaseModel):
    texto: str = Field(min_length=1, max_length=500)


class FotoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    ordem: int
    comentarios: list[ComentarioOut] = []


class FotoCreate(BaseModel):
    url: str = Field(min_length=1, max_length=500)


class PerfilOut(BaseModel):
    """Versão pública — o que qualquer usuário logado vê ao visitar o perfil de alguém."""

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    nome: str
    foto_perfil_url: str | None
    bio: str | None
    curso: str | None
    idade: int | None
    signo: str | None
    instagram_url: str | None
    linkedin_url: str | None
    fotos: list[FotoOut] = []
    nivel_atual_ordem: int
    nivel_atual_nome: str


class PerfilUpdate(BaseModel):
    """Campos editáveis pelo próprio dono do perfil — todos opcionais (edição parcial)."""

    foto_perfil_url: str | None = Field(default=None, max_length=500)
    bio: str | None = Field(default=None, max_length=1000)
    curso: str | None = Field(default=None, max_length=120)
    idade: int | None = Field(default=None, ge=13, le=120)
    signo: str | None = None
    instagram_url: str | None = Field(default=None, max_length=300)
    linkedin_url: str | None = Field(default=None, max_length=300)

    @field_validator("signo")
    @classmethod
    def _validar_signo(cls, v):
        if v in (None, ""):
            return None
        if v not in SIGNOS_VALIDOS:
            raise ValueError(f"Signo inválido. Use um destes: {', '.join(SIGNOS_VALIDOS)}.")
        return v
