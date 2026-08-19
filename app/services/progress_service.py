"""
Progresso real por nível: o usuário só acessa lições do nível que já
desbloqueou. Um nível é considerado completo quando o usuário tirou nota
>= nota_minima_para_avancar no quiz de TODAS as lições dele — nesse
momento, o próximo nível é desbloqueado automaticamente.

Usuário sem nivel_atual_id definido (nunca registrado com nível, ou banco
sem níveis na hora do registro) é tratado como se estivesse no nível de
ordem 1 — evita null-checks espalhados pelo resto do código.
"""

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.level import Lesson, Level
from app.models.quiz import Quiz, QuizAttempt
from app.models.user import User


def ordem_do_nivel_do_usuario(db: Session, user: User) -> int:
    """Retorna a ordem do nível mais alto que o usuário já desbloqueou."""
    if not user.nivel_atual_id:
        return 1
    nivel = db.query(Level).filter(Level.id == user.nivel_atual_id).first()
    return nivel.ordem if nivel else 1


def usuario_pode_acessar_nivel(db: Session, user: User, level: Level) -> bool:
    return level.ordem <= ordem_do_nivel_do_usuario(db, user)


def garantir_acesso_nivel(db: Session, user: User, level: Level) -> None:
    if not usuario_pode_acessar_nivel(db, user, level):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Você ainda não desbloqueou o nível '{level.nome}'. Complete o nível anterior primeiro.",
        )


def buscar_licao_com_acesso(db: Session, user: User, level_id: int, lesson_id: int) -> Lesson:
    """
    Busca a lição garantindo que o usuário tem acesso ao nível dela.
    404 se a lição não existe, 403 se o nível está bloqueado.
    """
    licao = db.query(Lesson).filter(Lesson.id == lesson_id, Lesson.level_id == level_id).first()
    if not licao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lição não encontrada.")

    nivel = db.query(Level).filter(Level.id == level_id).first()
    garantir_acesso_nivel(db, user, nivel)

    return licao


def nivel_esta_completo(db: Session, user: User, level: Level) -> bool:
    """
    True se o usuário tirou nota >= nota_minima_para_avancar no quiz de
    TODAS as lições desse nível (uma lição sem quiz gerado ainda conta
    como não completa).
    """
    licoes = db.query(Lesson).filter(Lesson.level_id == level.id).all()
    if not licoes:
        return False

    for licao in licoes:
        quiz = db.query(Quiz).filter(Quiz.lesson_id == licao.id).first()
        if not quiz:
            return False

        melhor_nota = (
            db.query(func.max(QuizAttempt.nota))
            .filter(QuizAttempt.quiz_id == quiz.id, QuizAttempt.user_id == user.id)
            .scalar()
        )
        if melhor_nota is None or melhor_nota < level.nota_minima_para_avancar:
            return False

    return True


def verificar_e_avancar_nivel(db: Session, user: User, level: Level) -> Level | None:
    """
    Chamado após o usuário enviar um quiz. Se o nível dessa lição ficou
    completo (todas as lições aprovadas) e existe um próximo nível ainda
    não desbloqueado, avança o usuário e retorna o novo nível. Senão,
    retorna None.
    """
    if not nivel_esta_completo(db, user, level):
        return None

    proximo_nivel = db.query(Level).filter(Level.ordem == level.ordem + 1).first()
    if not proximo_nivel:
        return None  # já é o último nível

    if proximo_nivel.ordem <= ordem_do_nivel_do_usuario(db, user):
        return None  # já estava desbloqueado, não é novidade

    user.nivel_atual_id = proximo_nivel.id
    db.commit()
    return proximo_nivel
