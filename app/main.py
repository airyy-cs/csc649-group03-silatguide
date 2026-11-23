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

# Welcome-screen suggestions. They are ordinary chat questions sent to the normal pipeline.
SUGGESTIONS = [
    ("🥋", "What is Silat?"),
    ("📜", "What is the history of Silat?"),
    ("🐅", "What are the different styles of Silat?"),
    ("🛡️", "What are the basic safety rules in Silat training?"),
]
# Sidebar topic shortcuts (also ordinary questions).
TOPICS = [
    ("History", "How far back can Silat be traced in Malay history?"),
    ("Styles", "What is Silat Harimau?"),
    ("Clothing", "What do Silat practitioners traditionally wear?"),
    ("Training safety", "Why is warming up important before Silat practice?"),
    ("Ethics", "Is Silat meant for hurting other people?"),
]

COPY_ICON = ("<svg viewBox='0 0 24 24' width='16' height='16' fill='none' stroke='currentColor' stroke-width='2' "
             "stroke-linecap='round' stroke-linejoin='round'><rect x='9' y='9' width='11' height='11' rx='2.5'/>"
             "<path d='M5 15V6.5A2.5 2.5 0 0 1 7.5 4H15'/></svg>")

# One tiny script, installed once into the page: (1) copy-to-clipboard for the copy icons,
# (2) keep the newest message in view. Streamlit cannot run JS inside st.markdown, hence the iframe.
PAGE_SCRIPT = """<script>
(function(){
  var w = window.parent, d = w.document;
  function fallback(t, done){
    var a = d.createElement('textarea'); a.value = t; a.style.cssText = 'position:fixed;opacity:0';
    d.body.appendChild(a); a.select();
    try { d.execCommand('copy'); done(); } catch(e) {}
    d.body.removeChild(a);
  }
  if (!w.__sgCopyInstalled) {
    w.__sgCopyInstalled = true;
    d.addEventListener('click', function(e){
      var b = e.target.closest && e.target.closest('.sg-copy'); if (!b) return;
      var box = b.closest('.sg-bubble'), node = box && box.querySelector('.sg-text'); if (!node) return;
      var text = node.innerText.trim();
      var done = function(){ b.classList.add('ok'); setTimeout(function(){ b.classList.remove('ok'); }, 1500); };
      if (w.navigator.clipboard && w.isSecureContext) {
        w.navigator.clipboard.writeText(text).then(done, function(){ fallback(text, done); });
      } else { fallback(text, done); }
    });
  }
  var msgs = d.querySelectorAll('.sg-msg');
  if (msgs.length) { msgs[msgs.length - 1].scrollIntoView({behavior: 'smooth', block: 'end'}); }
})();
</script><!-- messages:%d -->"""