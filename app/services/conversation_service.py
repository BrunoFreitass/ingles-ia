"""
Orquestra a conversa com IA: inicia uma sessão (a IA puxa assunto sozinha) e
processa cada mensagem do aluno, enviando o histórico completo pro Gemini a
cada chamada (o modelo não tem memória própria entre chamadas — o "contexto"
da conversa é sempre reconstruído a partir do banco).
"""

from sqlalchemy.orm import Session

from app.models.conversation import ConversationMessage, ConversationSession
from app.models.level import Lesson
from app.models.user import User
from app.services.gemini_client import GeminiIndisponivelError, gemini_client
from app.services.prompts import prompt_conversa


def iniciar_sessao(db: Session, user: User, lesson: Lesson) -> ConversationSession:
    """Cria uma nova sessão de conversa e já gera a primeira mensagem (a IA puxa assunto)."""
    sessao = ConversationSession(user_id=user.id, lesson_id=lesson.id, tema=lesson.tema)
    db.add(sessao)
    db.flush()  # garante sessao.id

    dados = gemini_client.generate_json(prompt_conversa(lesson, historico=[]))
    resposta = dados.get("resposta")
    if not resposta:
        raise GeminiIndisponivelError("O Gemini respondeu sem gerar a mensagem inicial.")

    db.add(
        ConversationMessage(
            session_id=sessao.id, autor="ia", texto=resposta, texto_pt=dados.get("resposta_pt"), erro_corrigido=None
        )
    )
    db.commit()
    db.refresh(sessao)
    return sessao


def enviar_mensagem(db: Session, sessao: ConversationSession, texto_usuario: str) -> ConversationMessage:
    """
    Salva a mensagem do aluno, monta o histórico completo, chama o Gemini
    pra gerar a resposta (+ possível correção de erro) e salva a resposta.
    """
    lesson = sessao.lesson

    msg_usuario = ConversationMessage(session_id=sessao.id, autor="usuario", texto=texto_usuario)
    db.add(msg_usuario)
    db.flush()

    historico = (
        db.query(ConversationMessage)
        .filter(ConversationMessage.session_id == sessao.id)
        .order_by(ConversationMessage.criado_em)
        .all()
    )

    dados = gemini_client.generate_json(prompt_conversa(lesson, historico=historico))
    resposta = dados.get("resposta")
    if not resposta:
        raise GeminiIndisponivelError("O Gemini respondeu sem gerar a resposta da conversa.")

    erro_corrigido = dados.get("erro_corrigido")
    # Normaliza: a IA às vezes manda a string literal "null" em vez de JSON null de verdade
    if erro_corrigido in (None, "null", "None", ""):
        erro_corrigido = None

    msg_ia = ConversationMessage(
        session_id=sessao.id,
        autor="ia",
        texto=resposta,
        texto_pt=dados.get("resposta_pt"),
        erro_corrigido=erro_corrigido,
    )
    db.add(msg_ia)
    db.commit()
    db.refresh(msg_ia)
    return msg_ia