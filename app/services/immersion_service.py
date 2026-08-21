"""
Motor de imersão: recebe um texto em PT-BR do aluno, traduz pro inglês e gera
perguntas de vocabulário/compreensão sobre ele. Também pode gerar um texto
novo em português a partir de um tema pedido pelo aluno (e já processá-lo
pelo mesmo pipeline de tradução + perguntas).

Diferente de flashcards/quiz, aqui não há cache — cada texto é único (o
aluno decide o que colar ou pedir), então sempre chama o Gemini.
"""

import json

from sqlalchemy.orm import Session

from app.models.conversation import ImmersionText
from app.models.user import User
from app.services.gemini_client import GeminiIndisponivelError, gemini_client
from app.services.prompts import prompt_gerar_texto_por_tema, prompt_traduzir_e_gerar_perguntas


def processar_texto(db: Session, user: User, texto_pt: str) -> ImmersionText:
    """Traduz o texto e gera as perguntas, salvando o registro completo."""
    dados = gemini_client.generate_json(prompt_traduzir_e_gerar_perguntas(texto_pt))
    texto_en = dados.get("texto_en")
    perguntas = dados.get("perguntas", [])

    if not texto_en:
        raise GeminiIndisponivelError("O Gemini respondeu sem gerar a tradução do texto.")

    registro = ImmersionText(
        user_id=user.id,
        texto_pt=texto_pt,
        texto_en=texto_en,
        perguntas_json=json.dumps(perguntas, ensure_ascii=False),
    )
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


def gerar_texto_por_tema(db: Session, user: User, tema: str) -> ImmersionText:
    """Gera um texto novo em português sobre o tema pedido, e já processa (traduz + perguntas)."""
    dados = gemini_client.generate_json(prompt_gerar_texto_por_tema(tema))
    texto_pt = dados.get("texto_pt")

    if not texto_pt:
        raise GeminiIndisponivelError("O Gemini respondeu sem gerar o texto sobre o tema pedido.")

    return processar_texto(db, user, texto_pt)