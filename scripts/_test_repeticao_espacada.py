"""
Testa a repetição espaçada de ponta a ponta. Não precisa mockar o Gemini
aqui — a revisão em si não chama IA, só o algoritmo de intervalos. Insere
um flashcard direto no banco pra isolar o teste dessa peça específica.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.flashcard import Flashcard, UserFlashcardProgress  # noqa: E402
from app.models.level import Level  # noqa: E402

Base.metadata.create_all(bind=engine)
client = TestClient(app)

# --- setup: garante um nível e um flashcard direto no banco, sem IA ---
db = SessionLocal()
nivel = db.query(Level).first()
if not nivel:
    nivel = Level(ordem=1, nome="Nível de teste", nota_minima_para_avancar=7.0)
    db.add(nivel)
    db.commit()
    db.refresh(nivel)

cartao = Flashcard(palavra="dog", traducao="cachorro", exemplo="The dog is happy.", truque_memorizacao="-", nivel_id=nivel.id)
db.add(cartao)
db.commit()
db.refresh(cartao)
cartao_id = cartao.id
db.close()

client.post("/auth/register", json={"nome": "Teste SR", "email": "sr@teste.com", "senha": "senha12345"})
token = client.post("/auth/login", data={"username": "sr@teste.com", "password": "senha12345"}).json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# --- 1. fila de revisão deve trazer o cartão novo (nunca revisado) ---
r1 = client.get("/flashcards/review", headers=headers)
assert r1.status_code == 200, r1.text
fila1 = r1.json()
print("GET /flashcards/review (cartão novo):", r1.status_code, "-", len(fila1), "cartão(ões) na fila")
assert any(c["id"] == cartao_id for c in fila1)

# --- 2. acerta a revisão: intervalo deve ir de 1 -> 2 dias ---
r2 = client.post(f"/flashcards/{cartao_id}/review", json={"acertou": True}, headers=headers)
assert r2.status_code == 200, r2.text
progresso2 = r2.json()
print("POST review (acertou):", r2.status_code, "- intervalo_dias:", progresso2["intervalo_dias"], "acertos:", progresso2["acertos"])
assert progresso2["intervalo_dias"] == 2
assert progresso2["acertos"] == 1
assert progresso2["vezes_revisado"] == 1

# --- 3. fila de revisão agora NÃO deve trazer esse cartão (não está vencido) ---
r3 = client.get("/flashcards/review", headers=headers)
fila3 = r3.json()
print("GET /flashcards/review (logo após acertar):", r3.status_code, "-", len(fila3), "cartão(ões) na fila")
assert not any(c["id"] == cartao_id for c in fila3), "Cartão não deveria aparecer, ainda não está vencido!"

# --- 4. acerta de novo: intervalo deve dobrar de novo (2 -> 4) ---
r4 = client.post(f"/flashcards/{cartao_id}/review", json={"acertou": True}, headers=headers)
progresso4 = r4.json()
print("POST review (acertou de novo):", r4.status_code, "- intervalo_dias:", progresso4["intervalo_dias"])
assert progresso4["intervalo_dias"] == 4

# --- 5. erra: intervalo deve voltar pra 1 ---
r5 = client.post(f"/flashcards/{cartao_id}/review", json={"acertou": False}, headers=headers)
progresso5 = r5.json()
print("POST review (errou):", r5.status_code, "- intervalo_dias:", progresso5["intervalo_dias"], "acertos:", progresso5["acertos"])
assert progresso5["intervalo_dias"] == 1
assert progresso5["acertos"] == 2  # acertos não decrescem, só o intervalo reseta
assert progresso5["vezes_revisado"] == 3

# --- 6. simula o tempo passar (força proxima_revisao pro passado) e confirma que volta a aparecer ---
db = SessionLocal()
prog = db.query(UserFlashcardProgress).filter(UserFlashcardProgress.flashcard_id == cartao_id).first()
prog.proxima_revisao = datetime.now(timezone.utc) - timedelta(hours=1)
db.commit()
db.close()

r6 = client.get("/flashcards/review", headers=headers)
fila6 = r6.json()
print("GET /flashcards/review (após 'vencer'):", r6.status_code, "-", len(fila6), "cartão(ões) na fila")
assert any(c["id"] == cartao_id for c in fila6), "Cartão vencido deveria voltar a aparecer na fila!"

print("\n✅ TODOS OS TESTES DE REPETIÇÃO ESPAÇADA PASSARAM")
