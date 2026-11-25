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

# ------------------------------------------------------------------ cached resources
@st.cache_resource(show_spinner=False)
def get_bot() -> SilatGuideBot:
    return SilatGuideBot()


@st.cache_data(show_spinner=False)
def b64(path: str) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode()


@st.cache_data(ttl=10, show_spinner=False)
def ollama_status(_host: str, _model: str):
    return get_bot().llm.status()


def img_src(name: str, mime: str) -> str:
    p = ASSETS / name
    return f"data:{mime};base64,{b64(str(p))}" if p.exists() else ""


def inject_css() -> None:
    css = (APP_DIR / "styles.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# ------------------------------------------------------------------------- rendering
def _safe_url(url: str) -> str:
    return url if re.match(r"^https?://", url) else ""


def sources_html(sources: list[dict]) -> str:
    """Collapsible 'View Sources'. Shows only what is in the dataset's Source column."""
    seen: list[str] = []
    for s in sources:
        for ref in s.get("sources", []):
            if ref not in seen:
                seen.append(ref)
    items = []
    for ref in seen:
        if ref.startswith("Team-written"):
            # Guidance written by the team, not one published source: say so plainly.
            items.append("<li>Team-written beginner guidance (not a quotation from a single published source)</li>")
            continue
        name, sep, url = ref.partition(" - http")
        url = _safe_url("http" + url) if sep else ""
        label = html.escape(name.strip())
        items.append(f"<li><a href='{html.escape(url)}' target='_blank' rel='noopener noreferrer'>{label}</a></li>"
                     if url else f"<li>{label}</li>")
    if not items:
        return ""
    return f"<details class='sg-src'><summary>View Sources</summary><ul>{''.join(items)}</ul></details>"


def message_html(msg: dict, bot_av: str) -> str:
    if msg["role"] == "user":
        text = html.escape(msg["content"]).replace("\n", "<br>")
        return f"<div class='sg-msg user'><div class='sg-bubble'>{text}</div></div>"
    note = ""
    if msg.get("mode") == MODE_DATASET:  # friendly, non-technical honesty note
        note = ("<div class='sg-note'>The AI assistant is resting right now, so this answer comes "
                "straight from SilatGuide's saved information.</div>")
    copy_btn = f"<button class='sg-copy' type='button' title='Copy answer' aria-label='Copy answer'>{COPY_ICON}</button>"
    return (f"<div class='sg-msg bot'><img class='sg-av' src='{bot_av}' alt='SilatGuide'/>"
            f"<div class='sg-bubble'><div class='sg-text'>{render_basic_markdown(msg['content'])}</div>{note}"
            f"<div class='sg-foot'>{sources_html(msg.get('sources', []))}{copy_btn}</div></div></div>")


def loading_html(bot_av: str, gif: str) -> str:
    return (f"<div class='sg-msg bot'><img class='sg-av' src='{bot_av}' alt=''/>"
            f"<div class='sg-loading'><img src='{gif}' alt='Two tiny Silat friends sparring playfully'/>"
            f"<div><div class='t'>SilatGuide is preparing your answer...</div>"
            f"<div class='s'>Gathering what I know about Silat</div>"
            f"<div class='sg-dots'><span></span><span></span><span></span></div></div></div></div>")

def ask(q: str) -> None:
    st.session_state.pending = q
    st.rerun()


def render_sidebar(bot_av: str, s: Settings) -> None:
    with st.sidebar:
        st.markdown(
            f"<div class='sg-brand'><img src='{bot_av}' alt=''/><div><div class='ttl'>SilatGuide</div>"
            "<span>Malaysian Silat companion</span></div></div>"
            "<div class='sg-desc'>Your friendly guide to the art, history and traditions of Malaysian Silat.</div>",
            unsafe_allow_html=True)

        if st.button("🗑️  Clear conversation", key="clear", use_container_width=True):
            st.session_state.messages = []
            st.session_state.pending = None
            st.rerun()

        st.markdown("<div class='sg-h4'>Suggested topics</div>", unsafe_allow_html=True)
        for label, q in TOPICS:
            if st.button(label, key=f"topic_{label}", use_container_width=True):
                ask(q)

        stt = ollama_status(s.ollama_host, s.ollama_model)
        on = stt.ok
        title = "Connected" if on else ("Model not installed" if stt.reachable else "Offline")
        st.markdown(f"<div class='sg-conn' title='{title}'><span class='sg-dot {'on' if on else 'off'}'></span>"
                    f"{'Connected' if on else 'Offline'}</div>", unsafe_allow_html=True)

def render_welcome(bot_av: str) -> None:
    st.markdown(
        f"<div class='sg-hero'><img src='{bot_av}' alt='SilatGuide mascot'/><div class='txt'>"
        "<div class='sg-eyebrow'>Seni Silat · Warisan Malaysia</div>"
        "<h2>Welcome to SilatGuide</h2>"
        "<p>Discover the art, history, traditions and cultural heritage of Malaysian Silat.</p>"
        "</div></div><div class='sg-section'>✨ Try asking</div>", unsafe_allow_html=True)
    cols = st.columns(2)
    for i, (icon, q) in enumerate(SUGGESTIONS):
        if cols[i % 2].button(f"{icon}  {q}", key=f"sug_{i}", use_container_width=True):
            ask(q)

# ------------------------------------------------------------------------------ main
def main() -> None:
    inject_css()
    s = Settings.from_env()
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("pending", None)

    try:
        bot = get_bot()
    except Exception as exc:  # dataset missing/invalid -> clear error instead of a crash
        st.error(f"SilatGuide could not start: {exc}")
        st.stop()

    bot_av = img_src("chatbot_avatar.png", "image/png")
    gif = img_src("loading_silat.gif", "image/gif")
    render_sidebar(bot_av, s)

       typed = st.chat_input("Ask me anything about Silat...")
    question = typed or st.session_state.pending
    st.session_state.pending = None

    if not st.session_state.messages and not question:
        render_welcome(bot_av)
        return

    if question:
        st.session_state.messages.append({"role": "user", "content": question})

    st.markdown("<div class='sg-chat'>" + "".join(message_html(m, bot_av) for m in st.session_state.messages) + "</div>",
                unsafe_allow_html=True)

   if question:
        slot = st.empty()
        slot.markdown(loading_html(bot_av, gif), unsafe_allow_html=True)
        try:
            resp: BotResponse = bot.answer(question)
        except Exception:  # last-resort guard so the UI never crashes
            resp = BotResponse(text="Sorry, something went wrong while preparing your answer. Please try again.",
                               mode=MODE_OUT_OF_SCOPE)
        slot.empty()
        st.session_state.messages.append({
            "role": "assistant", "content": resp.text, "mode": resp.mode, "sources": resp.sources,
        })
        st.rerun()

    components.html(PAGE_SCRIPT % len(st.session_state.messages), height=0)


main()