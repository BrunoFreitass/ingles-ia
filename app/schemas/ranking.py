from pydantic import BaseModel


class RankingItem(BaseModel):
    posicao: int
    nome: str
    nivel_atual_ordem: int
    nivel_atual_nome: str
    nota_media: float
    total_tentativas: int
    total_erros: int
    eh_voce: bool = False
