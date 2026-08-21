"""
Testa o progresso real por nível: usuário começa só com o nível 1 liberado,
não consegue acessar lições do nível 2, e ao tirar nota >= mínima no quiz de
TODAS as lições do nível 1, o nível 2 é desbloqueado automaticamente.
"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def gerar_json_falso(self, prompt, **kwargs):
    # Todas as perguntas com resposta "A" — o teste sempre responde "A" pra
    # simular acerto total (nota 10, bem acima do mínimo de 7).
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
    from app.models.level import Lesson, Level

    Base.metadata.create_all(bind=engine)
    client = TestClient(app)

    db = SessionLocal()
    nivel1 = db.query(Level).filter(Level.ordem == 1).first()
    nivel2 = db.query(Level).filter(Level.ordem == 2).first()
    licoes_nivel1 = db.query(Lesson).filter(Lesson.level_id == nivel1.id).all()
    licao_nivel2 = db.query(Lesson).filter(Lesson.level_id == nivel2.id).first()
    db.close()

    if not nivel2 or not licao_nivel2:
        print("ERRO: rode scripts/seed.py antes deste teste (precisa de 2+ níveis).")
        sys.exit(1)

    print(f"Nível 1 tem {len(licoes_nivel1)} lição(ões); Nível 2 existe: {nivel2.nome}")

    # --- registro: já deve nascer com nível 1 liberado ---
    client.post("/auth/register", json={"nome": "Teste Progresso", "email": "progresso@teste.com", "senha": "senha12345"})
    token = client.post("/auth/login", data={"username": "progresso@teste.com", "password": "senha12345"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # --- 1. GET /levels: nível 1 liberado, nível 2 bloqueado ---
    r1 = client.get("/levels", headers=headers)
    niveis = r1.json()
    n1 = next(n for n in niveis if n["ordem"] == 1)
    n2 = next(n for n in niveis if n["ordem"] == 2)
    print("GET /levels: nível1 liberado =", n1["liberado"], "| nível2 liberado =", n2["liberado"])
    assert n1["liberado"] is True
    assert n2["liberado"] is False

    # --- 2. Tentar acessar lição do nível 2 -> 403 ---
    r2 = client.get(f"/levels/{nivel2.id}/lessons/{licao_nivel2.id}", headers=headers)
    print("GET lição do nível 2 (bloqueado):", r2.status_code)
    assert r2.status_code == 403

    # --- 3. Tentar pegar quiz da lição do nível 2 -> também 403 ---
    r3 = client.get(f"/levels/{nivel2.id}/lessons/{licao_nivel2.id}/quiz", headers=headers)
    print("GET quiz do nível 2 (bloqueado):", r3.status_code)
    assert r3.status_code == 403

    # --- 4. Passar em todas as lições do nível 1 ---
    for licao in licoes_nivel1:
        rq = client.get(f"/levels/{nivel1.id}/lessons/{licao.id}/quiz", headers=headers)
        assert rq.status_code == 200, rq.text
        perguntas = rq.json()["perguntas"]
        respostas = [{"pergunta_id": p["id"], "resposta_selecionada": "A"} for p in perguntas]
        rs = client.post(
            f"/levels/{nivel1.id}/lessons/{licao.id}/quiz/submit",
            json={"respostas": respostas},
            headers=headers,
        )
        assert rs.status_code == 200, rs.text
        resultado = rs.json()
        print(
            f"Quiz da lição '{licao.titulo}': nota {resultado['nota']}"
            f" | nivel_desbloqueado={resultado['nivel_desbloqueado']}"
            f" | novo_nivel_nome={resultado['novo_nivel_nome']}"
        )

    # A última submissão (a que completa o nível) deve ter desbloqueado o nível 2
    assert resultado["nivel_desbloqueado"] is True
    assert resultado["novo_nivel_nome"] == nivel2.nome
    print("Confirmado: nível 2 foi desbloqueado após completar todas as lições do nível 1. ✔")

    # --- 5. Agora GET /levels deve mostrar nível 2 liberado, e nível 1 concluído ---
    r5 = client.get("/levels", headers=headers)
    niveis5 = r5.json()
    n1_depois = next(n for n in niveis5 if n["ordem"] == 1)
    n2_depois = next(n for n in niveis5 if n["ordem"] == 2)
    print("GET /levels (depois): nível1 concluido =", n1_depois["concluido"], "| nível2 liberado =", n2_depois["liberado"])
    assert n1_depois["concluido"] is True
    assert n2_depois["liberado"] is True

    # --- 6. Agora a lição do nível 2 deve ser acessível ---
    r6 = client.get(f"/levels/{nivel2.id}/lessons/{licao_nivel2.id}", headers=headers)
    print("GET lição do nível 2 (agora liberado):", r6.status_code)
    assert r6.status_code == 200

    # --- 7. /auth/me deve refletir o novo nivel_atual_id ---
    r7 = client.get("/auth/me", headers=headers)
    print("GET /auth/me: nivel_atual_id =", r7.json()["nivel_atual_id"], "(esperado:", nivel2.id, ")")
    assert r7.json()["nivel_atual_id"] == nivel2.id

    print("\n✅ TODOS OS TESTES DE PROGRESSO POR NÍVEL PASSARAM")