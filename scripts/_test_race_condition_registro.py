"""
Simula a condição de corrida vista em produção: duas requisições de registro
quase simultâneas com o MESMO e-mail. Antes da correção, a segunda vazava
como 500; depois da correção, deve vir 409 (mesma mensagem amigável do
caso "e-mail duplicado" normal).
"""

import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from app.core.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

Base.metadata.create_all(bind=engine)
client = TestClient(app)

resultados = []
EMAIL = "corrida@teste.com"


def registrar():
    r = client.post(
        "/auth/register",
        json={"nome": "Teste Corrida", "email": EMAIL, "senha": "senha12345"},
    )
    resultados.append(r.status_code)


# Duas threads disparando o registro quase ao mesmo tempo — mesma janela de
# corrida do bug real (as duas passam pela checagem antes de qualquer
# commit terminar)
t1 = threading.Thread(target=registrar)
t2 = threading.Thread(target=registrar)
t1.start()
t2.start()
t1.join()
t2.join()

print("Status codes das duas requisições concorrentes:", sorted(resultados))

assert 500 not in resultados, f"BUG AINDA PRESENTE: uma das respostas foi 500! {resultados}"
assert 201 in resultados, "Nenhuma das duas conseguiu criar a conta!"
assert 409 in resultados, "A segunda deveria ter recebido 409 (e-mail duplicado), não recebeu."
assert sorted(resultados) == [201, 409], f"Esperado exatamente [201, 409], veio {sorted(resultados)}"

print("✅ Condição de corrida corrigida: 201 (criou) + 409 (duplicado), sem nenhum 500.")