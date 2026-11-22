"""Local LLM integration for SilatGuide using Ollama."""

from __future__ import annotations

from dataclasses import dataclass, field

import requests

from .utils import FALLBACK_MESSAGE, Settings


class OllamaError(Exception):
    user_message = "The local language model could not be used."

    def __init__(self, detail: str = ""):
        super().__init__(detail or self.user_message)
        self.detail = detail


class OllamaUnavailable(OllamaError):
    user_message = "Ollama is not running. Start Ollama and try again."


class OllamaModelMissing(OllamaError):
    user_message = "The model is missing. Run ollama pull llama3.2:3b."


class OllamaTimeout(OllamaError):
    user_message = "The model took too long to answer."


class OllamaBadResponse(OllamaError):
    user_message = "Ollama returned an unexpected response."