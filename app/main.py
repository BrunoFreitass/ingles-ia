from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import (
    auth,
    capitulos,
    conversation,
    exercicios,
    flashcard_review,
    flashcards,
    immersion,
    levels,
    profile,
    quiz,
    ranking,
    users,
)

# Garante que todos os modelos foram importados antes do create_all
import app.models  # noqa: F401

app = FastAPI(title=settings.APP_NAME)

# Em dev, cria as tabelas automaticamente. Em produção, prefira Alembic
# (veja README.md) para ter controle de versão do schema.
if settings.ENVIRONMENT == "development":
    Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # "*" em dev; domínio real em produção via CORS_ORIGINS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(levels.router)
app.include_router(flashcards.router)
app.include_router(quiz.router)
app.include_router(exercicios.router)
app.include_router(conversation.router)
app.include_router(immersion.router)
app.include_router(flashcard_review.router)
app.include_router(capitulos.router)
app.include_router(ranking.router)
app.include_router(profile.router)


@app.get("/")
def raiz():
    return {"app": settings.APP_NAME, "status": "no ar"}