"""
Corrige em produção a frase de exemplo que tinha o nome "Bruno" fixo,
trocando por '{nome}' — o placeholder que o backend agora substitui pelo
primeiro nome de quem estiver logado (ver LessonOut.from_orm_model).

Só precisa rodar UMA VEZ, contra o banco que já está no ar (o seed.py normal
não toca em bancos que já têm dados, então esse ajuste não chega lá sozinho).
É seguro rodar mais de uma vez: se não achar "Bruno" em nenhuma frase, não
faz nada.

Uso local (banco de dev):
    python scripts/fix_exemplo_nome_fixo.py

Uso contra produção (Render):
    defina DATABASE_URL com a connection string de produção antes de rodar,
    ou rode como "Shell" a partir do próprio serviço no painel do Render.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal  # noqa: E402
from app.models.level import LessonExample  # noqa: E402

db = SessionLocal()

candidatos = (
    db.query(LessonExample)
    .filter(LessonExample.frase_en.contains("Bruno") | LessonExample.frase_pt.contains("Bruno"))
    .all()
)

if not candidatos:
    print("Nada pra corrigir — nenhuma frase de exemplo contém 'Bruno'.")
    db.close()
    sys.exit(0)

for exemplo in candidatos:
    antes_en, antes_pt = exemplo.frase_en, exemplo.frase_pt
    exemplo.frase_en = exemplo.frase_en.replace("Bruno", "{nome}")
    exemplo.frase_pt = exemplo.frase_pt.replace("Bruno", "{nome}")
    print(f"Lição {exemplo.lesson_id} — exemplo #{exemplo.id}:")
    print(f"  antes: {antes_en!r} / {antes_pt!r}")
    print(f"  depois: {exemplo.frase_en!r} / {exemplo.frase_pt!r}")

db.commit()
db.close()

print(f"\n{len(candidatos)} exemplo(s) corrigido(s) com sucesso.")