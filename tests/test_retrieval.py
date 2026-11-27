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
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

import pytest
import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src import chatbot as cb  # noqa: E402
from src.chatbot import SilatGuideBot  # noqa: E402
from src.llm import (  # noqa: E402
    OllamaClient, OllamaModelMissing, OllamaTimeout, OllamaUnavailable,
)
from src.retrieval import DatasetError, SilatRetriever, load_dataset, validate_dataset  # noqa: E402
from src.utils import FALLBACK_MESSAGE, Settings  # noqa: E402

DATA = ROOT / "data" / "silat_qa.csv"
CASES = list(csv.DictReader(open(ROOT / "tests" / "test_cases.csv", encoding="utf-8")))

EXPECTED_CATEGORIES = {
    "Introduction to Silat": 5, "History and Origins of Silat": 5, "Types and Styles of Silat": 4,
    "Malay Culture and Heritage": 4, "Basic Silat Movements and Techniques": 4,
    "Ethics and Discipline": 4, "Training Safety": 4, "Traditional Clothing and Equipment": 3,
    "General Beginner Questions": 3,
}
class FakeLLM:
    """Stands in for Ollama so retrieval/routing tests are fast and deterministic."""

    def __init__(self):
        self.calls = []

    def generate(self, question, context):
        self.calls.append((question, context))
        return "FAKE-LLM-ANSWER"


@pytest.fixture(scope="module")
def retriever():
    return SilatRetriever(DATA, threshold=0.25, top_k=3)


@pytest.fixture()
def bot(retriever):
    return SilatGuideBot(retriever=retriever, llm=FakeLLM())
def test_dataset_has_exactly_36_unique_rows():
    df, report = load_dataset(DATA)
    assert len(df) == 36
    assert report["empty_questions"] == [] and report["empty_answers"] == []
    assert report["duplicate_questions"] == []


def test_dataset_columns_and_categories():
    df, report = load_dataset(DATA)
    assert list(df.columns) == ["Question", "Answer", "Source", "Category"]
    assert report["categories"] == EXPECTED_CATEGORIES


def test_every_entry_has_a_source_and_reasonable_length():
    df, _ = load_dataset(DATA)
    assert (df["Source"].str.len() > 10).all()
    assert df["Answer"].str.split().str.len().between(25, 90).all()

def test_validator_detects_bad_data(tmp_path):
    import pandas as pd

    df = pd.DataFrame({
        "Question": ["A?", "a ?", ""],
        "Answer": ["x", "y", "z"],
        "Source": ["s"] * 3,
        "Category": ["c"] * 3,
    })

    rep = validate_dataset(df)

    assert rep["duplicate_questions"] == [(0, 1)]
    assert rep["empty_questions"] == [2]

    bad = tmp_path / "bad.csv"
    bad.write_text("Question,Answer\nq,a\n", encoding="utf-8")

    with pytest.raises(DatasetError):
        load_dataset(bad)

    with pytest.raises(DatasetError):
        load_dataset(tmp_path / "missing.csv")
    
    @pytest.mark.parametrize(
    "case",
    [c for c in CASES if c["expected_behavior"] == "answer"],
    ids=lambda c: c["id"],
)
def test_relevant_questions_retrieve_right_entry(retriever, case):
    res = retriever.search(case["question"])

    assert res.is_relevant, (
        f"rejected (score={res.top_score:.3f}, "
        f"coverage={res.coverage:.2f})"
    )

    needle = case["expected_top_question_contains"].lower()

    assert any(
        needle in m.question.lower()
        for m in res.matches[:3]
    ), [m.question for m in res.matches]
    @pytest.mark.parametrize(
    "case",
    [c for c in CASES if c["expected_behavior"] == "fallback"],
    ids=lambda c: c["id"],
)
def test_offtopic_and_unanswerable_are_rejected(retriever, case):
    res = retriever.search(case["question"])

    assert not res.is_relevant, (
        f"wrongly accepted (score={res.top_score:.3f}, "
        f"coverage={res.coverage:.2f})"
    )

    assert res.relevant_matches == []
@pytest.mark.parametrize(
    "case",
    [c for c in CASES if c["expected_behavior"] == "answer"][:6],
    ids=lambda c: c["id"],
)
def test_relevant_question_reaches_llm_with_context_and_sources(bot, case):
    r = bot.answer(case["question"])

    assert r.mode == cb.MODE_LLM
    assert r.used_llm
    assert r.text == "FAKE-LLM-ANSWER"

    assert r.sources
    assert all(s["source"] for s in r.sources)

    question, context = bot.llm.calls[-1]

    assert 1 <= len(context) <= 3
@pytest.mark.parametrize(
    "case",
    [c for c in CASES if c["expected_behavior"] == "refused"],
    ids=lambda c: c["id"],
)
def test_unsafe_requests_are_refused_without_llm(bot, case):
    r = bot.answer(case["question"])

    assert r.mode == cb.MODE_REFUSED
    assert "can't help" in r.text.lower()
    assert bot.llm.calls == []

@pytest.mark.parametrize(
    "case",
    [c for c in CASES if c["expected_behavior"] == "injection"],
    ids=lambda c: c["id"],
)
def test_prompt_injection_is_refused_without_llm(bot, case):
    r = bot.answer(case["question"])

    assert r.mode == cb.MODE_INJECTION
    assert "system prompt" not in r.text.lower() or "can't" in r.text.lower()
    assert bot.llm.calls == []
def test_small_talk_and_empty_input(bot):
    assert bot.answer("").mode == cb.MODE_SMALLTALK
    assert bot.answer("Hello!").mode == cb.MODE_SMALLTALK
    assert bot.answer("thank you").mode == cb.MODE_SMALLTALK
    assert bot.llm.calls == []
def test_model_saying_it_does_not_know_becomes_standard_fallback(retriever):
    class Refusing(FakeLLM):
        def generate(self, q, c):
            return FALLBACK_MESSAGE

    r = SilatGuideBot(
        retriever=retriever,
        llm=Refusing(),
    ).answer("What is Silat?")

    assert r.mode == cb.MODE_OUT_OF_SCOPE
    assert r.sources == []
# ------------------------------------------------------------- Ollama failure handling
@pytest.mark.parametrize("exc, expected_text", [
    (OllamaUnavailable("x"), "not running"),
    (OllamaModelMissing("x"), "ollama pull"),
    (OllamaTimeout("x"), "too long"),
])
def test_ollama_failure_gives_labelled_dataset_fallback(retriever, exc, expected_text):
    class Broken:
        def generate(self, q, c):
            raise exc

    r = SilatGuideBot(retriever=retriever, llm=Broken()).answer("What is a tengkolok?")
    assert r.mode == cb.MODE_DATASET, "must NOT be presented as an LLM answer"
    assert r.used_llm is False
    assert expected_text in r.error.lower()
    assert "tengkolok" in r.text.lower() and len(r.sources) == 1


def test_real_connection_failure_to_closed_port(retriever):
    s = Settings(ollama_host="http://127.0.0.1:9", timeout_seconds=2)
    r = SilatGuideBot(retriever=retriever, llm=OllamaClient(s), settings=s).answer("What is Silat?")
    assert r.mode == cb.MODE_DATASET and "not running" in r.error.lower()
    st = OllamaClient(s).status(timeout=1)
    assert not st.reachable and not st.ok


# ------------------------------------------------------- Ollama client with mocked HTTP
class _Resp:
    def __init__(self, code=200, payload=None, text=""):
        self.status_code, self._p, self.text = code, payload, text

    def json(self):
        if self._p is None:
            raise ValueError("no json")
        return self._p

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(str(self.status_code))


def test_client_sends_low_temperature_and_small_context(monkeypatch):
    seen = {}

    def fake_post(url, json=None, timeout=None):
        seen.update(url=url, body=json, timeout=timeout)
        return _Resp(payload={"message": {"content": "  hello  "}})

    monkeypatch.setattr(requests, "post", fake_post)
    out = OllamaClient(Settings()).generate("Q?", [{"question": "q", "answer": "a"}])
    assert out == "hello"
    assert seen["body"]["model"] == "llama3.2:3b" and seen["body"]["stream"] is False
    assert seen["body"]["options"]["temperature"] <= 0.2
    assert seen["body"]["options"]["num_ctx"] <= 4096 and seen["body"]["options"]["num_predict"] <= 400
    assert "CONTEXT" in seen["body"]["messages"][1]["content"]


def test_client_maps_http_errors(monkeypatch):
    from src.llm import OllamaBadResponse
    monkeypatch.setattr(requests, "post", lambda *a, **k: _Resp(404, text="model not found"))
    with pytest.raises(OllamaModelMissing):
        OllamaClient(Settings()).generate("q", [])
    monkeypatch.setattr(requests, "post", lambda *a, **k: _Resp(200, payload={"oops": 1}))
    with pytest.raises(OllamaBadResponse):
        OllamaClient(Settings()).generate("q", [])

    def timeout(*a, **k):
        raise requests.exceptions.Timeout("slow")
    monkeypatch.setattr(requests, "post", timeout)
    with pytest.raises(OllamaTimeout):
        OllamaClient(Settings()).generate("q", [])


def test_status_reports_missing_model(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp(payload={"models": [{"name": "mistral:7b"}]}))
    st = OllamaClient(Settings()).status()
    assert st.reachable and not st.model_ready and "ollama pull" in st.message
    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp(payload={"models": [{"name": "llama3.2:3b"}]}))
    assert OllamaClient(Settings()).status().ok


# ------------------------------------------------------------- documented limitations
@pytest.mark.xfail(reason="KNOWN LIMITATION: lexical TF-IDF cannot map the phrasal verb 'put on' to 'wear'", strict=True)
def test_known_limitation_phrasal_verb_paraphrase(retriever):
    assert retriever.search("What do practitioners put on when doing Silat?").is_relevant


# ------------------------------------------------------------- suggested questions
def test_every_suggested_question_is_answerable(retriever):
    sys.path.insert(0, str(ROOT / "app"))
    import ast
    src = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    lists = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") in ("SUGGESTIONS", "TOPICS"):
            lists[node.targets[0].id] = ast.literal_eval(node.value)
    questions = [q for _, q in lists["SUGGESTIONS"]] + [q for _, q in lists["TOPICS"]]
    assert len(questions) == 9
    for q in questions:
        assert retriever.search(q).is_relevant, q


# ------------------------------------------------------------- optional live test
@pytest.mark.skipif(os.getenv("RUN_OLLAMA_TESTS") != "1", reason="set RUN_OLLAMA_TESTS=1 with Ollama running")
def test_live_ollama_answers_in_english():
    bot = SilatGuideBot()
    assert bot.llm.status().ok, "Ollama/model not ready"
    r = bot.answer("What is Silat?")
    assert r.mode == cb.MODE_LLM and len(r.text) > 40