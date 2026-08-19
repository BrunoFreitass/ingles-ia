"""
Configurações centrais da aplicação.

Todas as variáveis vêm do .env (veja .env.example). Em desenvolvimento,
o padrão é SQLite (zero setup). Para produção, defina DATABASE_URL
apontando para um Postgres, ex:
    postgresql://usuario:senha@host:5432/ingles_ia
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Banco de dados
    DATABASE_URL: str = "sqlite:///./ingles_ia.db"

    # Autenticação
    SECRET_KEY: str = "troque-esta-chave-em-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h

    # Aplicação
    APP_NAME: str = "Inglês IA"
    ENVIRONMENT: str = "development"

    # Gemini (geração de flashcards e quiz)
    # Múltiplas chaves separadas por vírgula — mesma estratégia de rotação
    # usada no OrçaObra AI: se uma chave estourar a cota, tenta a próxima.
    GEMINI_API_KEYS: str = ""
    GEMINI_MODEL: str = "gemini-3.1-flash-lite"

    @property
    def gemini_keys_list(self) -> list[str]:
        return [k.strip() for k in self.GEMINI_API_KEYS.split(",") if k.strip()]

    # CORS — em dev, "*" libera geral (útil enquanto tudo roda em localhost).
    # Em produção, defina CORS_ORIGINS com o domínio real do frontend
    # (separado por vírgula se tiver mais de um, ex: preview + produção).
    CORS_ORIGINS: str = "*"

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
