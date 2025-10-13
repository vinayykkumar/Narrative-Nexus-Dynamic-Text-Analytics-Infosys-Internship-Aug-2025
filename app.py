# app.py (restored + patched)
from unittest import result
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import uuid
import re
import time
import json
import datetime
import streamlit.components.v1 as components


# Keep only imports that are safe at module import time.
# Note: These imports assume you have a 'src' folder with these files.
# If they are in the same directory, you might need to adjust the import paths.
try:
    from src.inputHandler_fn import read_file
    from src.preprocessing import clean_text, summarize_text_stats
    from src.cleaners import clean_text
except ImportError:
    # Create dummy functions if 'src' is not available, allowing the app to run.
    st.warning("Could not import from 'src' directory. Using dummy functions.")
    def read_file(f): return {"text": f.getvalue().decode("utf-8"), "meta": {"source_type": "txt"}, "df_preview": None}
    def clean_text(t): return t
    def summarize_text_stats(t): return {"words": len(t.split()), "chars": len(t)}


# =============== GLOBAL SETTINGS ===============
# Flip this to True if you ALWAYS want refresh to land on Home (even if ?page exists)
ALWAYS_DEFAULT_HOME_ON_REFRESH = False

# --- Scoped CTA styles (kept; only affects buttons inside .cta-area) ---
st.markdown("""
<style>
/* only buttons inside .cta-area are green */
.cta-area .stButton>button {
  background:#50e3a4; color:#0b1f18; border:none; border-radius:12px;
  padding:12px 16px; font-weight:800; box-shadow:0 6px 16px rgba(0,0,0,.25);
}
.cta-area .stButton>button:hover { filter: brightness(1.03); }
</style>
""", unsafe_allow_html=True)



# ---------- DEBUG-FRIENDLY CLEANERS & DOC BUILDERS ---------
def _flatten_pdf_text__dbg(t: str) -> str:
    """Flatten PDF-like text: remove hyphen breaks, collapse newlines."""
    if not t:
        return ""
    # de-hyphenate across line breaks (word-)
    t = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", t)
    # collapse multiple newlines into spaces
    t = re.sub(r"[ \t]*\n+[ \t]*", " ", t)
    return t

_CLEAN_PAT__dbg = re.compile(r"""(?ix)
 (https?://\S+) | www\.\S+ | issn[:\s]\s*\d[\d\-xX]+ | ©\s*\d{4}.*
 |\bvolume\b.*\bissue\b.* | ^\s*page\s*\d+\s*$ | ^\s*international\s+journal.*$
""", re.MULTILINE)

def clean_for_summary__dbg(text: str) -> str:
    """Lenient cleaning (keep more text for summarizer)."""
    if not text:
        return ""
    text = _flatten_pdf_text__dbg(text)
    text = _CLEAN_PAT__dbg.sub(" ", text)
    lines = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        # keep uppercase headers (don’t drop aggressively)
        lines.append(s)
    text = " ".join(lines)
    return re.sub(r"\s{2,}", " ", text).strip()

_SENT_SPLIT__dbg = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9])')

def split_sentences__dbg(text: str) -> list[str]:
    """Split into sentences with a crude fallback."""
    if not text:
        return []
    parts = _SENT_SPLIT__dbg.split(text.strip())
    sents = [s.strip() for s in parts if len(s.strip()) >= 6]
    if len(sents) < 3:
        crude = [x.strip() for x in re.split(r"[.!?]+", text) if len(x.strip()) >= 6]
        if len(crude) > len(sents):
            sents = crude
    return sents

def ensure_docs__dbg(min_docs: int = 1, words_per_doc: int = 200) -> list[str]:
    """Chunk cleaned_text/raw_text into pseudo-docs for modeling/summarization."""
    text = st.session_state.get("cleaned_text") or st.session_state.get("raw_text") or ""
    docs = st.session_state.get("docs", [])

    def _chunk_by_words(t: str, chunk_size=200, overlap=40):
        words = t.split()
        if not words:
            return []
        step = max(1, chunk_size - overlap)
        out = []
        for i in range(0, len(words), step):
            chunk = " ".join(words[i:i+chunk_size])
            if chunk.strip():
                out.append(chunk)
            if i + chunk_size >= len(words):
                break
        return out

    if not docs:
        try:
            from src.topic_modeling import make_docs_from_text
            docs = make_docs_from_text(text, words_per_doc=words_per_doc)
        except Exception:
            docs = []
        if len(docs) < min_docs:
            docs = _chunk_by_words(text, chunk_size=words_per_doc, overlap=40)

    st.session_state["docs"] = docs
    return docs


# Tiny post-processor
def _postprocess_summary(s: str) -> str:
    import re, unicodedata

    if not s:
        return s

    # --- Normalize unicode & spaces ---
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", " ", s).strip()

    # --- Remove residual journal/news boilerplate (publisher-agnostic) ---
    s = re.sub(r"(?i)\bInternational Journal\b[^.]*", " ", s)
    s = re.sub(r"(?i)\bVolume\b[^.]{0,120}\bIssue\b[^.]*", " ", s)
    s = re.sub(r"(?i)\bISSN[:\s]*\d[\dxX\-]+\b", " ", s)
    s = re.sub(r"(?i)\bISBN[:\s]*(97[89][-\s]?)?\d[\d\-\s]+\b", " ", s)
    s = re.sub(r"(?i)\b10\.\d{4,9}/\S+\b", " ", s)      # DOI
    s = re.sub(r"(?i)\bIJRTI\d+\b", " ", s)
    s = re.sub(r"(?i)\bpage\s*\d+\b", " ", s)

    # --- Kill duplicated words/phrases ---
    s = re.sub(r"\b(\w+)\s+\1\b", r"\1", s, flags=re.I)            # "diagnosis diagnosis"
    s = re.sub(r"\b(\w+\s+\w+)\s+\1\b", r"\1", s, flags=re.I)      # "have the have the"
    s = re.sub(r"(?:\s*\.\s*){2,}", ". ", s)                        # ".. .." -> ". "
    s = re.sub(r"\s+\.", ".", s)

    # --- Light grammar and fluency fixes (safe, generic rewrites) ---
    fixes = [
        (r"(?i)\bcan\s+solve\s+complex\s+problems\s+with\s+efficient\s+way\b", "can solve complex problems efficiently"),
        (r"(?i)\bmaking\s+our\s+daily\s+life\s+more\s+comfortable\s+and\s+fast\b", "improving daily life"),
        (r"(?i)\btoday\s+society\b", "today’s society"),
        (r"(?i)\bfor\s+today\s+time\b", "today"),
        (r"(?i)\bwill\s+be\s+invented\b", "may emerge"),
        (r"(?i)\bnew\s+means\s+cyber\s+attack\b", "new forms of cyberattack"),
        (r"(?i)\bbetter\s+diagnoses?\s+and\s+faster\s+diagnosis\b", "faster and more accurate diagnoses"),
        (r"(?i)\bredefining\s+how\s+must\s+think\b", "redefining how we must think"),
        (r"(?i)\bis\s+becoming\s+more\s+advantageous\b", "is becoming more advantageous"),
        (r"(?i)\bthe\s+application\s+of\s+Artificial\s+Intelligence\b", "the application of artificial intelligence"),
    ]
    for pat, rep in fixes:
        s = re.sub(pat, rep, s)

    # --- Sentence boundary cleanup: split long fragments, ensure capitalization ---
    # Split on period/question/exclamation keeping delimiter
    parts = re.split(r'([.!?])', s)
    # Rebuild sentences, trim, capitalize starts
    sentences = []
    buf = ""
    for i in range(0, len(parts), 2):
        seg = parts[i].strip()
        end = parts[i+1] if i+1 < len(parts) else "."
        if not seg:
            continue
        # Capitalize first letter if sentence starts lowercase
        seg = seg[0].upper() + seg[1:] if seg and seg[0].islower() else seg
        sentences.append(seg + (end if end.strip() else "."))
    s = " ".join(sentences)

    # --- Final tidy ---
    s = re.sub(r"\s{2,}", " ", s).strip()
    # Remove any leftover leading 'Abstract' marker if it floated in
    s = re.sub(r"(?i)^abstract\s*[:.]?\s*", "", s)

    return s

    

# =============== PDF-safe normalization & lenient cleaner (PATCH) ===============
_HARD_BREAKS = re.compile(r"\r\n|\r|\n")
_SOFT_HYPHEN_WRAP = re.compile(r"(\w)-\s+(\w)")
_INLINE_MULTI_SPACE = re.compile(r"[ \t]{2,}")
_CTRL = re.compile(r"[\u0000-\u0008\u000B\u000C\u000E-\u001F]")



_URL = re.compile(r"(https?://\S+|www\.\S+)")
_ISSN = re.compile(r"\bISSN[:\s]*\d[\d\-xX]+\b", re.IGNORECASE)
_COPY = re.compile(r"©\s*\d{4}.*", re.IGNORECASE)
_MULTI_SPACE = re.compile(r"\s{2,}")



# ---------- universal doc builders ----------
def _chunk_by_words(text: str, chunk_size: int = 200, overlap: int = 40):
    words = text.split()
    if not words:
        return []
    out = []
    step = chunk_size - overlap if (chunk_size - overlap) > 0 else chunk_size
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            out.append(chunk)
        if i + chunk_size >= len(words):
            break
    return out

def ensure_docs(min_docs: int = 1, words_per_doc: int = 200):
    """Create st.session_state['docs'] from cleaned_text or raw_text if missing/empty."""
    text = st.session_state.get("cleaned_text") or st.session_state.get("raw_text") or ""
    docs = st.session_state.get("docs", [])

    if not docs:
        try:
            # use your existing chunker from src
            from src.topic_modeling import make_docs_from_text
            docs = make_docs_from_text(text, words_per_doc=words_per_doc)
        except Exception:
            docs = []

        if len(docs) < min_docs:
            docs = _chunk_by_words(text, chunk_size=words_per_doc, overlap=40)

    st.session_state["docs"] = docs
    return docs


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NarrativeNexus AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Force all anchors to open in the SAME TAB
st.markdown('<base target="_self">', unsafe_allow_html=True)

# ---------------- PAGES ----------------
PAGES = [
    "Home", "Data Input", "Preprocessing", "Topic Modeling",
    "Sentiment", "Summarization", "Dashboard", "About"
]

# ---------------- NAV HELPERS ----------------
def _set_page(page_name: str, update_query=True):
    """Set the current page and (optionally) sync the URL query param."""
    st.session_state["page"] = page_name
    if update_query:
        try:
            st.query_params.update(page=page_name.replace(" ", "_"))
        except Exception:
            pass

def nav_to(page_name: str, *, in_callback: bool = False):
    """Programmatic navigation; use in_callback=True inside widget callbacks."""
    _set_page(page_name, update_query=True)
    if not in_callback:
        st.rerun()  # outside callbacks only

def _get_url_page_param():
    """Return page from URL or None (new/old Streamlit compatible)."""
    try:
        vals = st.query_params.get_all("page")
        if vals:
            return vals[0].replace("_", " ")
    except Exception:
        pass
    try:
        if 'page' in st.query_params:
            v = st.query_params['page']
            if isinstance(v, (list, tuple)):
                v = v[0]
            return str(v).replace("_", " ")
    except Exception:
        pass
    return None

def sync_url_to_state():
    """Keep st.session_state['page'] aligned with the current URL."""
    url_page = _get_url_page_param()
    if ALWAYS_DEFAULT_HOME_ON_REFRESH:
        url_page = None
        try:
            st.query_params.clear()
        except Exception:
            pass
    if url_page and url_page in PAGES and st.session_state.get("page") != url_page:
        st.session_state["page"] = url_page

def init_page():
    """Initialize session_state['page'] if not present."""
    if "page" not in st.session_state:
        url_page = _get_url_page_param()
        if ALWAYS_DEFAULT_HOME_ON_REFRESH:
            url_page = None
        st.session_state["page"] = url_page if (url_page in PAGES) else "Home"

# ---------------- STYLES (Consolidated and Patched) ----------------
# I've combined all your custom styles into this one block for easier management.
HOME_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    :root {
        --bg: #0e1117;
        --fg: #eaf2f6;
        --muted: #9fb1bd;
        --brand: #50e3a4;
        --brand-ink: #0b1f18;
        --glass: rgba(255, 255, 255, 0.06);
        --border: rgba(255, 255, 255, 0.12);
        --font-family: 'Inter', sans-serif;
    }

    html, body, .stApp { background: var(--bg); color: var(--fg); font-family: var(--font-family); }
    /* Hide default Streamlit chrome */
    .st-emotion-cache-18ni7ap, .st-emotion-cache-h4xjwg, .st-emotion-cache-ltfnpr { display: none !important; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .main-content-wrapper { max-width: 1200px; margin: 0 auto; padding: 0 18px; }

    /* -------- NAVBAR -------- */
    .nn-nav {
        position: sticky; top: 0; z-index: 1000;
        background: rgba(14,17,23,.92);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid var(--border);
    }
    .nn-nav-inner {
        max-width: 1200px; margin: 0 auto; padding: 12px 16px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .nn-logo { font-weight: 800; font-size: 20px; color: #eaf7f0 !important; white-space: nowrap; cursor: pointer; }
    .nn-logo small { color: var(--muted); margin-left: 6px; font-weight: 600; font-size: 0.8em; }

    .nn-links { display: flex; gap: 18px; align-items: center; }
    .nn-nav a, .nn-links a, .nn-cta a { text-decoration: none !important; }
    .nn-link {
        color: var(--fg) !important; text-decoration: none !important;
        font-weight: 600; font-size: 14px; padding: 8px 10px; border-radius: 6px;
        transition: background .15s ease, color .15s ease; cursor: pointer;
    }
    .nn-link:hover { background: var(--glass); }
    .nn-link.active { background: rgba(255,255,255,.10); color: #fff !important; }

    .nn-cta .nn-login {
        background: var(--brand); color: var(--brand-ink) !important;
        padding: 8px 16px; border-radius: 999px; font-weight: 800; display: inline-block; cursor: pointer;
    }
    .nn-cta .nn-login:hover { filter: brightness(1.08); }

    /* -------- HERO -------- */
    .hero-center { padding: 80px 0 24px; text-align: center; }
    .hero-center h1 {
        margin: 0; font-size: 58px; line-height: 1.1; letter-spacing: -1.5px; font-weight: 800;
        background: linear-gradient(90deg, #f6fff9, #defbe9); -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; background-clip: text;
    }
    .hero-center p { margin: 16px auto 0; max-width: 720px; color: var(--muted); font-size: 18px; line-height: 1.6; }

    /* PATCH: Correctly style and center the main hero button */
    /* Target the container Streamlit generates for any button to center it */
    div[data-testid="stButton"] {
        display: flex;
        justify-content: center;
    }
    
    /* We use a unique ID on an empty div as a "hook" to target ONLY the hero button */
    /* This rule targets the button container that is the *next sibling* of our hook */
    #hero-button-container + div[data-testid="stButton"] {
    display: flex;
    justify-content: center;
    width: 100%;
    margin: 30px 0 64px; /* Vertical spacing */
}

/* Use the hook to style the button element itself with gradients, fonts, etc. */
#hero-button-container + div[data-testid="stButton"] > button {
    background: linear-gradient(90deg, #50e3a4, #2fc48d) !important;
    color: #0b1f18 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 32px !important;
    font-weight: 800 !important;
    font-size: 18px !important;
    box-shadow: 0 8px 24px rgba(80,227,164,0.25) !important;
    transition: transform .2s, box-shadow .2s !important;
}

/* Hover effect for the specific hero button */
#hero-button-container + div[data-testid="stButton"] > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 30px rgba(80,227,164,0.35);
    filter: brightness(1.05);
}
    /* END PATCH */

    /* -------- MEDIA -------- */
    .media-section { padding: 32px 0 24px; }
    .media-frame {
        width: 100%; max-width: 900px; margin: 0 auto; aspect-ratio: 16/9; border-radius: 20px; overflow: hidden;
        border: 1px solid var(--border); box-shadow: 0 16px 40px rgba(0,0,0,.35);
    }

    /* -------- SECTIONS -------- */
    .section { padding: 96px 0; }
    .section-header { text-align: center; margin-bottom: 48px; }
    .section-kicker { color: var(--brand); font-weight: 700; letter-spacing: .12em; text-transform: uppercase; font-size: 12px; }
    .section-title { font-size: 36px; font-weight: 700; margin: 8px 0 0; line-height: 1.2; }
    .section-subtitle { color: var(--muted); max-width: 700px; margin: 16px auto 0; text-align: center; }

    /* -------- WHY -------- */
    .why-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; }
    .why-card { background: var(--glass); border: 1px solid var(--border); border-radius: 16px; padding: 24px; transition: background .2s, transform .2s; height: 100%; }
    .why-card:hover { background: rgba(255,255,255,.08); transform: translateY(-4px); }
    .why-card .icon { font-size: 32px; margin-bottom: 16px; color: var(--brand); }
    .why-card h4 { margin: 0 0 8px; color: #dffcea; font-size: 20px; font-weight: 600; }
    .why-card p { margin: 0; color: var(--muted); font-size: 15px; line-height: 1.5; }

    /* -------- CORE FUNCTIONS -------- */
    .core-fn-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
    .core-fn-card { background: #12161E; border: 1px solid var(--border); border-radius: 12px; padding: 20px; }
    .core-fn-card h4 { margin: 0 0 8px; font-size: 16px; font-weight: 600; }
    .core-fn-card p { margin: 0; font-size: 14px; color: var(--muted); line-height: 1.45; }

    /* -------- PRICING -------- */
    .pricing-card {
        border: 1px solid var(--border); border-radius: 16px; padding: 32px; text-align: center;
        display: flex; flex-direction: column; height: 100%; background: #10141B;
    }
    .pricing-card.highlight { border-color: var(--brand); box-shadow: 0 0 30px rgba(80,227,164,.15); }
    .pricing-card h3 { font-size: 20px; margin:0 0 8px; }
    .pricing-card .price { font-size: 42px; font-weight: 700; margin:0 0 8px; }
    .pricing-card .price span { font-size: 16px; color: var(--muted); font-weight: 400; }
    .pricing-card ul { list-style: none; padding: 0; margin: 24px 0; text-align: left; }
    .pricing-card ul li { margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
    .pricing-card ul li::before { content: '✓'; color: var(--brand); }
    .pricing-btn {
        display: inline-block; margin-top: auto; padding: 12px 18px; border-radius: 999px;
        background: transparent; border: 1px solid var(--border); color: var(--fg) !important;
        font-weight: 700; text-decoration: none !important; transition: background .2s, transform .2s, border-color .2s; cursor: pointer;
    }
    .pricing-btn:hover { background: var(--glass); transform: translateY(-1px); border-color: rgba(255,255,255,.35); }

    /* -------- FOOTER -------- */
    .footer { border-top: 1px solid var(--border); padding: 32px 0; margin-top: 64px; text-align: center; color: var(--muted); font-size: 14px; }

    /* Avoid blue default links anywhere inside main wrappers */
    .main-content-wrapper a { color: var(--fg) !important; text-decoration: none !important; }
</style>
"""

# ---------------- RENDER NAVBAR ----------------
def render_navbar():
    st.markdown(HOME_CSS, unsafe_allow_html=True)
    current_page = st.session_state.get("page", "Home")

    # Build anchor links with explicit target="_self"
    links_html = []
    for p in PAGES:
        active = "active" if p == current_page else ""
        href = f"?page={p.replace(' ', '_')}"
        links_html.append(f'<a class="nn-link {active}" href="{href}" target="_self">{p}</a>')
    links = "\n".join(links_html)

    nav_html = f"""
    <div class="nn-nav">
      <div class="nn-nav-inner">
        <a class="nn-logo" href="?page=Home" target="_self">NarrativeNexus <small>AI</small></a>
        <div class="nn-links">{links}</div>
        <div class="nn-cta">
          <a class="nn-login" href="?page=Data_Input" target="_self">Login</a>
        </div>
      </div>
    </div>
    """
    st.markdown(nav_html, unsafe_allow_html=True)

# ---------------- HOME PAGE (Patched Button) ----------------
def page_home():
    # --- HERO ---
    st.markdown("""
        <div class="main-content-wrapper">
            <div class="hero-center">
                <h1>NarrativeNexus &mdash; AI Text Analysis for Real Decisions</h1>
                <p>Upload documents, clean text, discover topics, summarize key ideas, and surface sentiment-driven actions — all in one minimal, powerful workspace.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- CENTERED CALL-TO-ACTION BUTTON (PATCH) ---
    # We use an empty div with a unique ID as a "hook" for our CSS selector.
    # The CSS targets the Streamlit button container that *immediately follows* this hook,
    # ensuring only this specific button is styled and centered.
    st.markdown('<div id="hero-button-container"></div>', unsafe_allow_html=True)
    st.button("🚀 Get Started Now", key="hero_get_started",
              on_click=lambda: nav_to("Data Input", in_callback=True))

    # --- VIDEO ---
    st.markdown("""
        <div class="main-content-wrapper">
            <div class="media-section">
                <div class="media-frame">
                    <iframe width="100%" height="100%"
                        src="https://www.youtube.com/embed/TXSOitGoINE"
                        title="YouTube video player" frameborder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen>
                    </iframe>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- WHY NARRATIVENEXUS ---
    st.markdown("""
        <div class="main-content-wrapper">
            <section class="section">
                <div class="section-header">
                    <div class="section-kicker">Why NarrativeNexus</div>
                    <h2 class="section-title">From Raw Text to Decisions in Minutes</h2>
                    <p class="section-subtitle">We've engineered a workflow that eliminates complexity and surfaces insights faster than any other tool on the market.</p>
                </div>
                <div class="why-grid">
                    <div class="why-card">
                        <div class="icon">⚙️</div>
                        <h4>One Streamlined Flow</h4>
                        <p>Input → preprocess → topics → sentiment → summarize → dashboard. Opinionated defaults give you great results without endless fiddling.</p>
                    </div>
                    <div class="why-card">
                        <div class="icon">🎯</div>
                        <h4>Signal Over Noise</h4>
                        <p>Topic-aware sentiment + MMR-guided extractive summaries, polished with DistilBART, keep the narrative tight and actionable.</p>
                    </div>
                    <div class="why-card">
                        <div class="icon">📈</div>
                        <h4>Report & Act</h4>
                        <p>Export executive HTML reports with KPIs, risks, opportunities, and rule-based recommendations powered by topic × sentiment.</p>
                    </div>
                </div>
            </section>
        </div>
    """, unsafe_allow_html=True)

    # --- CORE FUNCTIONS ---
    st.markdown("""
        <div class="main-content-wrapper">
            <section class="section">
                <div class="section-header">
                    <div class="section-kicker">Our Toolkit</div>
                    <h2 class="section-title">All Your Text Analysis Tools in One Place</h2>
                </div>
                <div class="core-fn-grid">
                    <div class="core-fn-card"><h4>📄 Data Input</h4><p>Upload TXT, DOCX, CSV, or paste text. Smart preview and validation.</p></div>
                    <div class="core-fn-card"><h4>🧹 Preprocessing</h4><p>Lowercasing, noise removal, stopwords, lemmatization, n-grams.</p></div>
                    <div class="core-fn-card"><h4>📊 Topic Modeling</h4><p>NMF / LDA with coherence, perplexity, diversity & silhouette.</p></div>
                    <div class="core-fn-card"><h4>💬 Sentiment</h4><p>VADER (fast) or RoBERTa (accurate). Overall + per-topic views.</p></div>
                    <div class="core-fn-card"><h4>🧾 Summarization</h4><p>MMR extractive + DistilBART polish. Doc-level & topic-level.</p></div>
                    <div class="core-fn-card"><h4>📈 Dashboard</h4><p>KPIs, word cloud, topic distribution, and live recommendations.</p></div>
                    <div class="core-fn-card"><h4>🧭 Recommendations</h4><p>Rule-based actions from sentiment × topic risk scoring.</p></div>
                    <div class="core-fn-card"><h4>📥 Reporting</h4><p>Executive HTML report with visuals, risks & opportunities.</p></div>
                </div>
            </section>
        </div>
    """, unsafe_allow_html=True)

    # --- PRICING ---
    st.markdown("""
        <div class="main-content-wrapper">
            <section class="section" id="pricing">
                <div class="section-header">
                    <div class="section-kicker">Pricing</div>
                    <h2 class="section-title">Simple, Transparent Plans</h2>
                </div>
            </section>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="main-content-wrapper">
      <div class="why-grid">
        <div class="pricing-card">
            <h3>Starter</h3>
            <div class="price">$0<span>/mo</span></div>
            <p>For individuals and small projects.</p>
            <ul>
                <li>Up to 50 documents/month</li>
                <li>Basic preprocessing</li>
                <li>Standard topic modeling</li>
                <li>Community support</li>
            </ul>
            <a class="pricing-btn" href="?page=Data_Input" target="_self">Get started</a>
        </div>
        <div class="pricing-card highlight">
            <h3>Pro</h3>
            <div class="price">$49<span>/mo</span></div>
            <p>For professionals and growing teams.</p>
            <ul>
                <li>Up to 1,000 documents/month</li>
                <li>Advanced preprocessing</li>
                <li>RoBERTa sentiment analysis</li>
                <li>Priority email support</li>
            </ul>
            <a class="pricing-btn" href="?page=Data_Input" target="_self">Upgrade to Pro</a>
        </div>
        <div class="pricing-card">
            <h3>Enterprise</h3>
            <div class="price">Custom</div>
            <p>For large-scale, custom deployments.</p>
            <ul>
                <li>Unlimited documents</li>
                <li>On-premise option</li>
                <li>Custom models & integrations</li>
                <li>Dedicated 24/7 support</li>
            </ul>
            <a class="pricing-btn" href="?page=About" target="_self">Contact sales</a>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    

# --- Data Input ---
def page_data_input():
    st.title("📄 Step 1: Data Input")
    st.caption("Upload a file or paste text. We’ll validate and show an instant preview before preprocessing.")

    col_main, col_side = st.columns([1.8, 1])
    with col_main:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3>Choose your input <span class='pill'>TXT / CSV / DOCX / PDF / Paste</span></h3>", unsafe_allow_html=True)
        tabs = st.tabs(["📤 Upload file", "📝 Paste text"])
        uploaded = None
        pasted_text = ""
        with tabs[0]:
            uploaded = st.file_uploader(" ", type=["txt", "csv", "docx", "pdf"], key="file_up", label_visibility="collapsed")
        with tabs[1]:
            pasted_text = st.text_area("Paste your text here", height=200, key="paste_text")
        st.markdown("</div>", unsafe_allow_html=True)

        preview_text = ""
        df_preview = None
        source_type = None

        if pasted_text and pasted_text.strip():
            preview_text = pasted_text.strip()
            source_type = "pasted"
        elif uploaded is not None:
            try:
                with st.spinner("Reading file…"):
                    data = read_file(uploaded)
                preview_text = data["text"] or ""
                df_preview = data.get("df_preview")
                source_type = data["meta"]["source_type"]
                
                st.session_state["pages"] = data.get("pages")
            except Exception as e:
                st.error(f"Failed to read file: {e}")

        # PATCH: normalize PDF-ish content right here
        
        if preview_text:
            import unicodedata
            preview_text = unicodedata.normalize("NFKC", preview_text)
            preview_text = preview_text.replace("\u00A0", " ")  # NBSP -> space

        if preview_text or df_preview is not None:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h3>Quick Preview</h3>", unsafe_allow_html=True)
            if df_preview is not None:
                with st.expander("🔎 CSV rows (sample)"):
                    st.dataframe(df_preview, use_container_width=True)
            if preview_text:
                st.markdown("<div class='preview'>", unsafe_allow_html=True)
                st.text(preview_text[:800] + ("..." if len(preview_text) > 800 else ""))
                st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='btn-primary' style='max-width:320px; margin:18px auto 0;'>", unsafe_allow_html=True)
        if st.button("🚀 Go Ahead", key="btn_data_goahead", use_container_width=True):
            if preview_text:
                # === ADD DEBUG HERE ===
                st.write(f"📝 Storing {len(preview_text)} chars to session state...")
                st.write(f"First 100 chars: {preview_text[:100]}")

                st.session_state["raw_text"] = preview_text
                st.session_state["uploaded_file_name"] = uploaded.name if uploaded else "pasted_text"
                st.session_state["df_preview"] = df_preview
                st.session_state["source_type"] = source_type or "pasted"

                # === CRITICAL: Clear old processed data ===
                for key in ["cleaned_text", "docs", "final_summary", "topic_summaries", "sentiment_results"]:
                    st.session_state.pop(key, None)

                # Build docs now so downstream pages always have something
                ensure_docs(min_docs=1, words_per_doc=200)

                nav_to("Preprocessing")
            else:
                st.warning("Please upload a file or paste some text first.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_side:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3>Tips & Requirements</h3>", unsafe_allow_html=True)
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <ul class='muted'>
              <li>CSV: include at least one text-like column (e.g., <i>text, content, body</i>).</li>
              <li>Large CSVs: we preview ~800 rows to keep things fast.</li>
              <li>DOCX support requires <code>python-docx</code> (already in requirements).</li>
            </ul>
            """,
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)


# --- Preprocessing ---
def page_preprocessing():
    st.title("🧹 Step 2: Preprocessing")
    
    raw_text = st.session_state.get("raw_text", "")
    if not raw_text:
        st.warning("⚠️ Please upload text first.")
        return
    
    st.subheader("📌 Original")
    st.text_area("Original", raw_text[:1000], height=150, key="prep_original")
    
    # Simple cleaning for preprocessing (don't use the new clean_text here)
    import re
    import unicodedata
    
    cleaned = raw_text[:120_000]
    
    # Basic normalization only
    cleaned = unicodedata.normalize("NFKC", cleaned)
    cleaned = re.sub(r"©\s*\d{4}[^\n]{0,100}", " ", cleaned)
    cleaned = re.sub(r"\bISSN[:\s]*\d[\dxX\-]+", " ", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    
    st.session_state["cleaned_text"] = cleaned
    
    st.subheader("🧽 Cleaned")
    st.text_area("Cleaned", cleaned[:1000], height=150, key="prep_cleaned")
    
    stats = summarize_text_stats(cleaned)
    st.dataframe(pd.DataFrame([stats]), use_container_width=True)
    
    ensure_docs(min_docs=1, words_per_doc=200)
    
    if st.button("➡️ Next: Topic Modeling", use_container_width=True):
        nav_to("Topic Modeling")
                

# --- Topic Modeling ---
def page_topics():
    try:
        from src.topic_modeling import (
            make_docs_from_text, vectorize_tfidf, vectorize_count, safe_array,
            fit_nmf, fit_lda, top_terms_per_topic, doc_topic_distribution, save_artifacts,
            compute_coherence_score, compute_model_perplexity, topic_diversity, topic_silhouette_score
        )
    except Exception as e:
        st.error(f"Topic-modeling helpers unavailable: {e}")
        return

    st.title("📊 Topic Modeling")
    docs = st.session_state.get("docs", [])

    # Skip if too small
    if len(docs) < 15:
        st.warning(
            f"Only {len(docs)} documents detected — skipping Topic Modeling. "
            "We’ll still run summarization & sentiment directly on the document(s)."
        )
        st.session_state["skip_topic_modeling"] = True
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            if st.button("➡️ Next: Sentiment Analysis", key="btn_skip_to_sentiment", use_container_width=True):
                nav_to("Sentiment")
        with c3:
            if st.button("🧾 Go to Summarization", key="btn_skip_to_summarization", use_container_width=True):
                nav_to("Summarization")
        return
    else:
        st.session_state["skip_topic_modeling"] = False

    if "raw_text" not in st.session_state or not st.session_state["raw_text"]:
        st.warning("Please go to **Data Input** and add some text first.")
        return

    cleaned_text = st.session_state.get("cleaned_text", None)
    if not cleaned_text:
        with st.spinner("Cleaning text (quick pass)…"):
            cleaned_text = clean_text(st.session_state["raw_text"][:200_000])

    with st.expander("⚙️ Modeling Settings", expanded=True):
        algo = st.selectbox("Algorithm", ["NMF (TF-IDF)", "LDA (Count)"])
        n_topics = st.slider("Number of topics", min_value=3, max_value=20, value=8, step=1)
        max_features = st.slider("Max vocabulary size", min_value=1000, max_value=20000, value=5000, step=500)

        col_ng1, col_ng2 = st.columns(2)
        with col_ng1:
            min_n = st.slider("Min n-gram", 1, 3, 1, step=1)
        with col_ng2:
            max_n = st.slider("Max n-gram", 1, 3, 2, step=1)
        if max_n < min_n:
            st.error("Max n-gram must be ≥ Min n-gram.")
            return
        ngram_range = (min_n, max_n)

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            min_df = st.number_input("min_df (min docs containing term)", min_value=1, max_value=100, value=2, step=1)
        with col_f2:
            max_df = st.slider("max_df (ignore if in >X% docs)", 0.50, 1.00, 0.95, step=0.01)

        cta1, cta2 = st.columns(2)
        with cta1:
            train_btn = st.button("🚀 Train model", key="btn_train_model", use_container_width=True)
        with cta2:
            save_btn = st.button("💾 Save artifacts", key="btn_save_artifacts", use_container_width=True, disabled=("tm_model" not in st.session_state))

    words_per_doc = 200
    try:
        docs = make_docs_from_text(cleaned_text, words_per_doc=words_per_doc)
    except Exception:
        docs = []

    if len(docs) <= 1:
        docs_fallback = _chunk_by_words(cleaned_text, chunk_size=words_per_doc, overlap=20)
        if len(docs_fallback) > 1:
            docs = docs_fallback

    if len(docs) < 5:
        st.error("Not enough text to form multiple documents. Add more text or use a larger CSV.")
        return

    if train_btn:
        with st.spinner("Vectorizing & training…"):
            if algo.startswith("NMF"):
                V = vectorize_tfidf(
                    docs,
                    max_features=max_features,
                    ngram_range=ngram_range,
                    min_df=min_df,
                    max_df=max_df
                )
                X_nd = safe_array(V.X)
                model = fit_nmf(X_nd, n_topics=n_topics)
                algo_name = "NMF"
            else:
                V = vectorize_count(
                    docs,
                    max_features=max_features,
                    ngram_range=ngram_range,
                    min_df=min_df,
                    max_df=max_df
                )
                X_nd = safe_array(V.X)
                model = fit_lda(X_nd, n_topics=n_topics)
                algo_name = "LDA"

            st.session_state["tm_algo"] = algo_name
            st.session_state["tm_vectorizer"] = V.vectorizer
            st.session_state["tm_model"] = model
            st.session_state["tm_feature_names"] = V.feature_names
            st.session_state["tm_docs"] = docs
            st.session_state["tm_X"] = X_nd

        st.success(f"Trained {algo_name} with {n_topics} topics ✔")

    # --- Diagnostics (Coherence, Perplexity, Diversity, Silhouette) ---
    if "tm_model" in st.session_state:
        model = st.session_state["tm_model"]
        feat_names = st.session_state.get("tm_feature_names")
        X_vec = st.session_state.get("tm_X")
        docs_for_eval = st.session_state.get("tm_docs", [])

        with st.expander("🛠️ Model diagnostics (coherence, perplexity, diversity, silhouette)", expanded=False):
            if not docs_for_eval or not feat_names:
                st.warning("Docs or feature names missing.")
            else:
                total_docs = len(docs_for_eval)
                SAMPLE_DOCS = st.slider("Docs to sample", 50, min(1000, total_docs), min(200, total_docs), 50, key="diag_sample_docs")
                TOPN = st.slider("Top N words per topic (for coherence)", 5, 20, 10, key="diag_topn")
                compute_sil = st.checkbox("Compute silhouette (slower)", value=False, key="diag_sil")

                sampled_docs = docs_for_eval[:SAMPLE_DOCS]

                @st.cache_data(show_spinner=False, ttl=3600)
                def coherence_cv_cached(sd, topn, feat_key):
                    from src.topic_modeling import compute_coherence_score
                    return compute_coherence_score(model, sd, feat_names, topn=topn, coherence="c_v")

                try:
                    coh_cv = coherence_cv_cached(sampled_docs, TOPN, "|".join(feat_names[:500]))
                except Exception as e:
                    coh_cv = None
                    st.warning(f"c_v coherence failed: {e}")

                try:
                    from src.topic_modeling import compute_model_perplexity, topic_diversity
                    perp = compute_model_perplexity(model, X_vec)
                    div  = topic_diversity(model, feat_names, topn=TOPN)
                except Exception:
                    perp, div = None, None

                sil = None
                if compute_sil:
                    try:
                        from src.topic_modeling import topic_silhouette_score
                        SIL_DOCS = min(300, SAMPLE_DOCS)
                        sil = topic_silhouette_score(
                            sampled_docs[:SIL_DOCS],
                            model,
                            X_vec[:SIL_DOCS] if hasattr(X_vec,'__getitem__') else X_vec,
                            feat_names,
                            topn_docs=SIL_DOCS
                        )
                    except Exception as e:
                        st.warning(f"Silhouette failed: {e}")

                k1, k2, k3, k4 = st.columns(4)
                with k1: st.metric("Coherence (c_v, 0–1 ↑)", f"{coh_cv:.4f}" if coh_cv is not None else "—")
                with k2: st.metric("Perplexity (↓)", f"{perp:.2f}" if perp is not None else "—")
                with k3: st.metric("Topic diversity (↑)", f"{div:.3f}" if div is not None else "—")
                with k4: st.metric("Silhouette (↑)", f"{sil:.4f}" if sil not in (None, float('nan')) else "—")

                if st.button("🧹 Clear cached coherence"):
                    try:
                        st.cache_data.clear()
                        st.success("Cache cleared. Re-run diagnostics.")
                    except Exception:
                        pass

    # Show topics (if trained)
    if "tm_model" in st.session_state:
        model = st.session_state["tm_model"]
        feature_names = st.session_state.get("tm_feature_names")
        X = st.session_state.get("tm_X")

        st.subheader("🧩 Discovered Topics")
        topics = top_terms_per_topic(model, feature_names, topn=10)
        for k, terms in enumerate(topics, start=1):
            st.markdown(f"**Topic {k}:** " + ", ".join(terms))

        st.subheader("📈 Topic distribution (first 6 docs)")
        theta = doc_topic_distribution(model, X)
        n_show = min(6, theta.shape[0])
        df_theta = pd.DataFrame(theta[:n_show], columns=[f"Topic {i+1}" for i in range(theta.shape[1])])
        st.dataframe(df_theta.style.format("{:.2f}"), use_container_width=True)

        with st.expander("💾 Save (model + vectorizer)"):
            prefix = st.text_input("Path prefix", value="models/topic_model")
            if st.button("Save", use_container_width=True, key="btn_save_model"):
                try:
                    save_artifacts(prefix, model, st.session_state["tm_vectorizer"])
                    st.success(f"Saved: {prefix}_model.joblib and {prefix}_vectorizer.joblib")
                except Exception as e:
                    st.error(f"Failed to save: {e}")
    else:
        st.info("Adjust settings and click **Train model** to see topics.")

    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        if st.button("➡️ Next: Sentiment Analysis", key="btn_next_sentiment", use_container_width=True):
            nav_to("Sentiment")

# --- Sentiments (RESTORED: topic-wise bars) ---
def page_sentiment():
    import numpy as np
    import pandas as pd

    try:
        from src.sentiment import (
            analyze_vader,
            analyze_hf,
            distribution,
            overall_distribution_pct,
        )
    except Exception as e:
        st.error(f"Sentiment helpers missing: {e}")
        return

    has_tm = all(k in st.session_state for k in ["tm_model", "tm_X"])
    if has_tm:
        try:
            from src.topic_modeling import doc_topic_distribution
        except Exception as e:
            has_tm = False
            st.warning(f"Topic helpers missing for per-topic sentiment: {e}")

    st.title("💬 Sentiment Analysis")

    # Robust text sourcing (PATCH)
    docs = ensure_docs(min_docs=1, words_per_doc=200)
    if not docs:
        raw_fallback = (st.session_state.get("cleaned_text")
                        or st.session_state.get("raw_text") or "")
        if raw_fallback.strip():
            words = raw_fallback.split()
            step = 160
            docs = [" ".join(words[i:i+step]) for i in range(0, len(words), step)]
            st.session_state["docs"] = docs

    # Simple join without over-cleaning
    text_all = " ".join(docs) if docs else ""

    with st.expander("⚙️ Sentiment settings", expanded=True):
        analyzer = st.selectbox(
            "Choose analyzer",
            ["VADER (fast)", "Hugging Face (accurate)"],
            key="sent_sel_analyzer",
        )
        batch_size = st.slider(
            "Batch size (HF only)",
            min_value=4,
            max_value=32,
            value=16,
            step=4,
            key="sent_hf_batch",
            disabled=not analyzer.startswith("Hugging"),
        )
        if has_tm:
            aggregation = st.selectbox(
                "Per-topic aggregation",
                ["Dominant topic (argmax)", "Weighted by topic prob"],
                key="sent_topic_agg",
            )
        else:
            aggregation = None

        run_btn = st.button("🔎 Run Sentiment", key="btn_sent_run", use_container_width=True)

    if not text_all.strip():
        st.warning("No text available yet. Please add data on the **Data Input** page.")
        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Back: Data Input", key="btn_sent_back_input", use_container_width=True):
                nav_to("Data Input")
        with c2:
            if st.button("🧾 Go to Summarization", key="btn_sent_goto_summ_empty", use_container_width=True):
                nav_to("Summarization")
        return

    if run_btn:
        with st.spinner("Analyzing sentiment…"):
            if len(docs) >= 3:
                if analyzer.startswith("VADER"):
                    results = analyze_vader(docs)
                else:
                    results = analyze_hf(docs, batch_size=batch_size)
            else:
                if analyzer.startswith("VADER"):
                    res = analyze_vader([text_all])
                else:
                    res = analyze_hf([text_all], batch_size=batch_size)
                results = res

        st.session_state["sentiment_results"] = results

        labels = [r.get("label") for r in results if isinstance(r, dict)]
        counts = distribution(labels) if labels else {}
        pct = overall_distribution_pct(labels) if labels else {}

        st.subheader("📊 Overall Sentiment Distribution")
        overall_df = pd.DataFrame(
            [
                {"label": "NEGATIVE", "count": counts.get("NEGATIVE", 0), "pct": pct.get("NEGATIVE", 0.0)},
                {"label": "NEUTRAL",  "count": counts.get("NEUTRAL",  0), "pct": pct.get("NEUTRAL",  0.0)},
                {"label": "POSITIVE", "count": counts.get("POSITIVE", 0), "pct": pct.get("POSITIVE", 0.0)},
            ]
        )
        overall_df["pct_display"] = overall_df["pct"].apply(lambda v: f"{v:.1f}%")
        st.dataframe(
            overall_df[["label", "count", "pct_display"]].rename(columns={"pct_display": "pct"}),
            use_container_width=True,
        )

        try:
            import plotly.express as px
            values_col = "pct" if len(results) >= 3 else "count"
            fig = px.pie(overall_df, names="label", values=values_col, title="Overall sentiment", hole=0.35)
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass

        # RESTORED: per-topic sentiment bars (argmax & weighted)
        if has_tm and len(results) >= 3:
            try:
                theta = doc_topic_distribution(st.session_state["tm_model"], st.session_state["tm_X"])
            except Exception as e:
                theta = None
                st.warning(f"Could not compute per-topic sentiment: {e}")

            if theta is not None:
                st.subheader("🧩 Sentiment by Topic")

                n = min(len(results), getattr(theta, "shape", (0, 0))[0])
                if n == 0:
                    st.info("No overlapping documents for topic alignment.")
                else:
                    theta = theta[:n, :]
                    labels_aligned = labels[:n]
                    n_topics = theta.shape[1]

                    if aggregation and aggregation.startswith("Dominant"):
                        dom = np.argmax(theta, axis=1)
                        rows = []
                        for t in range(n_topics):
                            idxs = np.where(dom == t)[0]
                            topic_labels = [labels_aligned[i] for i in idxs]
                            neg = topic_labels.count("NEGATIVE")
                            neu = topic_labels.count("NEUTRAL")
                            pos = topic_labels.count("POSITIVE")
                            total = max(1, len(idxs))
                            rows.append(
                                {
                                    "topic": t,
                                    "NEGATIVE": neg,
                                    "NEUTRAL": neu,
                                    "POSITIVE": pos,
                                    "neg_pct": neg * 100.0 / total,
                                    "neu_pct": neu * 100.0 / total,
                                    "pos_pct": pos * 100.0 / total,
                                    "total_docs": total,
                                }
                            )
                        s_df = pd.DataFrame(rows)
                        s_df_display = s_df.copy()
                        for c in ["neg_pct", "neu_pct", "pos_pct"]:
                            s_df_display[c] = s_df_display[c].round(1)
                        st.dataframe(
                            s_df_display.rename(
                                columns={
                                    "topic": "Topic",
                                    "NEGATIVE": "Negative (count)",
                                    "NEUTRAL": "Neutral (count)",
                                    "POSITIVE": "Positive (count)",
                                    "neg_pct": "Negative (%)",
                                    "neu_pct": "Neutral (%)",
                                    "pos_pct": "Positive (%)",
                                    "total_docs": "Total docs",
                                }
                            ),
                            use_container_width=True,
                        )

                        try:
                            import plotly.express as px
                            plot_df = s_df[["topic", "pos_pct", "neu_pct", "neg_pct"]].melt(
                                id_vars=["topic"],
                                value_vars=["pos_pct", "neu_pct", "neg_pct"],
                                var_name="sentiment",
                                value_name="pct",
                            )
                            plot_df["sentiment"] = plot_df["sentiment"].map(
                                {"pos_pct": "Positive", "neu_pct": "Neutral", "neg_pct": "Negative"}
                            )
                            plot_df["pct"] = plot_df["pct"].astype(float)
                            fig = px.bar(
                                plot_df,
                                x="topic",
                                y="pct",
                                color="sentiment",
                                barmode="group",
                                title="Sentiment % by Topic (argmax)",
                                text="pct",
                            )
                            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                            fig.update_layout(xaxis_title="Topic (0-indexed)", yaxis_title="Percent (%)")
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception:
                            pass

                    else:
                        rows = []
                        for t in range(n_topics):
                            neg_w = neu_w = pos_w = 0.0
                            for i, lab in enumerate(labels_aligned):
                                w = float(theta[i, t])
                                if lab == "NEGATIVE":
                                    neg_w += w
                                elif lab == "NEUTRAL":
                                    neu_w += w
                                elif lab == "POSITIVE":
                                    pos_w += w
                            total = max(1e-9, neg_w + neu_w + pos_w)
                            rows.append(
                                {
                                    "topic": t,
                                    "NEGATIVE": neg_w,
                                    "NEUTRAL": neu_w,
                                    "POSITIVE": pos_w,
                                    "neg_pct": neg_w * 100.0 / total,
                                    "neu_pct": neu_w * 100.0 / total,
                                    "pos_pct": pos_w * 100.0 / total,
                                    "total_weight": total,
                                }
                            )
                        s_df = pd.DataFrame(rows)
                        s_df_display = s_df.copy()
                        for c in ["neg_pct", "neu_pct", "pos_pct"]:
                            s_df_display[c] = s_df_display[c].round(1)
                        st.caption("Weighted: each document contributes to topics proportional to its topic probability.")
                        st.dataframe(
                            s_df_display.rename(
                                columns={
                                    "topic": "Topic",
                                    "NEGATIVE": "Negative (weight)",
                                    "NEUTRAL": "Neutral (weight)",
                                    "POSITIVE": "Positive (weight)",
                                    "neg_pct": "Negative (%)",
                                    "neu_pct": "Neutral (%)",
                                    "pos_pct": "Positive (%)",
                                    "total_weight": "Total weight",
                                }
                            ),
                            use_container_width=True,
                        )

                        try:
                            import plotly.express as px
                            plot_df = s_df[["topic", "pos_pct", "neu_pct", "neg_pct"]].melt(
                                id_vars=["topic"],
                                value_vars=["pos_pct", "neu_pct", "neg_pct"],
                                var_name="sentiment",
                                value_name="pct",
                            )
                            plot_df["sentiment"] = plot_df["sentiment"].map(
                                {"pos_pct": "Positive", "neu_pct": "Neutral", "neg_pct": "Negative"}
                            )
                            plot_df["pct"] = plot_df["pct"].astype(float)
                            fig = px.bar(
                                plot_df,
                                x="topic",
                                y="pct",
                                color="sentiment",
                                barmode="group",
                                title="Sentiment % by Topic (weighted)",
                                text="pct",
                            )
                            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                            fig.update_layout(xaxis_title="Topic (0-indexed)", yaxis_title="Percent (%)")
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception:
                            pass

        st.success("Sentiment analysis complete ✅")

    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("⬅️ Back: Topic Modeling", key="btn_sent_nav_tm", use_container_width=True):
            nav_to("Topic Modeling")
    with c2:
        if st.button("🧾 Go to Summarization", key="btn_sent_nav_summ", use_container_width=True):
            nav_to("Summarization")
    with c3:
        if st.button("📊 Open Dashboard", key="btn_sent_nav_dash", use_container_width=True):
            nav_to("Dashboard")


# --- Summarization  ---
def page_summarization():
    """Complete summarization with topic-level summaries."""
    import streamlit as st
    import pandas as pd
    import numpy as np
    import re
    
    st.title("🧾 Summarization")
    
    # ============ Helper: Nuclear Clean ============
    def nuclear_clean(text: str) -> str:
        """Gentle removal of ads - keeps most content."""
        if not text or len(text.strip()) < 100:
            return text
        
        # Only remove lines that are CLEARLY promotional
        lines = text.split('\n')
        clean_lines = []
        
        for line in lines:
            # Skip if line is pure vendor marketing
            if re.search(r'\b(NetApp|ONTAP)\b.*\b(software|enables?|solutions?)\b', line, re.I):
                continue
            # Skip IJRTI codes
            if re.search(r'IJRTI\d{5,}', line):
                continue
            # Keep everything else
            clean_lines.append(line)
        
        return '\n'.join(clean_lines)
    
    # ============ Prerequisites ============
    raw_text = st.session_state.get("raw_text", "")
    
    if not raw_text or len(raw_text.strip()) < 100:
        st.warning("⚠️ No text found. Go to **Data Input** first.")
        if st.button("⬅️ Go to Data Input"):
            nav_to("Data Input")
        return
    
    # ============ CSV Options ============
    df_preview = st.session_state.get("df_preview")
    use_csv = False
    csv_text = ""
    
    if df_preview is not None and isinstance(df_preview, pd.DataFrame) and len(df_preview) > 0:
        with st.expander("📊 CSV Column Selection", expanded=False):
            numeric_cols = set(df_preview.select_dtypes(include=[np.number]).columns)
            text_cols = [c for c in df_preview.columns if c not in numeric_cols]
            
            if text_cols:
                col_select = st.selectbox("Column", ["[All text]"] + text_cols)
                n_rows = st.slider("Rows", 50, min(1000, len(df_preview)), 200, 50)
                
                if col_select != "[All text]":
                    use_csv = True
                    csv_text = "\n\n".join(df_preview[col_select].dropna().astype(str).head(n_rows).tolist())
                    st.info(f"Using {n_rows} rows from: **{col_select}**")
    
    # ============ Source Text ============
    source_text = csv_text if use_csv else raw_text
    pages = st.session_state.get("pages") if st.session_state.get("source_type") == "pdf" else None
    
    st.write(f"**Source:** {len(source_text):,} chars, {len(source_text.split()):,} words")
    
    # ============ Settings ============
    st.subheader("⚙️ Summarization Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        mode = st.selectbox(
            "Mode",
            ["Hybrid (Best Quality)", "Extractive (Fastest)"],
            index=0,
            help="Hybrid = Extractive + Abstractive polish"
        )
        mode_value = "hybrid" if "Hybrid" in mode else "extractive"
    
    with col2:
        num_sentences = st.slider("Extractive sentences", 5, 20, 10, 1)
    
    with col3:
        use_embeddings = st.checkbox("Use embeddings", value=True, help="Slower but better quality")
    
    # Model selection (ONLY for Hybrid mode)
    selected_model = "distilbart"
    
    if mode_value == "hybrid":
        st.markdown("---")
        st.markdown("##### 🤖 Abstractive Model (Hybrid Mode)")
        
        col4, col5 = st.columns([1, 1])
        with col4:
            model_name = st.selectbox(
                "Model",
                ["DistilBART (Fast, 500MB)", "BART-large (Quality, 1.6GB)"],
                index=0
            )
            selected_model = "distilbart" if "DistilBART" in model_name else "bart"
        
        with col5:
            st.info("**Pipeline:**\n1. Extract key sentences\n2. Rephrase with BART")
        
        st.markdown("---")
    
    # Length controls
    col6, col7 = st.columns(2)
    with col6:
        min_words = st.number_input("Min words", 100, 300, 150, 10)
    with col7:
        max_words = st.number_input("Max words", 150, 500, 300, 10)
    
    # ============ Generate Executive Summary ============
    if st.button("🚀 Generate Executive Summary", type="primary", use_container_width=True):
        
        with st.spinner("Cleaning text..."):
            # Try gentle cleaning first (NO aggressive mode)
            import unicodedata
            
            cleaned_text = source_text
            
            # Step 1: Basic normalization
            cleaned_text = unicodedata.normalize("NFKC", cleaned_text)
            cleaned_text = cleaned_text.replace("\u00A0", " ")
            
            # Step 2: Remove obvious boilerplate
            cleaned_text = re.sub(r"©\s*\d{4}[^\n.]{0,100}", " ", cleaned_text)
            cleaned_text = re.sub(r"\bISSN[:\s]*\d[\dxX\-]+", " ", cleaned_text)
            cleaned_text = re.sub(r"\bIJRTI\d{5,}", " ", cleaned_text)
            cleaned_text = re.sub(r"https?://\S+", " ", cleaned_text)
            
            # Step 3: Cut at References section
            parts = re.split(r"(?i)\bREFERENCES?\s*\n", cleaned_text, maxsplit=1)
            if len(parts) > 1:
                cleaned_text = parts[0]
            
            # Step 4: Cut at NetApp section header
            parts = re.split(r"(?i)\bNetApp and artificial intelligence\b", cleaned_text, maxsplit=1)
            if len(parts) > 1:
                cleaned_text = parts[0]
            
            # Step 5: Nuclear clean (gentle)
            cleaned_text = nuclear_clean(cleaned_text)
            
            # Step 6: Final cleanup
            cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text).strip()
            
            st.write(f"✅ Cleaned: {len(cleaned_text.split())} words")
    
        # Check if we have enough text
        if len(cleaned_text.split()) < 100:
            st.error("❌ Not enough text after cleaning. Your document might be mostly boilerplate.")
            st.text_area("Debug - what's left:", cleaned_text[:500], height=150)
            return
        
        # Summarize
        with st.spinner("Generating summary..."):
            try:
                from src.summarization import summarize_document
                
                summary_result = summarize_document(
                    cleaned_text,
                    mode=mode_value,
                    num_sentences=num_sentences,
                    min_words=min_words,
                    max_words=max_words,
                    use_embeddings=use_embeddings,
                    model_name=selected_model
                )
                
                summary = summary_result.get("summary", "")
                
                if not summary or len(summary.split()) < 20:
                    st.error("⚠️ Summary too short or empty.")
                    st.text_area("Extractive output:", summary_result.get("extractive_summary", "")[:500])
                    return
                
                # Store
                st.session_state["final_summary"] = summary
                
                # ============ Display Executive Summary ============
                st.success("✅ Summary Generated")
                st.markdown("### 📝 Executive Summary")
                st.markdown(f"> {summary}")
                st.caption(
                    f"**Mode:** {summary_result['mode_used']} | "
                    f"**Words:** {summary_result['word_count']} | "
                    f"**Compression:** {len(cleaned_text.split())} → {summary_result['word_count']}"
                )
                
                # ============ Highlights ============
                st.markdown("### ✨ Key Highlights")
                
                from src.cleaners import split_sentences
                from src.summarization import extractive_summary_tfidf
                
                sentences = split_sentences(cleaned_text)
                highlights = extractive_summary_tfidf(sentences, k=6)
                
                # Filter out promotional sentences
                clean_highlights = []
                for h in highlights:
                    if not re.search(r'\b(NetApp|ONTAP|IJRTI|building blocks)\b', h, re.I):
                        clean_highlights.append(h)
                
                if len(clean_highlights) < 4:
                    clean_highlights = highlights[:6]
                
                for i, h in enumerate(clean_highlights, 1):
                    st.markdown(f"{i}. {h}")
                
                st.session_state["highlights"] = clean_highlights
                
                # ============ Key Insights ============
                st.markdown("### 🔎 Key Insights")
                
                insights = []
                
                # Topic modeling insights
                if "tm_model" in st.session_state:
                    try:
                        from src.topic_modeling import top_terms_per_topic
                        keywords = top_terms_per_topic(
                            st.session_state["tm_model"],
                            st.session_state.get("tm_feature_names", []),
                            topn=5
                        )
                        for i, kws in enumerate(keywords[:3], 1):
                            insights.append(f"**Topic {i}:** {', '.join(kws)}")
                    except:
                        pass
                
                # Sentiment insights
                if "sentiment_results" in st.session_state:
                    results = st.session_state["sentiment_results"]
                    if results and isinstance(results, list):
                        labels = [r.get("label", "") for r in results if isinstance(r, dict)]
                        if labels:
                            total = len(labels)
                            pos = labels.count("POSITIVE") * 100 / total
                            neg = labels.count("NEGATIVE") * 100 / total
                            neu = labels.count("NEUTRAL") * 100 / total
                            insights.append(f"**Sentiment:** {pos:.1f}% Positive, {neu:.1f}% Neutral, {neg:.1f}% Negative")
                
                if insights:
                    for insight in insights:
                        st.markdown(f"- {insight}")
                    st.session_state["key_insights"] = insights
                else:
                    st.info("Run Topic Modeling and Sentiment first to see insights here.")
                
            except Exception as e:
                st.error(f"❌ Summarization failed: {str(e)}")
                st.exception(e)
    
    # ============ Topic-Level Summaries ============
    st.markdown("---")
    st.subheader("🧩 Topic-Level Summaries")
    
    has_topics = all(k in st.session_state for k in ["tm_model", "tm_X", "tm_docs"])
    
    if not has_topics:
        st.info("Run **Topic Modeling** first to enable topic-level summaries.")
        if st.button("➡️ Go to Topic Modeling"):
            nav_to("Topic Modeling")
    else:
        sentences_per_topic = st.slider("Sentences per topic", 3, 10, 5, 1)
        
        if st.button("📑 Generate Topic Summaries", use_container_width=True):
            with st.spinner("Generating topic summaries..."):
                try:
                    from src.topic_modeling import doc_topic_distribution, top_terms_per_topic
                    from src.summarization import summarize_by_topics
                    
                    theta = doc_topic_distribution(st.session_state["tm_model"], st.session_state["tm_X"])
                    topic_assignments = np.argmax(theta, axis=1).tolist()
                    docs = st.session_state["tm_docs"]
                    n_topics = theta.shape[1]
                    
                    topic_summaries = summarize_by_topics(docs, topic_assignments, n_topics, sentences_per_topic)
                    keywords = top_terms_per_topic(
                        st.session_state["tm_model"],
                        st.session_state.get("tm_feature_names", []),
                        topn=8
                    )
                    
                    rows = []
                    for t in range(n_topics):
                        n_docs = topic_assignments.count(t)
                        summary = topic_summaries.get(t, "")
                        kws = ", ".join(keywords[t] if t < len(keywords) else [])
                        
                        rows.append({
                            "Topic": t + 1,
                            "Keywords": kws,
                            "Documents": n_docs,
                            "Summary": summary[:200] + "..." if len(summary) > 200 else summary
                        })
                    
                    df = pd.DataFrame(rows)
                    st.success(f"✅ Generated {n_topics} topic summaries")
                    st.dataframe(df, use_container_width=True, height=400)
                    
                    st.session_state["topic_summaries"] = rows
                    st.session_state["topic_summaries_table"] = df
                    
                    csv = df.to_csv(index=False)
                    st.download_button("📥 Download CSV", csv, "topic_summaries.csv", "text/csv")
                    
                except Exception as e:
                    st.error(f"❌ Failed: {e}")
    
    # ============ Navigation ============
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ Back: Sentiment", use_container_width=True):
            nav_to("Sentiment")
    with col2:
        if st.button("📊 Dashboard", use_container_width=True):
            nav_to("Dashboard")
    with col3:
        if st.button("🔄 Clear & Restart", use_container_width=True):
            for key in ["final_summary", "highlights", "key_insights", "topic_summaries"]:
                st.session_state.pop(key, None)
            st.rerun()



# --- Dashboard ---
def page_dashboard_local_fallback():
    if "tm_model" not in st.session_state:
        st.info("⚠️ No topic model available. Showing direct summary instead.")
        text = st.session_state.get("raw_text", "")
        if text.strip():
            from src.summarization import summarize_abstractive_polish
            summary = summarize_abstractive_polish(text)
            st.subheader("Direct Summary")
            st.write(summary)
        else:
            st.warning("No text found to summarize.")
        st.stop()

    st.title("📊 Dashboard (local fallback)")
    st.write("This is the local dashboard fallback. Use Summarization -> Open Dashboard to produce topic summaries first.")
    topic_summaries = st.session_state.get("topic_summaries")
    if topic_summaries:
        if isinstance(topic_summaries, list):
            for r in topic_summaries:
                st.markdown(f"**{r.get('topic_display','Topic')}**")
                st.write((r.get("summary") or "")[:400] + ("..." if r.get("summary") and len(r.get("summary"))>400 else ""))

def page_dashboard_router():
    try:
        from src.dashboard import page_dashboard as modular_dashboard
        modular_dashboard()
    except Exception:
        page_dashboard_local_fallback()

# --- About Us ---
def page_about():
    st.title("ℹ️ About")
    st.write("""
    **AI Text Analysis** helps you convert raw text and CSVs into actionable insights.
    Built with Streamlit, pandas, spaCy and scikit-learn.
    """)


# ---------------- MAIN ----------------
def main():
    sync_url_to_state()
    init_page()
    render_navbar()

    page = st.session_state.get("page", "Home")
    routes = {
        "Home": page_home,
        "Data Input": page_data_input,
        "Preprocessing": page_preprocessing,
        "Topic Modeling": page_topics,
        "Sentiment": page_sentiment,
        "Summarization": page_summarization,
        "Dashboard": page_dashboard_local_fallback,
        "About": page_about,
    }
    routes.get(page, lambda: st.write("Page not found."))()

if __name__ == "__main__":
    main()


st.markdown(
    """
    <hr style="opacity:.08; margin-top:36px;">
    <div style="display:flex; align-items:center; justify-content:space-between; color:#9fb1bd;">
      <div>© 2025 NarrativeNexus</div>
      <div style="display:flex; gap:14px;">
        <a href="#" style="color:#9fb1bd; text-decoration:none;">Features</a>
        <a href="#" style="color:#9fb1bd; text-decoration:none;">Contact</a>
        <a href="#" style="color:#9fb1bd; text-decoration:none;">GitHub</a>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)
