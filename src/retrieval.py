"""TF-IDF + cosine-similarity retrieval over the SilatGuide Q&A dataset.

Why this design (easy to explain in the presentation):
  * Word-level TF-IDF (1-2 grams, stop-words removed, light stemming) captures *meaning words*
    such as "history", "tengkolok" or "warm-up".
  * Each channel is computed twice: against the dataset *questions only* (so "What is Silat?"
    finds the entry that is literally about that) and against the *whole entry*
    (question + category + answer, so facts that only appear in answers are findable).
  * Character n-gram TF-IDF (3-5 chars) forgives spelling mistakes ("silatt", "tengkolk").
  * Query words that are not in the dataset vocabulary are spell-corrected when a close match
    exists (difflib), otherwise they count against the question's *coverage*.
  * A question is accepted only if (a) its blended similarity reaches the threshold AND
    (b) enough of its important words (IDF-weighted) are actually known to the dataset.
    This is what stops "How do I learn Python?" from getting a Silat answer.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .utils import normalize_text, tokenize

log = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["Question", "Answer", "Source", "Category"]
WORD_WEIGHT = 0.70
CHAR_WEIGHT = 0.30
DEFAULT_MIN_COVERAGE = 0.60


class DatasetError(Exception):
    """Raised when the CSV is missing, unreadable or lacks the required columns."""


@dataclass
class Match:
    index: int
    question: str
    answer: str
    source: str
    category: str
    score: float


@dataclass
class RetrievalResult:
    query: str
    normalized_query: str
    matches: list[Match] = field(default_factory=list)  # top-k, best first (always filled)
    threshold: float = 0.0
    coverage: float = 0.0          # share of the question's important words known to the dataset
    min_coverage: float = 0.0
    corrected_query: str = ""      # tokens after spell-correction (for transparency / debugging)

    @property
    def top_score(self) -> float:
        return self.matches[0].score if self.matches else 0.0

    @property
    def is_relevant(self) -> bool:
        return bool(self.matches) and self.top_score >= self.threshold and self.coverage >= self.min_coverage

    @property
    def relevant_matches(self) -> list[Match]:
        """Matches that are safe to pass to the LLM as context."""
        if not self.is_relevant:
            return []
        floor = max(self.threshold, 0.45 * self.top_score)
        return [m for m in self.matches if m.score >= floor]


def validate_dataset(df: pd.DataFrame) -> dict:
    """Return a report describing dataset problems (does not raise)."""
    report: dict = {
        "rows": int(len(df)),
        "missing_columns": [c for c in REQUIRED_COLUMNS if c not in df.columns],
        "empty_questions": [],
        "empty_answers": [],
        "empty_sources": [],
        "duplicate_questions": [],
        "categories": {},
    }
    if report["missing_columns"]:
        return report
    for i, row in df.iterrows():
        if not str(row["Question"]).strip():
            report["empty_questions"].append(int(i))
        if not str(row["Answer"]).strip():
            report["empty_answers"].append(int(i))
        if not str(row["Source"]).strip():
            report["empty_sources"].append(int(i))
    seen: dict[str, int] = {}
    for i, q in df["Question"].items():
        key = normalize_text(str(q))
        if not key:
            continue
        if key in seen:
            report["duplicate_questions"].append((seen[key], int(i)))
        else:
            seen[key] = int(i)
    report["categories"] = df["Category"].value_counts().to_dict()
    return report


def load_dataset(path: str | Path) -> tuple[pd.DataFrame, dict]:
    """Load + validate the CSV. Empty / duplicate rows are dropped (and reported)."""
    path = Path(path)
    if not path.exists():
        raise DatasetError(f"Dataset not found: {path}")
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")
    except Exception as exc:  # pragma: no cover - pandas raises many different errors
        raise DatasetError(f"Could not read dataset: {exc}") from exc

    df.columns = [c.strip() for c in df.columns]
    report = validate_dataset(df)
    if report["missing_columns"]:
        raise DatasetError(f"Dataset is missing required columns: {report['missing_columns']}")

    for col in REQUIRED_COLUMNS:
        df[col] = df[col].astype(str).str.strip()

    bad = set(report["empty_questions"]) | set(report["empty_answers"]) | {b for _, b in report["duplicate_questions"]}
    if bad:
        log.warning("Dropping %d invalid dataset rows: %s", len(bad), sorted(bad))
        df = df.drop(index=sorted(bad))
    df = df.reset_index(drop=True)
    if df.empty:
        raise DatasetError("Dataset has no usable rows.")
    return df, report


def _edit_distance(a: str, b: str) -> int:
    """Levenshtein distance (small strings only, so the simple DP is fine)."""
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


class SilatRetriever:
    """Index the dataset once, then answer `search()` calls quickly."""

    def __init__(
        self,
        csv_path: str | Path,
        threshold: float = 0.25,
        top_k: int = 3,
        min_coverage: float = DEFAULT_MIN_COVERAGE,
    ):
        self.threshold = float(threshold)
        self.top_k = int(top_k)
        self.min_coverage = float(min_coverage)
        self.df, self.report = load_dataset(csv_path)

        # Pre-tokenised documents. Questions are tripled inside the "full" doc so they weigh more
        # than the (much longer) answers.
        q_docs = [" ".join(tokenize(q)) for q in self.df["Question"]]
        # Category names form a third, small channel so topic-style queries ("silat history",
        # "clothing", "safety tips") also land on the right group of entries.
        c_docs = [" ".join(tokenize(c)) for c in self.df["Category"]]
        d_docs = [
            " ".join(tokenize(f"{q} {q} {q} {c} {a}"))
            for q, c, a in zip(self.df["Question"], self.df["Category"], self.df["Answer"])
        ]

        def word_vec() -> TfidfVectorizer:
            return TfidfVectorizer(tokenizer=str.split, token_pattern=None, lowercase=False,
                                   ngram_range=(1, 2), sublinear_tf=True)

        def char_vec() -> TfidfVectorizer:
            return TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)

        self._qw, self._dw, self._cw = word_vec(), word_vec(), word_vec()
        self._qc, self._dc = char_vec(), char_vec()
        self._qw_m = self._qw.fit_transform(q_docs)
        self._dw_m = self._dw.fit_transform(d_docs)
        self._cw_m = self._cw.fit_transform(c_docs)
        self._qc_m = self._qc.fit_transform(q_docs)
        self._dc_m = self._dc.fit_transform(d_docs)

        # Unigram vocabulary with IDF weights (used for spell-correction and the coverage gate).
        idf = dict(zip(self._dw.get_feature_names_out(), self._dw.idf_))
        self._idf = {t: v for t, v in idf.items() if " " not in t}
        self._max_idf = max(self._idf.values())
        self._vocab_list = sorted(self._idf)

    # ------------------------------------------------------------------ public API
    @property
    def size(self) -> int:
        return int(len(self.df))

    @property
    def categories(self) -> dict[str, int]:
        return self.df["Category"].value_counts().to_dict()

    def _correct(self, token: str) -> str:
        """Replace an unknown token by its closest dataset word (e.g. 'silatt' -> 'silat')."""
        if token in self._idf or len(token) < 5:
            return token
        # Typo fix by edit distance: 1 edit for short words, 2 for long ones, same first letter.
        # "silatt" -> "silat" and "unesko" -> "unesco" work, but "founder" is NOT turned into
        # the unrelated word "found" (2 edits on a 7-letter word).
        limit = 1 if len(token) <= 7 else 2
        best, best_d = token, limit + 1
        for v in self._vocab_list:
            if v[0] != token[0] or abs(len(v) - len(token)) > limit:
                continue
            d = _edit_distance(token, v)
            if d < best_d:
                best, best_d = v, d
        return best if best_d <= limit else token

    def _coverage(self, tokens: list[str]) -> float:
        """IDF-weighted share of query tokens that exist in the dataset vocabulary."""
        if not tokens:
            return 0.0
        total = known = 0.0
        for t in tokens:
            if t in self._idf:
                total += self._idf[t]
                known += self._idf[t]
            else:  # unknown word = informative but unanswerable -> count at maximum weight
                total += self._max_idf
        return known / total if total else 0.0

    def search(self, query: str, top_k: int | None = None) -> RetrievalResult:
        top_k = top_k or self.top_k
        result = RetrievalResult(
            query=query, normalized_query=normalize_text(query),
            threshold=self.threshold, min_coverage=self.min_coverage,
        )
        tokens = [self._correct(t) for t in tokenize(query)]
        if not tokens:
            return result  # nothing meaningful to search for -> no matches
        qstr = " ".join(tokens)
        result.corrected_query = qstr
        result.coverage = self._coverage(tokens)

        def cos(vec, mat):
            return cosine_similarity(vec.transform([qstr]), mat).ravel()

        word = 0.45 * cos(self._qw, self._qw_m) + 0.40 * cos(self._dw, self._dw_m) \
             + 0.15 * cos(self._cw, self._cw_m)
        char = 0.5 * cos(self._qc, self._qc_m) + 0.5 * cos(self._dc, self._dc_m)
        score = WORD_WEIGHT * word + CHAR_WEIGHT * char

        for i in np.argsort(-score)[:top_k]:
            row = self.df.iloc[int(i)]
            result.matches.append(
                Match(int(i), row["Question"], row["Answer"], row["Source"], row["Category"], float(score[i]))
            )
        return result
