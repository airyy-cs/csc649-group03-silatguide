"""SilatGuide chatbot: ties safety checks, retrieval and the local LLM together.

Pipeline for every question
  1. empty / greeting / thanks      -> short canned reply (no LLM needed)
  2. prompt-injection attempt       -> polite refusal (LLM never sees it)
  3. harmful / violent request      -> safety message (LLM never sees it)
  4. TF-IDF retrieval (top 3)       -> low relevance? -> "friendly fallback message"
  5. relevant context -> LLaMA 3.2 via Ollama -> grounded answer + sources
  6. Ollama down / model missing    -> clearly *labelled* dataset answer (never passed off as LLaMA)
"""