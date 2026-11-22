"""Shared helpers for SilatGuide: settings, text normalisation, safety filters.

Nothing in this module needs the network or a GPU, so it is safe to import anywhere
(including the unit tests).
"""
from __future__ import annotations

import html
import os
import re
from dataclasses import dataclass
from pathlib import Path

# --------------------------------------------------------------------------- paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_DIR / "data" / "silat_qa.csv"
ASSETS_DIR = ROOT_DIR / "app" / "assets"


# ------------------------------------------------------------------------ settings
def _load_dotenv(path: Path) -> None:
    """Tiny .env reader (so python-dotenv is not required). Existing env vars win."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    """Runtime configuration. Every value can be overridden in `.env`."""

    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    # Low temperature = consistent, fact-sticking answers.
    temperature: float = 0.1
    # Small context + short answers keep RAM use modest on a 16 GB laptop.
    num_ctx: int = 2048
    num_predict: int = 220
    timeout_seconds: int = 120
    keep_alive: str = "10m"
    # Retrieval
    top_k: int = 3
    similarity_threshold: float = 0.25
    dataset_path: str = str(DATA_PATH)

    @classmethod
    def from_env(cls) -> "Settings":
        def f(name: str, default, cast):
            raw = os.getenv(name)
            if raw is None or raw == "":
                return default
            try:
                return cast(raw)
            except ValueError:
                return default

        d = cls()
        return cls(
            ollama_host=f("OLLAMA_HOST", d.ollama_host, str).rstrip("/"),
            ollama_model=f("OLLAMA_MODEL", d.ollama_model, str),
            temperature=f("OLLAMA_TEMPERATURE", d.temperature, float),
            num_ctx=f("OLLAMA_NUM_CTX", d.num_ctx, int),
            num_predict=f("OLLAMA_NUM_PREDICT", d.num_predict, int),
            timeout_seconds=f("OLLAMA_TIMEOUT", d.timeout_seconds, int),
            keep_alive=f("OLLAMA_KEEP_ALIVE", d.keep_alive, str),
            top_k=f("TOP_K", d.top_k, int),
            similarity_threshold=f("SIMILARITY_THRESHOLD", d.similarity_threshold, float),
            dataset_path=f("DATASET_PATH", d.dataset_path, str),
        )


# --------------------------------------------------------------- fixed user messages
FALLBACK_MESSAGE = (
    "Sorry, I couldn't find enough reliable information to answer your question. "
    "Could you try rephrasing it?"
)
SAFETY_MESSAGE = (
    "I can't help with hurting, injuring or bullying anyone. Silat is a Malaysian cultural "
    "heritage built on discipline, respect and protecting others. If you would like to learn "
    "Silat, I'd be happy to talk about its values, its history or how beginners can start "
    "safely with a qualified instructor."
)
INJECTION_MESSAGE = (
    "I can't change my rules or share my internal instructions, but I'm happy to help with "
    "questions about Silat. Try asking about its history, styles, clothing or training safety."
)
GREETING_MESSAGE = (
    "Salam and hello! I'm SilatGuide, your friendly companion for learning about Malaysian "
    "Silat. Ask me about its history, styles, clothing, values or how to start training safely."
)
THANKS_MESSAGE = "You're most welcome! Feel free to ask me anything else about Silat."
EMPTY_MESSAGE = "Please type a question about Silat and I'll do my best to help."


# ------------------------------------------------------------- text normalisation
_SLANG = {
    "whats": "what is", "what's": "what is", "wats": "what is", "wat": "what", "wut": "what",
    "hw": "how", "u": "you", "ur": "your", "r": "are", "pls": "please", "plz": "please",
    "abt": "about", "wanna": "want to", "gonna": "going to", "gotta": "got to", "kinda": "kind of",
    "info": "information", "ppl": "people", "thx": "thanks", "ty": "thanks", "pls.": "please",
    "dont": "do not", "doesnt": "does not", "isnt": "is not", "cant": "can not",
    "hows": "how is", "wheres": "where is", "whos": "who is", "bg": "background",
}

STOPWORDS = frozenset(
    """
    a an the is are was were be been being am do does did done can could would should will shall may might
    i me my mine we us our you your yours he she it its they them their this that these those there here
    to of in on at for and or but nor so if as by from with into onto over under up down out off about
    what which who whom whose how why when where please tell explain give show me us any some lot lots
    just really very much many more most also too then than not no yes ok okay hey hi hello bot
    want know like need get got let go going come lol haha hehe btw pls plz thanks thank
    """.split()
)


def normalize_text(text: str) -> str:
    """Lower-case, expand common chat slang, strip punctuation, collapse spaces."""
    if not isinstance(text, str):
        return ""
    text = text.replace("\u2019", "'").replace("\u2018", "'").lower().strip()
    text = re.sub(r"[^a-z0-9'\s]", " ", text)
    words = []
    for w in text.split():
        words.append(_SLANG.get(w, w))
    text = " ".join(words)
    text = text.replace("'", "")
    return re.sub(r"\s+", " ", text).strip()


def stem(word: str) -> str:
    """Very small suffix stripper so 'styles'/'style' and 'learning'/'learn' match."""
    if len(word) <= 3:
        return word
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("ing") and len(word) > 5:
        return word[:-3]
    if word.endswith("ed") and len(word) > 4:
        return word[:-2]
    if word.endswith("es") and word[-3] in "sxz" or word.endswith(("ches", "shes")):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word


# Spelling-variant / synonym handling, applied identically to the dataset and to user queries.
_CANON = {
    "injured": "injury", "injuries": "injury", "injure": "injury", "injuring": "injury", "hurting": "hurt",
    "practise": "practice", "practised": "practice", "practising": "practice", "practicing": "practice",
    "practiced": "practice", "practices": "practice", "practitioners": "practitioner",
    "recognised": "recognition", "recognized": "recognition", "recognise": "recognition",
    "recognize": "recognition", "recognition": "recognition", "organization": "organisation",
    "organizations": "organisation", "organisations": "organisation", "safely": "safe", "safety": "safe",
    "clothes": "clothing", "dress": "clothing", "outfit": "clothing", "costume": "clothing",
    "uniform": "clothing", "attire": "clothing", "wearing": "wear", "worn": "wear",
    "kind": "type", "kinds": "type", "variety": "type", "varieties": "type", "category": "type",
    "origins": "origin", "originate": "origin", "originated": "origin", "began": "begin",
    "beginner": "beginner", "beginners": "beginner", "newbie": "beginner", "novice": "beginner",
    "dangerous": "danger", "risky": "risk", "risks": "risk", "riskier": "risk", "riskiest": "risk",
    "unsafe": "danger", "run": "organisation", "runs": "organisation", "manage": "organisation",
    "manages": "organisation", "govern": "organisation", "governs": "organisation",
    "oversee": "organisation", "oversees": "organisation", "federation": "organisation",
    "association": "organisation", "associations": "organisation", "bodies": "organisation",
    "tip": "guidance", "tips": "guidance", "advice": "guidance", "guideline": "guidance",
    "guidelines": "guidance", "precaution": "guidance", "precautions": "guidance",
    "fit": "health", "fitness": "health", "exercise": "health", "healthy": "health",
    "teacher": "guru", "instructor": "guru", "master": "guru", "coach": "guru", "teachers": "guru",
    "unesco": "unesco", "heritage": "heritage", "tradition": "traditional",
}
_EXPAND = {  # token -> extra tokens that carry the same meaning in the dataset's wording
    "old": ["history", "far", "back"], "age": ["history", "far", "back"], "ancient": ["history", "early"],
    "origin": ["come", "history"], "begin": ["come", "history"], "founded": ["history", "origin"],
    "wear": ["clothing"], "danger": ["injury", "risk"], "risk": ["injury"],
    "hurt": ["injury"], "style": ["type"], "type": ["style"],
}


def tokenize(text: str) -> list[str]:
    """Normalise -> canonicalise -> drop stop-words -> stem. Used by the TF-IDF vectorisers."""
    out: list[str] = []
    for w in normalize_text(text).split():
        w = _CANON.get(w, w)
        if w in STOPWORDS:
            continue
        s = stem(w)
        out.append(s)
        out.extend(_EXPAND.get(s, []))
    return out


def split_sources(source: str) -> list[str]:
    """The CSV `Source` column can hold several sources separated by '; '."""
    return [s.strip() for s in str(source).split(";") if s.strip()]


# ------------------------------------------------------------------ safety filters
_INJECTION_PATTERNS = [
    r"ignore (all |any |the |your |previous |prior |above )*(instructions|rules|prompt|guidelines)",
    r"disregard (all |any |the |your |previous |prior )*(instructions|rules|prompt|guidelines)",
    r"forget (all |your |the |previous )*(instructions|rules|prompt)",
    r"(reveal|show|print|repeat|display|tell me|leak) (me )?(your |the )?(system |hidden |secret |internal |initial )?(prompt|instructions|rules)",
    r"what (is|are) your (system |hidden |initial )?(prompt|instructions)",
    r"you are now\b", r"pretend (to be|you are|you're)", r"act as (if|an?|the)\b",
    r"developer mode", r"jailbreak", r"\bdan mode\b", r"override (your |the )?(safety|rules|instructions)",
    r"without (any )?(restrictions|rules|filters)",
]

_HARM_PATTERNS = [
    r"\b(kill|murder|stab|cripple|maim|torture)\b",
    r"\b(hurt|injure|harm|hit|punch|kick|strangle|choke|beat up|beat)\b.{0,25}\b(someone|somebody|people|person|him|her|them|my (friend|brother|sister|classmate|teacher|enemy)|a kid|kids)\b",
    r"\bhow (to|do i|can i)\b.{0,30}\b(break|snap|dislocate)\b.{0,20}\b(arm|leg|bone|bones|neck|finger|fingers|jaw|ribs?)\b",
    r"\bknock (him|her|them|someone|somebody|people)? ?out\b",
    r"\b(bully|bullying|revenge|get even)\b",
    r"\b(fight|attack|ambush|jump)\b.{0,20}\b(someone|somebody|people|a person|my enemy)\b",
    r"\b(deadly|deadliest|lethal|fatal|most dangerous)\b.{0,20}\b(move|moves|technique|techniques|strike|strikes|blow|attack)\b",
    r"\bhow to (win|start) a (street )?fight\b",
    r"\b(weapon|keris|knife|blade)\b.{0,30}\b(stab|cut|slash|kill|hurt|attack)\b",
]

_GREETING = re.compile(r"^(hi|hello|hey|hai|salam|assalamualaikum|good (morning|afternoon|evening)|yo)( there| silatguide| bot)?[!. ]*$")
_THANKS = re.compile(r"^(thanks|thank you|thank u|terima kasih|tq|thx|ty)( so much| a lot)?( silatguide)?[!. ]*$")


def is_prompt_injection(text: str) -> bool:
    t = normalize_text(text)
    return any(re.search(p, t) for p in _INJECTION_PATTERNS)


def is_harmful_request(text: str) -> bool:
    t = normalize_text(text)
    return any(re.search(p, t) for p in _HARM_PATTERNS)


def is_greeting(text: str) -> bool:
    return bool(_GREETING.match(normalize_text(text)))


def is_thanks(text: str) -> bool:
    return bool(_THANKS.match(normalize_text(text)))


# ------------------------------------------------------------------ HTML rendering
def render_basic_markdown(text: str) -> str:
    """Escape HTML, then support **bold**, *italic*, bullet lines and line breaks."""
    safe = html.escape(text or "")
    safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
    safe = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", safe)
    lines = []
    for line in safe.split("\n"):
        stripped = line.strip()
        if stripped.startswith(("- ", "\u2022 ")):
            lines.append("\u2022 " + stripped[2:])
        else:
            lines.append(line)
    return "<br>".join(lines)
