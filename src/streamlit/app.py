# Streamlit app: auto-load api_response.json on startup, show a branded Answer box,
# and display a clean References table. Two PNG logos are used automatically:
#   RIGHT logo is a faint page background (watermark)
#   LEFT logo sits to the right of the header
#
# Run:
#   pip install streamlit pandas
#   streamlit run app.py

from __future__ import annotations
import base64
import html
import json
import pathlib
import re
import pandas as pd
import streamlit as st

# ---------------- Page setup ----------------
st.set_page_config(page_title="Text/JSON ➜ PNG Logos (auto)", page_icon="🧩", layout="centered")
st.title("SwissRE Output Viewer")

# ---------------- Theme (same colors as before; tweak here if needed) ----------------
PRIMARY     = "#80A651"   # brand green (headers/buttons)
ACCENT      = "#B0D46F"   # light green (accents)
BG_TINT     = "#F1F4F4"   # tinted section background
BD_COL      = "#DDDDDD"   # soft border
ANSWER_COLOR= "#000000"   # bright text color for the Answer box

st.markdown(
    f"""
    <style>
    :root {{
        --pr:{PRIMARY}; --ac:{ACCENT}; --bg:{BG_TINT}; --bd:{BD_COL}; --answer:{ANSWER_COLOR};
    }}

    /* Answer wrapper and text styling */
    .answer-card {{
        background:#fff;
        border-left:6px solid var(--pr);
        border:1px solid var(--bd);
        border-radius:10px;
        padding:14px;
        box-shadow:1px 1px 3px rgba(0,0,0,0.04);
        margin-bottom:10px;
    }}
    .answer-box {{
        color:var(--answer);
        font-family: ui-serif, Georgia, "Times New Roman", serif;
        font-size:1.12rem;
        line-height:1.75;
        font-weight:700;
        white-space:pre-wrap;
        background:linear-gradient(180deg, rgba(139,209,70,0.12) 0%, #ffffff 60%);
        border-top:1px solid #e6e6e6;
        border-radius:10px;
        padding:12px 14px;
        box-shadow: inset 1px 1px 2px rgba(0,0,0,.03);
    }}

    /* Section panel (for references) */
    .section {{
        background:var(--bg);
        border:1px solid var(--bd);
        border-radius:10px;
        padding:12px;
        margin-top:8px;
    }}

    /* Headings & primary button */
    .block-container h2, .block-container h3 {{ color:{PRIMARY}; }}

    /* Keep page overlay clear for watermark */
    [data-testid="stAppViewContainer"] {{ background: transparent !important; }}
    .bg-overlay::before {{
        content:''; position:fixed; inset:0;
        background-repeat:no-repeat; background-position:center;
        background-size:60%; opacity:0.12; z-index:0;
        pointer-events:none;
    }}
    .bg-overlay .block-container {{ position:relative; z-index:1; }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="bg-overlay"></div>', unsafe_allow_html=True)

# ---------------- Helpers ----------------
@st.cache_data(show_spinner=False)
def _decode_bytes(b: bytes) -> str:
    for enc in ("utf-8", "utf-16", "latin-1"):
        try:
            return b.decode(enc)
        except Exception:
            pass
    return b.decode("utf-8", errors="replace")

@st.cache_data(show_spinner=False)
def _read_local_text(path: str) -> str:
    p = (pathlib.Path(__file__).parent / path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"No file found at: {p}")
    if p.is_dir():
        raise IsADirectoryError(f"Path is a directory: {p}")
    return _decode_bytes(p.read_bytes())

@st.cache_data(show_spinner=False)
def _read_local_bytes(path: str) -> bytes:
    p = (pathlib.Path(__file__).parent / path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"No file found at: {p}")
    if p.is_dir():
        raise IsADirectoryError(f"Path is a directory: {p}")
    return p.read_bytes()

def set_page_bg(img_bytes: bytes, opacity: float = 0.12, size: str = "60%min") -> None:
    b64 = base64.b64encode(img_bytes).decode()
    st.markdown(
        f"""
        <style>
        .bg-overlay::before {{
            background-image:url('data:image/png;base64,{b64}');
            background-repeat:no-repeat; background-position:center;
            background-size:{size}; opacity:{opacity};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ---------------- Logos (auto) ----------------
# Expecting the two images to live alongside the app (same folder)
LEFT_LOGO_PATH  = "securian.png"
RIGHT_LOGO_PATH = "securian_.png"

try:
    set_page_bg(_read_local_bytes(RIGHT_LOGO_PATH), opacity=0.12, size="60%min")
except Exception as e:
    st.warning(f"Background not set: {{type(e).__name__}}: {{e}}")

try:
    hdr_left, hdr_right = st.columns([0.78, 0.22], gap="small")
    with hdr_right:
        st.image(_read_local_bytes(LEFT_LOGO_PATH), use_container_width=True)
except Exception as e:
    st.warning(f"Header logo not shown: {{type(e).__name__}}: {{e}}")

# ---------------- Auto-load JSON on startup (no uploader, no buttons) ----------------
# Try a couple of sensible locations
CANDIDATE_JSON_PATHS = [
    "api_response.json",
    "../api_response.json",
    "../../api_response.json",
    "../src/api_response.json",
]

text = None
last_err = None
for candidate in CANDIDATE_JSON_PATHS:
    try:
        text = _read_local_text(candidate)
        break
    except Exception as e:
        last_err = e

if text is None:
    st.error(f"Couldn't read an api_response.json near the app. Last error: {{type(last_err).__name__}}: {{last_err}}")
    st.stop()

# ---------------- Parse JSON; if invalid, show a friendly error ----------------
try:
    obj = json.loads(text)
except Exception as e:
    st.error(f"`api_response.json` is not valid JSON. {{type(e).__name__}}: {{e}}")
    st.stop()

# ---------------- Render JSON (Answer + References only) ----------------
if isinstance(obj, dict):
    st.subheader("Answer", anchor=False)

    answer_html = obj.get("answer", "")
    answer_plain = re.sub(r"<[^>]+>", "", answer_html) if answer_html else ""
    answer_plain_escaped = html.escape(answer_plain)

    st.markdown('<div class="answer-card">', unsafe_allow_html=True)
    if answer_html:
        st.markdown(f'<div class="answer-box">{answer_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="answer-box">{answer_plain_escaped}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- References (Ref #, Label, Link only) ----
    refs = obj.get("references", [])
    rows = []
    if isinstance(refs, list) and refs:
        for r in refs:
            if isinstance(r, dict):
                rows.append({
                    "Ref #": r.get("referenceNumber"),
                    "Label": r.get("label") or r.get("externalURL") or "",
                    "Link": r.get("externalURL")
                })

    if rows:
        df = pd.DataFrame(rows, columns=["Ref #", "Label", "Link"])
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.markdown("### References")
        try:
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Ref #": st.column_config.NumberColumn("Ref #", format="%d"),
                    "Link": st.column_config.LinkColumn("Link"),
                },
            )
        except Exception:
            # Fallback for older Streamlit versions
            st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.error("Top-level JSON is not an object. Expected keys like 'answer' and 'references'.")
