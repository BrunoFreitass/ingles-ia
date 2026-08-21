"""
Testa o motor de imersão (Fase 5) com o Gemini mockado: envio de texto
próprio, geração por tema, histórico, detalhe, e isolamento entre usuários.
"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def gerar_json_falso(self, prompt, **kwargs):
    if "tema solicitado" in prompt.lower():
        return {"texto_pt": "O futebol é o esporte mais popular do Brasil. Milhões assistem aos jogos todo fim de semana."}
    if "mercado" in prompt.lower():
        return {
            "texto_en": "Yesterday I went to the market to buy fruits and vegetables for the week.",
            "perguntas": [
                {"pergunta": "Qual é a palavra em inglês para 'mercado'?", "resposta": "market"},
                {"pergunta": "O texto fala sobre comprar o quê?", "resposta": "frutas e verduras"},
            ],
        }
    return {
        "texto_en": "Football is the most popular sport in Brazil. Millions watch the games every weekend.",
        "perguntas": [
            {"pergunta": "Qual é a palavra em inglês para 'esporte'?", "resposta": "sport"},
            {"pergunta": "O texto fala sobre qual dia da semana?", "resposta": "weekend (fim de semana)"},
        ],
    }


with patch("app.services.gemini_client.GeminiClient.generate_json", gerar_json_falso):
    from fastapi.testclient import TestClient

    from app.core.database import Base, engine
    from app.main import app

    Base.metadata.create_all(bind=engine)
    client = TestClient(app)

    client.post(
        "/auth/register",
        json={"nome": "Teste Fase5", "email": "fase5@teste.com", "senha": "senha12345"},
    )
    token = client.post(
        "/auth/login", data={"username": "fase5@teste.com", "password": "senha12345"}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # --- enviar texto próprio ---
    r1 = client.post(
        "/immersion/texts",
        json={"texto_pt": "Ontem eu fui ao mercado comprar frutas e verduras para a semana."},
        headers=headers,
    )
    assert r1.status_code == 201, r1.text
    texto1 = r1.json()
    print("POST /immersion/texts:", r1.status_code, "-", len(texto1["perguntas"]), "perguntas")
    assert "market" in texto1["texto_en"].lower()
    assert "Football" not in texto1["texto_en"]
    assert len(texto1["perguntas"]) == 2

    # --- gerar texto por tema ---
    r2 = client.post("/immersion/texts/generate", json={"tema": "futebol"}, headers=headers)
    assert r2.status_code == 201, r2.text
    texto2 = r2.json()
    print("POST /immersion/texts/generate:", r2.status_code, "- texto_pt:", texto2["texto_pt"][:50], "...")
    assert "futebol" in texto2["texto_pt"].lower() or "Football" in texto2["texto_en"]

    # --- histórico ---
    r3 = client.get("/immersion/texts", headers=headers)
    assert r3.status_code == 200, r3.text
    historico = r3.json()
    print("GET /immersion/texts:", r3.status_code, "-", len(historico), "itens no histórico")
    assert len(historico) == 2
    assert "texto_en" not in historico[0]  # versão resumida não deve trazer o texto todo

    # --- detalhe ---
    r4 = client.get(f"/immersion/texts/{texto1['id']}", headers=headers)
    assert r4.status_code == 200, r4.text
    assert r4.json()["id"] == texto1["id"]
    print("GET /immersion/texts/{id}:", r4.status_code, "- OK")

    # --- isolamento entre usuários ---
    client.post(
        "/auth/register",
        json={"nome": "Outro5", "email": "outro5@teste.com", "senha": "senha12345"},
    )
    token_outro = client.post(
        "/auth/login", data={"username": "outro5@teste.com", "password": "senha12345"}
    ).json()["access_token"]
    headers_outro = {"Authorization": f"Bearer {token_outro}"}

    r5 = client.get(f"/immersion/texts/{texto1['id']}", headers=headers_outro)
    assert r5.status_code == 404, r5.text
    print("Confirmado: usuário não acessa texto de imersão de outro usuário (404). ✔")

    r6 = client.get("/immersion/texts", headers=headers_outro)
    assert r6.json() == [], "Vazamento: histórico de outro usuário não deveria aparecer!"
    print("Confirmado: histórico é isolado por usuário. ✔")

    print("\n✅ TODOS OS TESTES DA FASE 5 PASSARAM (com Gemini mockado)")