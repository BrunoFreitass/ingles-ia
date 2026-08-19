"""
Ranking competitivo entre todos os usuários — nível atual, nota média e
total de erros. Pensado pra turma pequena (não pagina, calcula tudo de
uma vez — não é feito pra escalar pra milhares de usuários).
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.level import Level
from app.models.quiz import QuizAttempt, QuizQuestion
from app.models.user import User
from app.schemas.ranking import RankingItem
from app.services.progress_service import ordem_do_nivel_do_usuario


def calcular_ranking(db: Session, usuario_atual: User) -> list[RankingItem]:
    usuarios = db.query(User).filter(User.ativo.is_(True)).all()

    # Quantas perguntas cada quiz tem — evita bater no banco de novo por tentativa.
    total_perguntas_por_quiz = dict(
        db.query(QuizQuestion.quiz_id, func.count(QuizQuestion.id)).group_by(QuizQuestion.quiz_id).all()
    )

    linhas = []
    for usuario in usuarios:
        tentativas = db.query(QuizAttempt).filter(QuizAttempt.user_id == usuario.id).all()

        nota_media = sum(t.nota for t in tentativas) / len(tentativas) if tentativas else 0.0

        total_erros = 0
        for t in tentativas:
            total_perguntas = total_perguntas_por_quiz.get(t.quiz_id, 10)
            acertos_estimados = round((t.nota / 10) * total_perguntas)
            total_erros += max(0, total_perguntas - acertos_estimados)

        ordem_nivel = ordem_do_nivel_do_usuario(db, usuario)
        nivel = db.query(Level).filter(Level.ordem == ordem_nivel).first()

        linhas.append(
            {
                "user_id": usuario.id,
                "nome": usuario.nome,
                "nivel_atual_ordem": ordem_nivel,
                "nivel_atual_nome": nivel.nome if nivel else "—",
                "nota_media": round(nota_media, 1),
                "total_tentativas": len(tentativas),
                "total_erros": total_erros,
            }
        )

    # Critério: nível mais alto primeiro; nota média como desempate.
    linhas.sort(key=lambda x: (-x["nivel_atual_ordem"], -x["nota_media"]))

    return [
        RankingItem(
            posicao=i,
            nome=linha["nome"],
            nivel_atual_ordem=linha["nivel_atual_ordem"],
            nivel_atual_nome=linha["nivel_atual_nome"],
            nota_media=linha["nota_media"],
            total_tentativas=linha["total_tentativas"],
            total_erros=linha["total_erros"],
            eh_voce=(linha["user_id"] == usuario_atual.id),
        )
        for i, linha in enumerate(linhas, start=1)
    ]
