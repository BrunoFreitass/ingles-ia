from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.level import Capitulo, Level
from app.models.quiz import Quiz, QuizAttempt, QuizQuestion
from app.models.user import User
from app.schemas.capitulo import CapituloListItem
from app.schemas.quiz import CorrecaoPergunta, QuizParaResponder, QuizSubmissao, ResultadoQuiz
from app.services.auth_service import get_current_user
from app.services.content_generation_service import obter_ou_gerar_prova_final
from app.services.gemini_client import GeminiIndisponivelError
from app.services.progress_service import (
    capitulo_esta_completo,
    garantir_acesso_prova_final,
    nivel_esta_completo,
    ordem_do_nivel_do_usuario,
    usuario_ja_passou_prova_final,
    usuario_pode_acessar_nivel,
    verificar_e_avancar_capitulo,
)

router = APIRouter(prefix="/capitulos", tags=["capítulos"])


def _serializar_capitulo(db: Session, user: User, capitulo: Capitulo) -> CapituloListItem:
    ordem_usuario = ordem_do_nivel_do_usuario(db, user)
    niveis_ordenados = sorted(capitulo.niveis, key=lambda n: n.ordem)

    niveis_serializados = []
    for nivel in niveis_ordenados:
        liberado = usuario_pode_acessar_nivel(db, user, nivel)
        niveis_serializados.append(
            {
                "id": nivel.id,
                "ordem": nivel.ordem,
                "nome": nivel.nome,
                "descricao": nivel.descricao,
                "liberado": liberado,
                "concluido": liberado and nivel_esta_completo(db, user, nivel),
                "lessons": nivel.lessons,
            }
        )

    # Capítulo liberado = usuário já alcançou o primeiro nível dele
    capitulo_liberado = niveis_ordenados[0].ordem <= ordem_usuario if niveis_ordenados else False
    prova_disponivel = capitulo_liberado and capitulo_esta_completo(db, user, capitulo)
    prova_aprovada = capitulo_liberado and usuario_ja_passou_prova_final(db, user, capitulo)

    return CapituloListItem(
        id=capitulo.id,
        ordem=capitulo.ordem,
        nome=capitulo.nome,
        descricao=capitulo.descricao,
        liberado=capitulo_liberado,
        concluido=prova_aprovada,
        prova_final_disponivel=prova_disponivel,
        prova_final_aprovada=prova_aprovada,
        niveis=niveis_serializados,
    )


@router.get("", response_model=list[CapituloListItem])
def listar_capitulos(
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """Lista todos os capítulos, com níveis/progresso/prova final calculados pro usuário."""
    capitulos = (
        db.query(Capitulo)
        .options(joinedload(Capitulo.niveis).joinedload(Level.lessons))
        .order_by(Capitulo.ordem)
        .all()
    )
    return [_serializar_capitulo(db, usuario_atual, c) for c in capitulos]


def _buscar_capitulo(db: Session, capitulo_id: int) -> Capitulo:
    capitulo = db.query(Capitulo).filter(Capitulo.id == capitulo_id).first()
    if not capitulo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Capítulo não encontrado.")
    return capitulo


@router.get("/{capitulo_id}/prova-final", response_model=QuizParaResponder)
def obter_prova_final(
    capitulo_id: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """
    Retorna as 15 perguntas da prova final do capítulo, SEM o gabarito.
    Só acessível depois de completar todos os níveis do capítulo.
    """
    capitulo = _buscar_capitulo(db, capitulo_id)
    garantir_acesso_prova_final(db, usuario_atual, capitulo)

    try:
        quiz = obter_ou_gerar_prova_final(db, capitulo)
    except GeminiIndisponivelError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Não foi possível gerar a prova final agora: {e}",
        ) from e

    quiz = db.query(Quiz).options(joinedload(Quiz.perguntas)).filter(Quiz.id == quiz.id).first()
    return quiz


@router.post("/{capitulo_id}/prova-final/submit", response_model=ResultadoQuiz)
def submeter_prova_final(
    capitulo_id: int,
    submissao: QuizSubmissao,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """Corrige a prova final, salva a tentativa, e avança de capítulo se passou."""
    capitulo = _buscar_capitulo(db, capitulo_id)
    garantir_acesso_prova_final(db, usuario_atual, capitulo)

    try:
        quiz = obter_ou_gerar_prova_final(db, capitulo)
    except GeminiIndisponivelError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Não foi possível corrigir a prova final agora: {e}",
        ) from e

    perguntas_por_id = {p.id: p for p in db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).all()}
    if not perguntas_por_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prova final sem perguntas.")

    respostas_por_pergunta_id = {r.pergunta_id: r.resposta_selecionada for r in submissao.respostas}

    correcao: list[CorrecaoPergunta] = []
    acertos = 0
    for pergunta_id, pergunta in perguntas_por_id.items():
        resposta_selecionada = respostas_por_pergunta_id.get(pergunta_id, "")
        acertou = resposta_selecionada == pergunta.resposta_correta
        if acertou:
            acertos += 1
        correcao.append(
            CorrecaoPergunta(
                pergunta_id=pergunta_id,
                pergunta=pergunta.pergunta,
                resposta_selecionada=resposta_selecionada,
                resposta_correta=pergunta.resposta_correta,
                acertou=acertou,
            )
        )

    total = len(perguntas_por_id)
    nota = round((acertos / total) * 10, 1) if total else 0.0

    tentativa = QuizAttempt(
        user_id=usuario_atual.id,
        quiz_id=quiz.id,
        nota=nota,
        respostas_json=submissao.model_dump_json(),
    )
    db.add(tentativa)
    db.commit()

    novo_nivel = verificar_e_avancar_capitulo(db, usuario_atual, capitulo)

    return ResultadoQuiz(
        nota=nota,
        total_perguntas=total,
        acertos=acertos,
        correcao=correcao,
        capitulo_desbloqueado=novo_nivel is not None,
        novo_capitulo_nome=None,  # o "novo capítulo" só existe quando alguém escrever o próximo
    )
