from pydantic import BaseModel, ConfigDict, Field


class ConversationMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    autor: str  # "usuario" | "ia"
    texto: str
    erro_corrigido: str | None


class ConversationSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lesson_id: int | None
    tema: str
    mensagens: list[ConversationMessageOut] = []


class MensagemEnviada(BaseModel):
    texto: str = Field(min_length=1, max_length=1000)
