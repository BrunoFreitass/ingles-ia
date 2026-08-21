"""
Setup do SQLAlchemy: engine, sessão e dependência get_db para os endpoints.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


def _normalizar_database_url(url: str) -> str:
    """
    Alguns provedores de hospedagem (Render, Railway, Heroku) entregam a
    connection string no esquema antigo "postgres://", que o SQLAlchemy 1.4+
    não aceita mais (exige "postgresql://"). Também força o driver psycopg
    (v3, instalado via requirements-postgres.txt) explicitamente, já que sem
    isso o SQLAlchemy tentaria usar psycopg2 por padrão, que não instalamos.
    """
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


database_url = _normalizar_database_url(settings.DATABASE_URL)

# connect_args só é necessário para SQLite (permite uso multi-thread)
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}

engine = create_engine(database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    """Dependência do FastAPI: abre uma sessão por request e fecha no final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()