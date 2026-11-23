"""Automated tests for SilatGuide.   Run from the project root:   pytest -v

What these tests DO cover (no GPU / Ollama needed):
  * dataset integrity (exactly 36 rows, category counts, required columns, no duplicates)
  * retrieval quality on exact / paraphrased / informal / misspelled questions
  * rejection of off-topic and unanswerable questions
  * safe routing of unsafe requests and prompt-injection attempts (LLM never called)
  * behaviour when Ollama is down / the model is missing (clearly labelled dataset fallback)
  * the Ollama HTTP client against a mocked `requests`

What they do NOT cover: the quality of real LLaMA 3.2 answers. That needs a manual check on a
machine with Ollama installed; an optional live test is provided (set RUN_OLLAMA_TESTS=1).
"""