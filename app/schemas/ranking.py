from pydantic import BaseModel


class RankingItem(BaseModel):
    posicao: int
    user_id: int
    nome: str
    foto_perfil_url: str | None = None
    nivel_atual_ordem: int
    nivel_atual_nome: str
    nota_media: float
    total_tentativas: int
    total_erros: int
    eh_voce: bool = False