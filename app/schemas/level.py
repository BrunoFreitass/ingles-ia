import json

from pydantic import BaseModel, ConfigDict, field_validator


def _personalizar(texto: str | None, primeiro_nome: str | None) -> str | None:
    """
    Substitui o placeholder '{nome}' pelo primeiro nome do usuário logado.
    Lições podem usar '{nome}' em frases de exemplo/gramática (ex: "Hi, I'm
    {nome}") pra soarem personalizadas em vez de sempre citar um nome fixo.
    Se por algum motivo não houver usuário (ou o texto não tiver o
    placeholder), retorna o texto original sem alteração.
    """
    if texto is None or not primeiro_nome:
        return texto
    return texto.replace("{nome}", primeiro_nome)


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
    def from_orm_model(cls, lesson, nome_usuario: str | None = None):
        """
        Monta o schema a partir do model, mapeando erros_comuns_json -> erros_comuns.

        `nome_usuario` é o nome completo do usuário logado (opcional). Quando
        informado, usamos só o primeiro nome pra personalizar qualquer trecho
        do conteúdo que use o placeholder '{nome}' (ex: frases de exemplo tipo
        "Hi, I'm {nome}"), em vez de sempre mostrar um nome fixo pra todo mundo.
        """
        primeiro_nome = nome_usuario.split(" ")[0] if nome_usuario else None

        erros_comuns = lesson.erros_comuns_json
        if isinstance(erros_comuns, str):
            erros_comuns = json.loads(erros_comuns)
        erros_comuns = [_personalizar(e, primeiro_nome) for e in (erros_comuns or [])]

        return cls(
            id=lesson.id,
            level_id=lesson.level_id,
            titulo=lesson.titulo,
            tema=lesson.tema,
            texto_gramatica=_personalizar(lesson.texto_gramatica, primeiro_nome),
            erros_comuns=erros_comuns,
            audio_url=lesson.audio_url,
            ordem=lesson.ordem,
            exemplos=[
                LessonExampleOut(
                    id=e.id,
                    frase_en=_personalizar(e.frase_en, primeiro_nome),
                    frase_pt=_personalizar(e.frase_pt, primeiro_nome),
                )
                for e in lesson.exemplos
            ],
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