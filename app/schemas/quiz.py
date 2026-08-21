import json

from pydantic import BaseModel, ConfigDict, model_validator


class QuizQuestionParaResponder(BaseModel):
    """Versão enviada ANTES do envio das respostas — sem o gabarito."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    pergunta: str
    opcoes: list[str]

    @model_validator(mode="before")
    @classmethod
    def _from_orm_model(cls, data):
        # O model ORM (QuizQuestion) guarda as opções como opcoes_json (string).
        # Aqui convertemos pro formato que o schema espera (lista de strings).
        if hasattr(data, "opcoes_json"):
            return {
                "id": data.id,
                "pergunta": data.pergunta,
                "opcoes": json.loads(data.opcoes_json),
            }
        return data


class QuizParaResponder(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lesson_id: int | None = None
    capitulo_id: int | None = None
    perguntas: list[QuizQuestionParaResponder]


class RespostaSubmetida(BaseModel):
    pergunta_id: int
    resposta_selecionada: str


class QuizSubmissao(BaseModel):
    respostas: list[RespostaSubmetida]


class CorrecaoPergunta(BaseModel):
    """Uma pergunta já corrigida — aqui sim o gabarito aparece."""

    pergunta_id: int
    pergunta: str
    resposta_selecionada: str
    resposta_correta: str
    acertou: bool


class ResultadoQuiz(BaseModel):
    nota: float  # 0 a 10
    total_perguntas: int
    acertos: int
    correcao: list[CorrecaoPergunta]
    nivel_desbloqueado: bool = False
    novo_nivel_nome: str | None = None
    capitulo_desbloqueado: bool = False
    novo_capitulo_nome: str | None = None
    # Preenchido quando esse quiz era o do ÚLTIMO nível da trilha: não existe
    # "próximo nível" pra desbloquear, mas a prova final da trilha passa a
    # estar disponível — sem isso o aluno termina o último nível sem nenhum
    # aviso de que já pode fazer a prova final.
    prova_final_disponivel: bool = False
    capitulo_id: int | None = None
    capitulo_nome: str | None = None