"""
Testa: prova final bloqueada até completar todos os 10 níveis do
capítulo; liberada e aprovável depois disso; e o ranking respondendo
corretamente com múltiplos usuários.
"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def gerar_json_falso(self, prompt, **kwargs):
    # Detecta se é a prova final (menciona "PROVA FINAL") ou um quiz normal de lição
    if "PROVA FINAL" in prompt:
        return {
            "perguntas": [
                {"pergunta": f"prova final pergunta {i}", "opcoes": ["A", "B", "C", "D"], "resposta_correta": "A"}
                for i in range(1, 16)
            ]
        }
    return {
        "perguntas": [
            {"pergunta": f"pergunta {i}", "opcoes": ["A", "B", "C", "D"], "resposta_correta": "A"}
            for i in range(1, 11)
        ]
    }


with patch("app.services.gemini_client.GeminiClient.generate_json", gerar_json_falso):
    from fastapi.testclient import TestClient

    from app.core.database import Base, SessionLocal, engine
    from app.main import app
    from app.models.level import Capitulo, Lesson, Level

    Base.metadata.create_all(bind=engine)
    client = TestClient(app)

    db = SessionLocal()
    capitulo1 = db.query(Capitulo).filter(Capitulo.ordem == 1).first()
    niveis = db.query(Level).filter(Level.capitulo_id == capitulo1.id).order_by(Level.ordem).all()
    db.close()

    if not capitulo1 or len(niveis) < 10:
        print("ERRO: rode scripts/seed.py e scripts/seed_capitulo1_niveis_3_a_10.py antes deste teste.")
        sys.exit(1)

    print(f"Capítulo '{capitulo1.nome}' tem {len(niveis)} níveis.")

    client.post("/auth/register", json={"nome": "Aluno Capitulo", "email": "capitulo@teste.com", "senha": "senha12345"})
    token = client.post("/auth/login", data={"username": "capitulo@teste.com", "password": "senha12345"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # --- 1. Prova final bloqueada antes de completar tudo ---
    r1 = client.get(f"/capitulos/{capitulo1.id}/prova-final", headers=headers)
    print("GET prova final (capítulo não completo):", r1.status_code)
    assert r1.status_code == 403

    # --- 2. Completa TODOS os 10 níveis (todas as lições de cada um) ---
    db = SessionLocal()
    for nivel in niveis:
        licoes = db.query(Lesson).filter(Lesson.level_id == nivel.id).all()
        for licao in licoes:
            rq = client.get(f"/levels/{nivel.id}/lessons/{licao.id}/quiz", headers=headers)
            assert rq.status_code == 200, f"Falhou pegar quiz da lição {licao.id}: {rq.text}"
            perguntas = rq.json()["perguntas"]
            respostas = [{"pergunta_id": p["id"], "resposta_selecionada": "A"} for p in perguntas]
            rs = client.post(
                f"/levels/{nivel.id}/lessons/{licao.id}/quiz/submit",
                json={"respostas": respostas},
                headers=headers,
            )
            assert rs.status_code == 200, f"Falhou submeter quiz da lição {licao.id}: {rs.text}"
    db.close()
    print("Todos os 10 níveis completados (todas as lições aprovadas).")

    # --- 3. Agora a prova final deve estar disponível ---
    r3 = client.get("/capitulos", headers=headers)
    capitulos_resp = r3.json()
    cap1_resp = next(c for c in capitulos_resp if c["id"] == capitulo1.id)
    print("GET /capitulos: prova_final_disponivel =", cap1_resp["prova_final_disponivel"])
    assert cap1_resp["prova_final_disponivel"] is True

    # --- 4. Pega e responde a prova final (15 perguntas) ---
    r4 = client.get(f"/capitulos/{capitulo1.id}/prova-final", headers=headers)
    assert r4.status_code == 200, r4.text
    perguntas_prova = r4.json()["perguntas"]
    print("GET prova final (agora liberada):", r4.status_code, "-", len(perguntas_prova), "perguntas")
    assert len(perguntas_prova) == 15
    assert "resposta_correta" not in perguntas_prova[0], "VAZAMENTO: gabarito apareceu antes de responder!"

    respostas_prova = [{"pergunta_id": p["id"], "resposta_selecionada": "A"} for p in perguntas_prova]
    r5 = client.post(
        f"/capitulos/{capitulo1.id}/prova-final/submit",
        json={"respostas": respostas_prova},
        headers=headers,
    )
    assert r5.status_code == 200, r5.text
    resultado = r5.json()
    print("POST prova final/submit: nota =", resultado["nota"], "| acertos =", resultado["acertos"])
    assert resultado["nota"] == 10.0
    assert resultado["acertos"] == 15

    # --- 5. Capítulo deve aparecer como concluído/aprovado agora ---
    r6 = client.get("/capitulos", headers=headers)
    cap1_depois = next(c for c in r6.json() if c["id"] == capitulo1.id)
    print("GET /capitulos (depois): prova_final_aprovada =", cap1_depois["prova_final_aprovada"], "| concluido =", cap1_depois["concluido"])
    assert cap1_depois["prova_final_aprovada"] is True
    assert cap1_depois["concluido"] is True

    # --- 6. Ranking deve incluir o usuário com dados corretos ---
    r7 = client.get("/ranking", headers=headers)
    assert r7.status_code == 200, r7.text
    ranking = r7.json()
    print("GET /ranking:", len(ranking), "usuário(s) no ranking")
    meu_item = next(item for item in ranking if item["eh_voce"])
    print(
        f"  -> {meu_item['nome']}: nível '{meu_item['nivel_atual_nome']}' (ordem {meu_item['nivel_atual_ordem']}), "
        f"nota média {meu_item['nota_media']}, {meu_item['total_tentativas']} tentativas, {meu_item['total_erros']} erros"
    )
    assert meu_item["nota_media"] == 10.0  # acertou tudo em tudo (lições + prova final)
    assert meu_item["total_erros"] == 0
    assert meu_item["total_tentativas"] == 12  # 11 quizzes de lição (nível 1 tem 2 lições) + 1 prova final

    print("\n✅ TODOS OS TESTES DE CAPÍTULOS/PROVA FINAL/RANKING PASSARAM")
