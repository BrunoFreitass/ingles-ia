"""
Script de DIAGNÓSTICO — só lê, não apaga nada. Lista todos os níveis e
lições existentes no banco apontado por DATABASE_URL, pra confirmar
exatamente o que está duplicado antes de corrigir.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal  # noqa: E402
from app.models.level import Lesson, Level  # noqa: E402

db = SessionLocal()

niveis = db.query(Level).order_by(Level.ordem, Level.id).all()

print(f"Total de níveis no banco: {len(niveis)}\n")

for nivel in niveis:
    licoes = db.query(Lesson).filter(Lesson.level_id == nivel.id).order_by(Lesson.ordem).all()
    print(f"Nível id={nivel.id} | ordem={nivel.ordem} | nome='{nivel.nome}' | {len(licoes)} lição(ões)")
    for licao in licoes:
        print(f"    - Lição id={licao.id} | ordem={licao.ordem} | titulo='{licao.titulo}'")

db.close()