"""
Testa o fluxo de conversa (Fase 4) com o Gemini mockado — valida: sessão
inicia com mensagem da IA, histórico é montado corretamente a cada nova
mensagem, correção de erro aparece quando simulada, e sessões de usuários
diferentes não se misturam.
"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

CONTADOR = {"chamadas": 0}


def gerar_json_falso(self, prompt, **kwargs):
    CONTADOR["chamadas"] += 1
    if "(nenhuma mensagem ainda)" in prompt:
        # primeira chamada da sessão — IA puxa assunto
        return {"resposta": "Hi! What's your favorite thing to eat for breakfast?", "erro_corrigido": None}
    if "I are happy" in prompt:
        # simula ter detectado um erro na última mensagem do aluno
        return {
            "resposta": "That's great! I love pancakes too.",
            "erro_corrigido": "Você disse 'I are happy', mas o certo é 'I am happy' — 'I' sempre usa 'am'.",
        }
    return {"resposta": "Cool, tell me more!", "erro_corrigido": None}


with patch("app.services.gemini_client.GeminiClient.generate_json", gerar_json_falso):
    from fastapi.testclient import TestClient

    from app.core.database import Base, SessionLocal, engine
    from app.main import app
    from app.models.level import Lesson

    Base.metadata.create_all(bind=engine)
    client = TestClient(app)

    session_db = SessionLocal()
    licao = session_db.query(Lesson).first()
    session_db.close()

    if not licao:
        print("ERRO: rode scripts/seed.py antes deste teste.")
        sys.exit(1)

    LEVEL_ID, LESSON_ID = licao.level_id, licao.id

    client.post(
        "/auth/register",
        json={"nome": "Teste Fase4", "email": "fase4@teste.com", "senha": "senha12345"},
    )
    token = client.post(
        "/auth/login", data={"username": "fase4@teste.com", "password": "senha12345"}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # --- iniciar conversa ---
    r1 = client.post(f"/levels/{LEVEL_ID}/lessons/{LESSON_ID}/conversation/start", headers=headers)
    assert r1.status_code == 201, r1.text
    sessao = r1.json()
    print("POST start:", r1.status_code, "mensagens:", len(sessao["mensagens"]))
    assert len(sessao["mensagens"]) == 1
    assert sessao["mensagens"][0]["autor"] == "ia"
    assert "breakfast" in sessao["mensagens"][0]["texto"].lower()
    print("Confirmado: IA puxou assunto sozinha na primeira mensagem. ✔")

    session_id = sessao["id"]

    # --- mensagem SEM erro ---
    r2 = client.post(
        f"/levels/{LEVEL_ID}/lessons/{LESSON_ID}/conversation/{session_id}/message",
        json={"texto": "I like pizza."},
        headers=headers,
    )
    assert r2.status_code == 200, r2.text
    msg2 = r2.json()
    print("POST message (sem erro):", r2.status_code, "erro_corrigido:", msg2["erro_corrigido"])
    assert msg2["erro_corrigido"] is None
    assert msg2["autor"] == "ia"

    # --- mensagem COM erro (gatilho do mock: "I are happy") ---
    r3 = client.post(
        f"/levels/{LEVEL_ID}/lessons/{LESSON_ID}/conversation/{session_id}/message",
        json={"texto": "I are happy today."},
        headers=headers,
    )
    assert r3.status_code == 200, r3.text
    msg3 = r3.json()
    print("POST message (com erro):", r3.status_code, "erro_corrigido:", msg3["erro_corrigido"])
    assert msg3["erro_corrigido"] is not None
    assert "am" in msg3["erro_corrigido"]
    print("Confirmado: erro de gramática foi detectado e corrigido no campo erro_corrigido. ✔")

    # --- sessão de outro usuário não pode ser acessada ---
    client.post(
        "/auth/register",
        json={"nome": "Outro", "email": "outro4@teste.com", "senha": "senha12345"},
    )
    token_outro = client.post(
        "/auth/login", data={"username": "outro4@teste.com", "password": "senha12345"}
    ).json()["access_token"]
    headers_outro = {"Authorization": f"Bearer {token_outro}"}

    r4 = client.post(
        f"/levels/{LEVEL_ID}/lessons/{LESSON_ID}/conversation/{session_id}/message",
        json={"texto": "tentando acessar sessão de outro usuário"},
        headers=headers_outro,
    )
    assert r4.status_code == 404, r4.text
    print("Confirmado: usuário não consegue acessar sessão de conversa de outro usuário (404). ✔")

    print(f"\nTotal de chamadas ao Gemini (mockado): {CONTADOR['chamadas']}")
    print("✅ TODOS OS TESTES DA FASE 4 PASSARAM (com Gemini mockado)")