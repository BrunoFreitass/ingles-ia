import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.exercise import Exercise, ExerciseAttempt
from app.models.user import User
from app.schemas.exercicio import ExercicioParaResponder, ExercicioSubmissao, ResultadoExercicio
from app.services.auth_service import get_current_user
from app.services.content_generation_service import obter_ou_gerar_exercicios
from app.services.gemini_client import GeminiIndisponivelError
from app.services.progress_service import buscar_licao_com_acesso

router = APIRouter(prefix="/levels/{level_id}/lessons/{lesson_id}/exercicios", tags=["exercícios"])


def _comparar_resposta(resposta_usuario, resposta_correta) -> bool:
    """
    Compara a resposta do aluno com o gabarito, normalizando espaços e
    maiúsculas/minúsculas. Funciona pros três formatos usados pelos tipos
    de exercício: string (maioria dos tipos), lista (não usado atualmente,
    mas suportado) e dict (tipo "ligar", pares palavra->emoji).
    """
    if resposta_correta is None:
        return False  # exercícios de "producao" não têm gabarito — nunca contam como "certo" automaticamente

    if isinstance(resposta_correta, str):
        return isinstance(resposta_usuario, str) and resposta_usuario.strip().lower() == resposta_correta.strip().lower()

    if isinstance(resposta_correta, dict):
        if not isinstance(resposta_usuario, dict):
            return False
        if set(resposta_usuario.keys()) != set(resposta_correta.keys()):
            return False
        return all(
            str(resposta_usuario[k]).strip().lower() == str(v).strip().lower()
            for k, v in resposta_correta.items()
        )

    if isinstance(resposta_correta, list):
        if not isinstance(resposta_usuario, list) or len(resposta_usuario) != len(resposta_correta):
            return False
        return [str(x).strip().lower() for x in resposta_usuario] == [
            str(x).strip().lower() for x in resposta_correta
        ]

    return resposta_usuario == resposta_correta


@router.get("", response_model=list[ExercicioParaResponder])
def listar_exercicios_da_licao(
    level_id: int,
    lesson_id: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """
    Retorna os até 10 exercícios de prática dessa lição, SEM revelar a
    resposta correta. Gera via IA na primeira chamada; nas próximas,
    reaproveita os exercícios já salvos.
    """
    licao = buscar_licao_com_acesso(db, usuario_atual, level_id, lesson_id)  # 404/403

    try:
        exercicios = obter_ou_gerar_exercicios(db, licao)
    except GeminiIndisponivelError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Não foi possível gerar os exercícios agora: {e}",
        ) from e

    return exercicios


@router.post("/{exercicio_id}/submit", response_model=ResultadoExercicio)
def submeter_resposta_exercicio(
    level_id: int,
    lesson_id: int,
    exercicio_id: int,
    submissao: ExercicioSubmissao,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(get_current_user),
):
    """
    Corrige a resposta de UM exercício e salva a tentativa. Diferente do
    quiz, aqui a correção é exercício a exercício (feedback imediato de
    prática), não em lote — e não desbloqueia nível sozinho: quem gate-keia
    o avanço continua sendo a prova do capítulo (quiz).
    """
    buscar_licao_com_acesso(db, usuario_atual, level_id, lesson_id)  # 404/403

    exercicio = (
        db.query(Exercise)
        .filter(Exercise.id == exercicio_id, Exercise.lesson_id == lesson_id)
        .first()
    )
    if not exercicio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercício não encontrado.")

    resposta_correta = (
        json.loads(exercicio.resposta_correta_json) if exercicio.resposta_correta_json else None
    )
    acertou = _comparar_resposta(submissao.resposta, resposta_correta)

    tentativa = ExerciseAttempt(
        user_id=usuario_atual.id,
        exercise_id=exercicio.id,
        resposta_dada_json=json.dumps(submissao.resposta, ensure_ascii=False),
        acertou=acertou,
    )
    db.add(tentativa)
    db.commit()

    # Produção livre não tem gabarito fixo — não faz sentido "corrigir" contra nada.
    resultado_acertou = acertou if exercicio.tipo != "producao" else True

    return ResultadoExercicio(
        exercicio_id=exercicio.id,
        acertou=resultado_acertou,
        resposta_correta=resposta_correta,
    )
