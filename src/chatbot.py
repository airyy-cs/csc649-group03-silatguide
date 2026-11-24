"""SilatGuide chatbot: ties safety checks, retrieval and the local LLM together.

Pipeline for every question
  1. empty / greeting / thanks      -> short canned reply (no LLM needed)
  2. prompt-injection attempt       -> polite refusal (LLM never sees it)
  3. harmful / violent request      -> safety message (LLM never sees it)
  4. TF-IDF retrieval (top 3)       -> low relevance? -> "friendly fallback message"
  5. relevant context -> LLaMA 3.2 via Ollama -> grounded answer + sources
  6. Ollama down / model missing    -> clearly *labelled* dataset answer (never passed off as LLaMA)
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

from .llm import OllamaClient, OllamaError
from .retrieval import Match, RetrievalResult, SilatRetriever
from .utils import (
    EMPTY_MESSAGE, FALLBACK_MESSAGE, GREETING_MESSAGE, INJECTION_MESSAGE, SAFETY_MESSAGE,
    THANKS_MESSAGE, Settings, is_greeting, is_harmful_request, is_prompt_injection, is_thanks,
    split_sources,
)

log = logging.getLogger(__name__)

# Response modes (the UI shows a different badge for each one)
MODE_LLM = "llm"                      # answered by LLaMA 3.2 using retrieved context
MODE_DATASET = "dataset_fallback"     # Ollama unavailable -> raw dataset answer, clearly labelled
MODE_OUT_OF_SCOPE = "out_of_scope"    # nothing relevant in the dataset
MODE_REFUSED = "refused"              # unsafe request
MODE_INJECTION = "injection_refused"  # attempt to override the rules
MODE_SMALLTALK = "smalltalk"          # greeting / thanks / empty


@dataclass
class BotResponse:
    text: str
    mode: str
    sources: list[dict] = field(default_factory=list)   # [{question, source, category, score}]
    error: str = ""                                      # user-safe reason if the LLM failed
    latency_s: float = 0.0
    used_llm: bool = False
    top_score: float = 0.0