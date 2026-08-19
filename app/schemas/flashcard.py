from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FlashcardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    palavra: str
    traducao: str
    exemplo: str | None
    truque_memorizacao: str | None


class FlashcardReviewIn(BaseModel):
    acertou: bool


class FlashcardProgressOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    flashcard_id: int
    vezes_revisado: int
    acertos: int
    intervalo_dias: int
    proxima_revisao: datetime | None
