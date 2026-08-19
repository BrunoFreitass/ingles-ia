"""
Testa a Fase 3 de ponta a ponta SEM chamar a API real do Gemini (sandbox
sem acesso a generativelanguage.googleapis.com). Usa TestClient (roda a
app no mesmo processo Python) pra que o monkeypatch do GeminiClient
realmente tenha efeito — rodar contra um `uvicorn` externo não funcionaria,
pois o patch não atravessa processos.

Isso NÃO substitui testar com uma chave Gemini real depois — só garante que
toda a orquestração ao redor da IA (endpoints, banco, cache, correção)
está correta.
"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

FLASHCARDS_FALSOS = {
    "flashcards": [
        {
            "palavra": "breakfast",
            "traducao": "café da manhã",
            "exemplo": "I always have a big breakfast.",
            "truque_memorizacao": "break (quebrar) + fast (jejum) — 'quebrar o jejum' da noite.",
        },
        {
            "palavra": "yesterday",
            "traducao": "ontem",
            "exemplo": "I called her yesterday.",
            "truque_memorizacao": "Pense em 'ayer' do espanhol, mas com 'yesterday' em inglês.",
        },
    ]
}

QUIZ_FALSO = {
    "perguntas": [
        {"pergunta": f"Pergunta de teste #{i}", "opcoes": ["A", "B", "C", "D"], "resposta_correta": "A"}
        for i in range(1, 11)
    ]
}


def gerar_json_falso(self, prompt, **kwargs):
    if "flashcard" in prompt.lower():
        return FLASHCARDS_FALSOS
    return QUIZ_FALSO


with patch("app.services.gemini_client.GeminiClient.generate_json", gerar_json_falso):
    from fastapi.testclient import TestClient

    from app.core.database import Base, SessionLocal, engine
    from app.main import app
    from app.models.level import Lesson

    Base.metadata.create_all(bind=engine)
    client = TestClient(app)

    session = SessionLocal()
    licao = session.query(Lesson).first()
    session.close()

    if not licao:
        print("ERRO: rode scripts/seed.py antes deste teste.")
        sys.exit(1)

    LEVEL_ID = licao.level_id
    LESSON_ID = licao.id

    client.post(
        "/auth/register",
        json={"nome": "Teste Fase3", "email": "fase3@teste.com", "senha": "senha12345"},
    )
    token_resp = client.post(
        "/auth/login", data={"username": "fase3@teste.com", "password": "senha12345"}
    )
    token = token_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r1 = client.get(f"/levels/{LEVEL_ID}/lessons/{LESSON_ID}/flashcards", headers=headers)
    print(
        "GET flashcards (1a vez):",
        r1.status_code,
        r1.json() if r1.status_code != 200 else f"{len(r1.json())} cartões",
    )
    assert r1.status_code == 200, r1.text
    assert len(r1.json()) == 2

    r2 = client.get(f"/levels/{LEVEL_ID}/lessons/{LESSON_ID}/flashcards", headers=headers)
    print("GET flashcards (2a vez, deve vir do cache):", r2.status_code, len(r2.json()), "cartões")
    assert r1.json() == r2.json(), "Cache falhou: gerou conteúdo diferente na 2a chamada!"

    rq = client.get(f"/levels/{LEVEL_ID}/lessons/{LESSON_ID}/quiz", headers=headers)
    assert rq.status_code == 200, rq.text
    quiz_data = rq.json()
    print("GET quiz:", rq.status_code, len(quiz_data["perguntas"]), "perguntas")
    assert len(quiz_data["perguntas"]) == 10
    assert "resposta_correta" not in quiz_data["perguntas"][0], "VAZAMENTO: gabarito apareceu antes de responder!"
    print("Confirmado: resposta_correta NÃO aparece antes da submissão. ✔")

    perguntas = quiz_data["perguntas"]
    respostas = [
        {"pergunta_id": p["id"], "resposta_selecionada": "A" if i < 7 else "B"}
        for i, p in enumerate(perguntas)
    ]

    rs = client.post(
        f"/levels/{LEVEL_ID}/lessons/{LESSON_ID}/quiz/submit",
        json={"respostas": respostas},
        headers=headers,
    )
    assert rs.status_code == 200, rs.text
    resultado = rs.json()
    print("POST submit:", rs.status_code, "nota:", resultado["nota"], "acertos:", resultado["acertos"])
    assert resultado["acertos"] == 7
    assert resultado["nota"] == 7.0
    assert resultado["correcao"][0]["resposta_correta"] == "A", "Gabarito não veio na correção!"
    print("Confirmado: nota calculada certa (7.0) e gabarito revelado na correção. ✔")

    rq2 = client.get(f"/levels/{LEVEL_ID}/lessons/{LESSON_ID}/quiz", headers=headers)
    assert rq2.json()["id"] == quiz_data["id"], "Cache do quiz falhou: gerou um quiz novo!"
    print("Confirmado: segunda chamada ao quiz reaproveita o mesmo (cache). ✔")

    print("\n✅ TODOS OS TESTES DA FASE 3 PASSARAM (com Gemini mockado)")
