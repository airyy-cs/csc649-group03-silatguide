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
    

class SilatGuideBot:
    def __init__(
        self,
        retriever: SilatRetriever | None = None,
        llm: OllamaClient | None = None,
        settings: Settings | None = None,
    ):
        self.settings = settings or Settings.from_env()
        self.retriever = retriever or SilatRetriever(
            self.settings.dataset_path,
            threshold=self.settings.similarity_threshold,
            top_k=self.settings.top_k,
        )
        self.llm = llm or OllamaClient(self.settings)

 # ------------------------------------------------------------------ helpers
    @staticmethod
    def _source_dicts(matches: list[Match]) -> list[dict]:
        return [
            {"question": m.question, "source": m.source, "sources": split_sources(m.source),
             "category": m.category, "score": round(m.score, 3)}
            for m in matches
        ]

    # ------------------------------------------------------------------ main entry
    def answer(self, question: str) -> BotResponse:
        t0 = time.perf_counter()

        def done(resp: BotResponse) -> BotResponse:
            resp.latency_s = round(time.perf_counter() - t0, 2)
            return resp
            
        q = (question or "").strip()
        if not q:
            return done(BotResponse(EMPTY_MESSAGE, MODE_SMALLTALK))
        if is_greeting(q):
            return done(BotResponse(GREETING_MESSAGE, MODE_SMALLTALK))
        if is_thanks(q):
            return done(BotResponse(THANKS_MESSAGE, MODE_SMALLTALK))
        if is_prompt_injection(q):
            return done(BotResponse(INJECTION_MESSAGE, MODE_INJECTION))
        if is_harmful_request(q):
            return done(BotResponse(SAFETY_MESSAGE, MODE_REFUSED))

        result: RetrievalResult = self.retriever.search(q)
        if not result.is_relevant:
            return done(BotResponse(FALLBACK_MESSAGE, MODE_OUT_OF_SCOPE, top_score=result.top_score))

        matches = result.relevant_matches
        sources = self._source_dicts(matches)
        context = [{"question": m.question, "answer": m.answer} for m in matches]