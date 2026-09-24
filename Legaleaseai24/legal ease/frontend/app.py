import os
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile

import requests
import streamlit as st
from dotenv import load_dotenv

from generators.docx_generator import format_docx
from generators.html_generator import format_html_preview
from generators.pdf_generator import format_pdf
from generators.txt_generator import format_txt

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")


DOCUMENT_TYPES = [
    "Employment Contract",
    "Non-Disclosure Agreement (NDA)",
    "Lease Agreement",
    "Freelance Work Contract",
    "Service Agreement",
    "Employment Offer Letter",
    "General Agreement",
    "Custom Legal Document",
]


def _safe_filename(document_type: str) -> str:
    filename = "".join(
        character if character.isalnum() or character in "-_" else "_"
        for character in document_type.lower()
    ).strip("_")
    return filename or "legalease_document"


def _generate_document(document_type: str, parties: str, terms: str, dates: str) -> requests.Response:
    return requests.post(
        f"{BACKEND_URL}/generate",
        json={
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "dates": dates,
        },
        timeout=120,
    )


@st.cache_data(show_spinner=False, max_entries=16)
def _build_exports(
    document: str,
    document_type: str,
    terms: str,
    logo_bytes: bytes,
    logo_name: str,
) -> tuple[str, bytes, bytes]:
    logo_stream = None
    temporary_logo_path = None
    if logo_bytes:
        logo_stream = BytesIO(logo_bytes)
        with NamedTemporaryFile(
            suffix=Path(logo_name).suffix or ".png", delete=False
        ) as temporary_logo:
            temporary_logo.write(logo_bytes)
            temporary_logo_path = temporary_logo.name
        logo_stream.name = temporary_logo_path

    try:
        return (
            format_txt(document),
            format_docx(document, document_type, terms, logo_stream),
            format_pdf(document, document_type, logo_stream),
        )
    finally:
        if temporary_logo_path:
            try:
                os.remove(temporary_logo_path)
            except OSError:
                pass

st.set_page_config(page_title="LegalEase | Drafting desk", page_icon="⚖️", layout="wide")

st.markdown(
    """
<style>
:root {
    --ink: #17211b;
    --muted: #68736c;
    --paper: #fbfaf6;
    --cream: #f1eee6;
    --line: #d9d8cf;
    --teal: #166b63;
    --teal-dark: #0d504b;
    --coral: #d66c4f;
}

.stApp, body, [data-testid='stAppViewContainer'], [data-testid='stMain'], section.main { background: var(--cream) !important; color: var(--ink); overflow-x: hidden; }
.stApp, .stApp p, .stApp label, .stApp input, .stApp textarea, .stApp button { font-family: 'Trebuchet MS', sans-serif; }
.block-container { max-width: 1320px; padding: 1.1rem clamp(1.2rem, 5vw, 4.5rem) 4rem; }
[data-testid='stHeader'] { background: transparent; }
[data-testid='stToolbar'] { right: 1rem; }
[data-testid='stDecoration'] { background: var(--coral); height: 2px; }

.masthead { display: flex; justify-content: space-between; align-items: center; padding: .75rem 0 1.35rem; border-bottom: 1px solid var(--line); }
.wordmark { color: var(--ink); font: 700 1.2rem 'Consolas', monospace; letter-spacing: .02em; }
.wordmark span { color: var(--coral); }
.system-status { color: var(--muted); font: 500 .68rem 'Consolas', monospace; letter-spacing: .1em; text-transform: uppercase; }
.system-status b { color: var(--teal); }
.intro { padding: 2.7rem 0 2.1rem; max-width: 800px; }
.kicker { color: var(--coral); font: 500 .72rem 'Consolas', monospace; letter-spacing: .13em; text-transform: uppercase; }
.intro h1 { color: var(--ink); font: 700 clamp(2.35rem, 4.5vw, 4.35rem)/1.02 Georgia, serif; letter-spacing: -.04em; margin: .7rem 0 1rem; }
.intro p { color: var(--muted); font-size: 1.08rem; line-height: 1.65; max-width: 650px; margin: 0; }
.section-rule { display: flex; justify-content: space-between; align-items: baseline; border-top: 1px solid var(--ink); padding-top: .75rem; margin: 1rem 0 1.35rem; }
.section-rule h2 { color: var(--ink); font: 600 1.12rem 'Trebuchet MS', sans-serif; margin: 0; }
.section-rule span { color: var(--muted); font: .68rem 'Consolas', monospace; text-transform: uppercase; letter-spacing: .08em; }
.note { background: #e5eee8; border-left: 3px solid var(--teal); color: #38564f; font-size: .82rem; line-height: 1.55; padding: .8rem 1rem; margin: 0 0 1.25rem; }
.workflow-bar { display: grid; grid-template-columns: repeat(3, 1fr); background: var(--paper); border: 1px solid var(--line); border-radius: 4px; margin: 0 0 2.3rem; box-shadow: 0 10px 24px rgba(23,33,27,.04); }
.workflow-step { display: flex; align-items: center; gap: .7rem; min-height: 3.8rem; padding: .7rem 1rem; }
.workflow-step + .workflow-step { border-left: 1px solid var(--line); }
.workflow-number { display: grid; place-items: center; width: 1.55rem; height: 1.55rem; border: 1px solid var(--teal); border-radius: 50%; color: var(--teal-dark); font: .68rem 'Consolas', monospace; flex: 0 0 auto; }
.workflow-step strong { color: var(--ink); display: block; font-size: .77rem; }
.workflow-step span { color: var(--muted); display: block; font-size: .68rem; margin-top: .12rem; }
.workflow-bar, .stForm, .preview-shell { animation: appear .45s ease-out both; }
@keyframes appear { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
.stForm { background: rgba(251,250,246,.8); border: 1px solid var(--line); border-radius: 4px; padding: 1.6rem 1.5rem 1.35rem; box-shadow: 0 16px 34px rgba(23,33,27,.045); }
.form-column-title { border-bottom: 1px solid var(--line); color: var(--teal-dark); font: 600 .72rem 'Consolas', monospace; letter-spacing: .08em; margin: 0 0 .25rem; padding-bottom: .6rem; text-transform: uppercase; }
.stForm [data-testid='stVerticalBlock'] > [style*='flex-direction: column'] { gap: .8rem; }
.stTextInput input, .stTextArea textarea, [data-baseweb='select'] > div { background: var(--paper); border: 1px solid var(--line); border-radius: 3px; color: var(--ink); }
.stTextInput input:focus, .stTextArea textarea:focus { border-color: var(--teal) !important; box-shadow: 0 0 0 1px var(--teal) !important; }
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible, [data-baseweb='select']:focus-within { outline: 3px solid rgba(214,108,79,.55); outline-offset: 2px; }
.stTextArea textarea { line-height: 1.55; }
.stSelectbox label, .stTextInput label, .stTextArea label, .stFileUploader label { color: var(--ink); font-size: .78rem; font-weight: 600; }
[data-testid='stFormSubmitButton'] button { background: var(--teal) !important; border: 1px solid var(--teal) !important; border-radius: 3px; color: white !important; font-weight: 600; min-height: 3rem; }
[data-testid='stDownloadButton'] button, [data-testid='stFormSubmitButton'] button { min-height: 2.85rem; }
[data-testid='stFormSubmitButton'] button:hover { background: var(--teal-dark) !important; border-color: var(--teal-dark) !important; }
[data-testid='stFileUploader'] section { background: rgba(251,250,246,.55); border: 1px dashed #b4b9b0; border-radius: 3px; color: var(--muted); }
[data-testid='stFileUploader'] section small, [data-testid='stFileUploader'] section span { color: var(--muted) !important; }
[data-testid='stFileUploader'] section button { background: var(--ink); border: 1px solid var(--ink); border-radius: 3px; color: white; }
.preview-shell { background: var(--paper); border: 1px solid var(--line); border-top: 4px solid var(--coral); padding: 2.2rem 2.5rem; min-height: 340px; max-height: 650px; overflow-y: auto; box-shadow: 0 14px 30px rgba(23,33,27,.07); }
.preview-shell, .preview-shell * { color: var(--ink); }
.preview-shell h1, .preview-shell h2, .preview-shell h3 { font-family: Georgia, serif; }
.preview-shell h3 { color: var(--teal-dark); }
.editor-label { color: var(--muted); font: .68rem 'Consolas', monospace; letter-spacing: .08em; text-transform: uppercase; margin: 1.6rem 0 .5rem; }
.download-label { color: var(--ink); font: 600 1.1rem 'Trebuchet MS', sans-serif; margin: 1.8rem 0 .8rem; }
.stDownloadButton > button { background: var(--paper); border: 1px solid var(--line); border-radius: 3px; color: var(--ink); font-weight: 600; }
.stDownloadButton > button:hover { border-color: var(--teal); color: var(--teal-dark); }
.metric-strip { display: flex; gap: 2.5rem; border-bottom: 1px solid var(--line); padding: 0 0 1.5rem; margin-bottom: 1.8rem; }
.metric strong { display: block; color: var(--ink); font: 700 1.15rem 'Consolas', monospace; }
.metric small { color: var(--muted); font-size: .73rem; }
.footer { border-top: 1px solid var(--line); color: var(--muted); font: .67rem 'Consolas', monospace; letter-spacing: .04em; margin-top: 3rem; padding-top: 1rem; }
@media (max-width: 720px) { .block-container { padding: 1.3rem 1rem 3rem; } .system-status { display: none; } .intro { padding: 2.5rem 0 2rem; } .intro p { font-size: .98rem; } .preview-shell { padding: 1.4rem; } .metric-strip { gap: 1.3rem; } }
@media (max-width: 720px) { .workflow-bar { grid-template-columns: 1fr; } .workflow-step + .workflow-step { border-left: 0; border-top: 1px solid var(--line); } .workflow-step { min-height: 3.2rem; } }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; scroll-behavior: auto !important; } }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<header class="masthead" aria-label="LegalEase header">
    <div class="wordmark">LEGAL<span>EASE</span></div>
    <div class="system-status"><b aria-hidden="true">●</b>&nbsp; drafting desk / connected</div>
</header>
<main class="intro">
    <div class="kicker">AI-assisted legal drafting</div>
    <h1>Turn the first thought<br>into a formal draft.</h1>
    <p>Describe the agreement in plain language. LegalEase shapes your notes into an editable document you can review, refine, and take with you.</p>
</main>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="workflow-bar" aria-label="Drafting workflow">
    <div class="workflow-step"><div class="workflow-number">01</div><div><strong>Set the brief</strong><span>Tell us what you need</span></div></div>
    <div class="workflow-step"><div class="workflow-number">02</div><div><strong>Review the draft</strong><span>Edit every detail</span></div></div>
    <div class="workflow-step"><div class="workflow-number">03</div><div><strong>Export & share</strong><span>Choose your format</span></div></div>
</div>
""",
    unsafe_allow_html=True,
)

if "document" not in st.session_state:
    st.session_state.document = ""
if "terms" not in st.session_state:
    st.session_state.terms = ""
if "document_type" not in st.session_state:
    st.session_state.document_type = "General Agreement"
if "document_editor" not in st.session_state:
    st.session_state.document_editor = st.session_state.document

st.markdown('<div class="section-rule"><h2>01 / Set the brief</h2><span>Required information</span></div>', unsafe_allow_html=True)
st.markdown('<div class="note"><strong>Review note:</strong> This tool creates an AI-assisted first draft, not legal advice. Check every detail and have important documents reviewed by a qualified professional.</div>', unsafe_allow_html=True)

with st.form("draft_form"):
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown('<div class="form-column-title">Agreement basics</div>', unsafe_allow_html=True)
        selected_type = st.selectbox(
            "Document type",
            DOCUMENT_TYPES,
            index=6,
            key="document_type_input",
        )
        custom_type = ""
        if selected_type == "Custom Legal Document":
            custom_type = st.text_input("Name this document", placeholder="e.g. Photography license agreement", key="custom_type_input")
        parties = st.text_area(
            "Parties involved",
            placeholder="Jane Doe (Service Provider), TechNova Inc. (Client)",
            height=135,
            key="parties_input",
        )
    with right:
        st.markdown('<div class="form-column-title">Scope and terms</div>', unsafe_allow_html=True)
        dates = st.text_input("Effective date", placeholder="April 10, 2026", key="dates_input")
        terms = st.text_area(
            "Terms and conditions",
            placeholder="Payment within 30 days; confidentiality must be maintained; either party may terminate with 15 days notice",
            height=135,
            help="Separate individual terms with semicolons.",
            key="terms_input",
        )
        logo_file = st.file_uploader("Company logo (optional)", type=["png", "jpg", "jpeg"], key="logo_file_input")

    submitted = st.form_submit_button("Generate first draft", type="primary", use_container_width=True)

if submitted:
    document_type = custom_type.strip() if selected_type == "Custom Legal Document" else selected_type
    if not document_type or not parties.strip() or not terms.strip() or not dates.strip():
        st.error("Complete the document type, parties, terms, and effective date to continue.")
    else:
        try:
            with st.spinner("Building your first draft..."):
                response = _generate_document(document_type, parties, terms, dates)
            if response.ok:
                generated_document = response.json().get("text", "").strip()
                if not generated_document:
                    st.error("The backend returned an empty document. Please try again.")
                    st.stop()
                st.session_state.document = generated_document
                st.session_state.document_editor = generated_document
                st.session_state.terms = terms
                st.session_state.document_type = document_type
                st.rerun()
            else:
                try:
                    detail = response.json().get("detail", response.text)
                except Exception:
                    detail = response.text
                st.error(f"Backend error: {detail}")
        except requests.RequestException as exc:
            st.error(f"Could not connect to FastAPI at {BACKEND_URL}. Start the backend first. Details: {exc}")

if st.session_state.document:
    document = st.session_state.get("document_editor", st.session_state.document)
    word_count = len(document.split())
    st.markdown(
        f'<div class="section-rule"><h2>02 / Review the draft</h2><span>Generated document</span></div><div class="metric-strip"><div class="metric"><strong>{word_count:,}</strong><small>words</small></div><div class="metric"><strong>{len(document.splitlines()):,}</strong><small>lines</small></div><div class="metric"><strong>AI</strong><small>first pass</small></div></div>',
        unsafe_allow_html=True,
    )
    preview = format_html_preview(document)
    st.markdown(f'<div class="preview-shell">{preview}</div>', unsafe_allow_html=True)

    st.markdown('<div class="editor-label">Editable source</div>', unsafe_allow_html=True)
    edited = st.text_area(
        "Edit the generated text before exporting",
        height=500,
        label_visibility="collapsed",
        key="document_editor",
    )
    st.session_state.document = edited

    st.markdown('<div class="download-label">03 / Export your document</div>', unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3, gap="medium")
    logo_bytes = logo_file.getvalue() if logo_file is not None else b""
    logo_name = logo_file.name if logo_file is not None else ""
    txt_data, docx_data, pdf_data = _build_exports(
        edited,
        st.session_state.document_type,
        st.session_state.terms,
        logo_bytes,
        logo_name,
    )
    safe_name = _safe_filename(st.session_state.document_type)

    with d1:
        st.download_button("Download TXT", data=txt_data, file_name=f"{safe_name}.txt", mime="text/plain", use_container_width=True)
    with d2:
        st.download_button("Download DOCX", data=docx_data, file_name=f"{safe_name}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
    with d3:
        st.download_button("Download PDF", data=pdf_data, file_name=f"{safe_name}.pdf", mime="application/pdf", use_container_width=True)

st.markdown('<div class="footer">LEGAL<span>EASE</span> &nbsp; / &nbsp; AI-assisted drafting prototype &nbsp; / &nbsp; verify before signing</div>', unsafe_allow_html=True)
