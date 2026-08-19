from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.quiz import Quiz, QuizAttempt, QuizQuestion
from app.models.user import User
from app.schemas.quiz import CorrecaoPergunta, QuizParaResponder, QuizSubmissao, ResultadoQuiz
from app.services.auth_service import get_current_user
from app.services.content_generation_service import obter_ou_gerar_quiz
from app.services.gemini_client import GeminiIndisponivelError
from app.services.progress_service import buscar_licao_com_acesso, verificar_e_avancar_nivel

router = APIRouter(prefix="/levels/{level_id}/lessons/{lesson_id}/quiz", tags=["quiz"])


@router.get("", response_model=QuizParaResponder)
def obter_quiz_da_licao(
    level_id: int,
    lesson_id: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """
    Retorna as 10 perguntas do quiz dessa lição, SEM revelar a resposta
    correta (o schema QuizParaResponder não inclui esse campo). Gera via
    IA na primeira chamada; nas próximas, reaproveita o quiz já salvo.
    """
    licao = buscar_licao_com_acesso(db, usuario_atual, level_id, lesson_id)  # 404/403

    try:
        quiz = obter_ou_gerar_quiz(db, licao)
    except GeminiIndisponivelError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Não foi possível gerar o quiz agora: {e}",
        ) from e

    # Recarrega com as perguntas (obter_ou_gerar_quiz pode retornar sem elas carregadas)
    quiz = (
        db.query(Quiz)
        .options(joinedload(Quiz.perguntas))
        .filter(Quiz.id == quiz.id)
        .first()
    )
    return quiz


@router.post("/submit", response_model=ResultadoQuiz)
def submeter_respostas(
    level_id: int,
    lesson_id: int,
    submissao: QuizSubmissao,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """
    Recebe as respostas do usuário, corrige contra o gabarito (só agora ele
    é revelado), salva a tentativa, verifica se o nível foi concluído (e
    avança o usuário automaticamente se sim) e retorna a nota + correção.
    """
    licao = buscar_licao_com_acesso(db, usuario_atual, level_id, lesson_id)  # 404/403

    try:
        quiz = obter_ou_gerar_quiz(db, licao)
    except GeminiIndisponivelError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Não foi possível corrigir o quiz agora: {e}",
        ) from e

    perguntas_por_id = {
        p.id: p
        for p in db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).all()
    }

    if not perguntas_por_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz sem perguntas.")

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

    novo_nivel = verificar_e_avancar_nivel(db, usuario_atual, licao.level)

    return ResultadoQuiz(
        nota=nota,
        total_perguntas=total,
        acertos=acertos,
        correcao=correcao,
        nivel_desbloqueado=novo_nivel is not None,
        novo_nivel_nome=novo_nivel.nome if novo_nivel else None,
    )
