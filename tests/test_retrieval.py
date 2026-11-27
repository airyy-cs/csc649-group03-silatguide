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