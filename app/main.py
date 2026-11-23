"""SilatGuide - Streamlit front-end.   Run from the project root:  streamlit run app/main.py

Only the presentation layer lives here. The chatbot itself (safety routing -> TF-IDF retrieval ->
LLaMA 3.2 via Ollama) is untouched and lives in src/.
"""
from __future__ import annotations

import base64
import html
import re
import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.chatbot import MODE_DATASET, MODE_OUT_OF_SCOPE, BotResponse, SilatGuideBot  # noqa: E402
from src.utils import Settings, render_basic_markdown  # noqa: E402

APP_DIR = Path(__file__).resolve().parent
ASSETS = APP_DIR / "assets"

st.set_page_config(page_title="SilatGuide - Malaysian Silat Companion", page_icon="🥋",
                   layout="centered", initial_sidebar_state="auto")
