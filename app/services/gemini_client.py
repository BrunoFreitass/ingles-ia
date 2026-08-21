"""
Cliente Gemini com rotação de múltiplas chaves de API.

Mesma estratégia usada no OrçaObra AI: se uma chave estourar a cota (erro de
quota/rate-limit), tenta automaticamente a próxima chave da lista antes de
desistir. Pede resposta em JSON puro (response_mime_type) pra evitar ter que
lidar com texto solto ou cercas de markdown ao redor do JSON.
"""

import json
import logging

import google.generativeai as genai

from app.core.config import settings

logger = logging.getLogger("ingles_ia.gemini")


class GeminiIndisponivelError(Exception):
    """Levantada quando todas as chaves configuradas falharam."""


class GeminiClient:
    def __init__(self, api_keys: list[str] | None = None, model_name: str | None = None):
        self.api_keys = api_keys if api_keys is not None else settings.gemini_keys_list
        self.model_name = model_name or settings.GEMINI_MODEL

    def generate_json(self, prompt: str, *, temperature: float = 0.7) -> dict:
        """
        Chama o Gemini pedindo saída em JSON, tentando cada chave configurada
        em sequência até uma funcionar. Lança GeminiIndisponivelError se
        nenhuma chave funcionar.
        """
        if not self.api_keys:
            raise GeminiIndisponivelError(
                "Nenhuma GEMINI_API_KEYS configurada no .env. "
                "Defina ao menos uma chave para gerar conteúdo por IA."
            )

        ultimo_erro: Exception | None = None

        for i, chave in enumerate(self.api_keys):
            try:
                genai.configure(api_key=chave)
                model = genai.GenerativeModel(self.model_name)
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": temperature,
                        "response_mime_type": "application/json",
                    },
                )
                texto = response.text.strip()
                # Salvaguarda: caso o modelo ainda envolva o JSON em ```json ... ```
                if texto.startswith("```"):
                    texto = texto.strip("`")
                    texto = texto.removeprefix("json").strip()

                logger.info("Gemini respondeu com sucesso usando a chave #%d", i + 1)
                return json.loads(texto)

            except Exception as e:  # noqa: BLE001 — queremos capturar qualquer falha e tentar a próxima chave
                logger.warning("Chave Gemini #%d falhou (%s), tentando a próxima...", i + 1, e)
                ultimo_erro = e
                continue

        raise GeminiIndisponivelError(
            f"Todas as {len(self.api_keys)} chave(s) Gemini falharam. Último erro: {ultimo_erro}"
        )


gemini_client = GeminiClient()