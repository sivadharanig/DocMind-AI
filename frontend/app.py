import html
from collections import Counter
import pandas as pd
import streamlit as st
from api_client import backend_client

# ---------------------------------------------------------------------------
# DocMind AI — Enterprise Document Management & Conversational RAG
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="DocMind AI",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'mailto:support@docmind.ai',
        'Report a bug': 'mailto:bugs@docmind.ai',
        'About': "DocMind AI - Enterprise Document Management & RAG Platform"
    }
)

DEFAULTS = {
    "token": None,
    "user": None,
    "current_session_uuid": None,
    "chat_messages": [],
    "suggested_prompt": "",
    "dark_mode": False,
    "workspace_nav": "Documents",
    "dl_cache": {},
}
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)

# Modern Design Tokens
LIGHT = {
    "canvas": "#f8fafc",
    "surface": "#ffffff",
    "surface2": "#f1f5f9",
    "ink": "#0f172a",
    "muted": "#64748b",
    "faint": "#94a3b8",
    "line": "#e2e8f0",
    "accent": "#2563eb",
    "accent_h": "#1d4ed8",
    "accent_soft": "#eff6ff",
    "accent_ink": "#1e40af",
    "mark": "#fef3c7",
    "mark_ink": "#92400e",
    "ok": "#dcfce7",
    "ok_soft": "#15803d",
    "warn": "#ffedd5",
    "warn_soft": "#c2410c",
    "bad": "#fee2e2",
    "bad_soft": "#b91c1c",
    "shadow": "0 1px 3px 0 rgba(0, 0, 0, 0.08), 0 1px 2px 0 rgba(0, 0, 0, 0.04)",
    "shadow_md": "0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04)",
    "shadow_lg": "0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.03)",
    "side": "#ffffff",
    "side_hover": "#f8fafc",
    "side_active": "#eff6ff",
}

DARK = {
    "canvas": "#0b0f19",
    "surface": "#131b2e",
    "surface2": "#1e293b",
    "ink": "#f8fafc",
    "muted": "#94a3b8",
    "faint": "#64748b",
    "line": "#1e293b",
    "accent": "#3b82f6",
    "accent_h": "#60a5fa",
    "accent_soft": "#1e3a8a",
    "accent_ink": "#dbeafe",
    "mark": "#451a03",
    "mark_ink": "#fde68a",
    "ok": "#064e3b",
    "ok_soft": "#4ade80",
    "warn": "#78350f",
    "warn_soft": "#fdba74",
    "bad": "#7f1d1d",
    "bad_soft": "#f87171",
    "shadow": "0 1px 3px 0 rgba(0, 0, 0, 0.35)",
    "shadow_md": "0 4px 6px -1px rgba(0, 0, 0, 0.45)",
    "shadow_lg": "0 10px 15px -3px rgba(0, 0, 0, 0.55)",
    "side": "#0f172a",
    "side_hover": "#1e293b",
    "side_active": "#1e3a8a",
}

def inject_css():
    """Inject robust CSS design system across all pages"""
    t = DARK if st.session_state.get("dark_mode") else LIGHT
    css_vars = []
    for k, v in t.items():
        css_vars.append(f"--{k.replace('_', '-')}: {v};")
        css_vars.append(f"--{k}: {v};")
    root = "\n".join(css_vars)

    st.markdown(
        f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {{
{root}
--r: 12px;
}}

html, body, [class*="css"], [data-testid="stAppViewContainer"] {{
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    color: var(--ink);
    -webkit-font-smoothing: antialiased;
}}

.stApp {{
    background: var(--canvas);
    color: var(--ink);
}}

[data-testid="stHeader"] {{
    background: transparent;
    padding: 0.5rem 0;
}}

.block-container {{
    max-width: 1350px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    margin: 0 auto;
}}

h1, h2, h3, h4, h5, h6 {{
    font-family: 'Inter', sans-serif;
    color: var(--ink);
    font-weight: 700;
    line-height: 1.25;
    letter-spacing: -0.02em;
}}

h1 {{ font-size: clamp(1.8rem, 2.5vw, 2.4rem); margin-bottom: 0.75rem; }}
h2 {{ font-size: 1.5rem; margin-bottom: 0.5rem; }}
h3 {{ font-size: 1.2rem; margin-bottom: 0.4rem; }}
p, li, label {{ color: var(--ink); line-height: 1.6; font-size: 0.95rem; }}

[data-testid="stCaptionContainer"], .muted {{ color: var(--muted) !important; }}
.faint {{ color: var(--faint) !important; }}
a {{ color: var(--accent); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

/* Sidebar Navigation */
[data-testid="stSidebar"] {{
    background: var(--side);
    border-right: 1px solid var(--line);
}}

[data-testid="stSidebar"] [role="radiogroup"] {{
    gap: 6px;
    margin-top: 0.5rem;
}}

[data-testid="stSidebar"] [role="radiogroup"] label {{
    border-radius: var(--r);
    padding: 0.65rem 1rem;
    border: 1px solid var(--line);
    background: var(--surface);
    transition: all 0.15s ease;
    cursor: pointer;
    font-weight: 500;
    margin-bottom: 4px;
}}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {{
    background: var(--side-hover);
    border-color: var(--accent);
}}

.side-label {{
    color: var(--muted);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 1.2rem 0 0.5rem 0;
}}

/* Brand component */
.brand {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.25rem 0 1rem;
    margin-bottom: 0.75rem;
    border-bottom: 1px solid var(--line);
}}

.brand-mark {{
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-h) 100%);
    color: #ffffff;
    font-weight: 800;
    font-size: 1.3rem;
    display: grid;
    place-items: center;
    box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
}}

.brand-name {{
    font-size: 1.25rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--ink);
    line-height: 1.1;
}}

.brand-sub {{
    color: var(--muted);
    font-size: 0.75rem;
    font-weight: 500;
    margin-top: 2px;
}}

/* Page header */
.page-head {{
    margin-bottom: 1.75rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--line);
}}

.page-head .crumb {{
    color: var(--accent);
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.25rem;
}}

.page-head h1 {{
    margin: 0 0 0.25rem 0;
}}

.page-head p {{
    color: var(--muted);
    font-size: 0.95rem;
    margin: 0;
}}

/* Modern Empty State */
.empty {{
    text-align: center;
    padding: 2.5rem 1.5rem;
    border: 2px dashed var(--line);
    border-radius: var(--r);
    background: var(--surface2);
    margin: 1rem 0;
}}

.empty .card-title {{
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 0.25rem;
}}

.empty .card-sub {{
    color: var(--muted);
    font-size: 0.875rem;
}}

/* Metrics */
div[data-testid="stMetric"] {{
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--r);
    padding: 1rem 1.25rem;
    box-shadow: var(--shadow);
}}

div[data-testid="stMetricLabel"] p {{
    color: var(--muted) !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}

div[data-testid="stMetricValue"] {{
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    color: var(--ink) !important;
    letter-spacing: -0.02em;
}}

/* Status & Role Badges */
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    line-height: 1;
}}

.b-personal {{
    background: var(--warn);
    color: var(--warn-soft);
    border: 1px solid rgba(194, 65, 12, 0.25);
}}

.b-public {{
    background: var(--ok);
    color: var(--ok-soft);
    border: 1px solid rgba(21, 128, 61, 0.25);
}}

.b-neutral {{
    background: var(--accent-soft);
    color: var(--accent-ink);
    border: 1px solid rgba(30, 64, 175, 0.25);
}}

/* File Type Badges */
.ftype {{
    width: 44px;
    height: 44px;
    border-radius: 10px;
    display: grid;
    place-items: center;
    font-size: 0.78rem;
    font-weight: 800;
    flex: none;
    letter-spacing: 0.02em;
}}

.ft-pdf {{ background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }}
.ft-docx {{ background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; }}
.ft-txt {{ background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }}

/* Document Item Card */
.doc-card {{
    display: flex;
    gap: 12px;
    align-items: center;
    padding: 0.5rem 0;
}}

.doc-name {{
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--ink);
    overflow-wrap: anywhere;
    line-height: 1.3;
}}

.doc-meta {{
    color: var(--muted);
    font-size: 0.78rem;
    margin-top: 3px;
}}

/* RAG Source Chips & Snippets */
.src-chip {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--accent-soft);
    color: var(--accent-ink);
    border: 1px solid rgba(37, 99, 235, 0.2);
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 0.8rem;
    font-weight: 600;
    margin: 4px 6px 4px 0;
}}

.snippet {{
    border-left: 3px solid var(--accent);
    padding: 0.6rem 0.85rem;
    color: var(--ink);
    font-size: 0.85rem;
    margin: 0.5rem 0 0.75rem;
    background: var(--surface2);
    border-radius: 0 8px 8px 0;
    line-height: 1.5;
}}

/* Primary & Secondary Buttons */
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] button {{
    border-radius: var(--r);
    font-weight: 600;
    font-size: 0.88rem;
    transition: all 0.15s ease;
    padding: 0.55rem 1.25rem;
    font-family: 'Inter', sans-serif;
}}

.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"] {{
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: #ffffff !important;
    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.25);
}}

.stButton > button[kind="primary"]:hover {{
    background: var(--accent-h) !important;
    border-color: var(--accent-h) !important;
    box-shadow: 0 4px 8px rgba(37, 99, 235, 0.35);
}}

/* Input & Select fields */
.stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] > div {{
    border-radius: var(--r) !important;
    background: var(--surface) !important;
    color: var(--ink) !important;
    border: 1px solid var(--line) !important;
    font-size: 0.92rem;
}}

.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
}}

/* Chat bubbles */
[data-testid="stChatMessage"] {{
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--r);
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: var(--shadow);
}}

/* Expanders & Containers */
div[data-testid="stExpander"] {{
    border: 1px solid var(--line);
    border-radius: var(--r);
    background: var(--surface);
    box-shadow: var(--shadow);
}}

[data-testid="stTabs"] [role="tab"] {{
    font-weight: 600;
    font-size: 0.9rem;
    padding: 0.6rem 1.2rem;
}}

hr {{
    border: none;
    height: 1px;
    background: var(--line);
    margin: 1.5rem 0;
}}

footer {{ visibility: hidden; }}
</style>""",
        unsafe_allow_html=True,
    )

inject_css()

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def safe(value):
    """Safely escape HTML entities"""
    return html.escape(str(value if value is not None else ""))

def show_notification(message, type="info"):
    """Render a clean non-breaking notification toast"""
    try:
        icon_map = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
        st.toast(f"{icon_map.get(type, 'ℹ️')} {message}")
    except Exception:
        if type == "success":
            st.success(message)
        elif type == "error":
            st.error(message)
        elif type == "warning":
            st.warning(message)
        else:
            st.info(message)

def api_call(label, callback, *args, **kwargs):
    """Execute API call with structured error handling"""
    try:
        return callback(*args, **kwargs)
    except Exception as exc:
        err = f"{label} error: {str(exc)}"
        st.error(err)
        return {"success": False, "error": err}

def fmt_size(n):
    """Format byte counts into human-readable strings"""
    n = n or 0
    if n >= 1024 * 1024 * 1024:
        return f"{n / (1024 * 1024 * 1024):.1f} GB"
    if n >= 1024 * 1024:
        return f"{n / (1024 * 1024):.1f} MB"
    if n >= 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n} B"

def ext_of(doc):
    """Extract normalized file extension"""
    ft = str(doc.get("file_type", "")).lower().replace(".", "")
    if ft:
        return ft
    fn = str(doc.get("filename", ""))
    return fn.split(".")[-1].lower() if "." in fn else "txt"

def brand():
    """Render unified platform brand component"""
    st.markdown(
        '<div class="brand"><div class="brand-mark">D</div><div><div class="brand-name">DocMind AI</div>'
        '<div class="brand-sub">Enterprise Document Intelligence</div></div></div>',
        unsafe_allow_html=True,
    )

def page_head(crumb, title, description):
    """Render structured page header"""
    st.markdown(
        f'<div class="page-head"><div class="crumb">{safe(crumb)}</div><h1>{safe(title)}</h1><p>{safe(description)}</p></div>',
        unsafe_allow_html=True,
    )

def empty_state(title, body):
    """Render empty state card"""
    st.markdown(
        f'<div class="empty"><div class="card-title">{safe(title)}</div><div class="card-sub">{safe(body)}</div></div>',
        unsafe_allow_html=True
    )

def download_control(token, doc, key, full_width=False):
    """Controlled document download widget with caching"""
    uuid = doc.get("document_uuid")
    name = doc.get("filename", "document")
    cache = st.session_state["dl_cache"]

    if uuid in cache:
        col1, col2 = st.columns([1, 0.25])
        with col1:
            st.download_button("💾 Download", cache[uuid], file_name=name, key=f"dl_{key}", use_container_width=full_width)
        with col2:
            if st.button("↻", key=f"refresh_{key}", help="Refresh file cache"):
                cache.pop(uuid, None)
                st.rerun()
    else:
        if st.button("📥 Download", key=f"prep_{key}", use_container_width=full_width):
            with st.spinner("Retrieving file..."):
                data = backend_client.download_document(token, uuid)
                if data is None:
                    st.error("Document download failed.")
                else:
                    cache[uuid] = data
                    st.rerun()

def cb_new_chat():
    """Reset chat state for a fresh conversation"""
    st.session_state.update(
        workspace_nav="AI Assistant",
        current_session_uuid=None,
        chat_messages=[],
        suggested_prompt="",
    )
    show_notification("New chat conversation started.", "success")

def cb_upload():
    """Open document upload workflow"""
    st.session_state.update(
        workspace_nav="Documents",
        open_upload_panel=True,
    )

def set_logged_in(result):
    """Persist authenticated session state"""
    st.session_state["token"] = result["data"]["access_token"]
    st.session_state["user"] = result["data"]["user"]
    st.session_state.update(
        chat_messages=[],
        current_session_uuid=None,
        workspace_nav="Documents",
        dl_cache={},
    )
    show_notification(f"Welcome back, {st.session_state['user'].get('full_name')}!", "success")
    st.rerun()

@st.cache_data(ttl=15, show_spinner=False)
def cached_health(nonce):
    return backend_client.get_health()

# ---------------------------------------------------------------------------
# Authentication Page
# ---------------------------------------------------------------------------

def render_auth():
    """Render modern dual-pane authentication portal"""
    left, right = st.columns([1.15, 1], gap="large")

    with left:
        st.markdown(
            """<div style="background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #4f46e5 100%); background-color: #1e3a8a; color: #ffffff; border-radius: 24px; padding: 2.75rem 2.25rem; min-height: 570px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 20px 25px -5px rgba(30, 58, 138, 0.35), 0 8px 10px -6px rgba(30, 58, 138, 0.2); border: 1px solid rgba(255,255,255,0.18); position: relative; overflow: hidden;">
  <div>
    <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.18); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.28); border-radius: 9999px; padding: 6px 14px; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; margin-bottom: 1.5rem; color: #ffffff;">
      <span style="font-size: 0.95rem;">✨</span> Enterprise Document Intelligence
    </div>
    <h2 style="color: #ffffff !important; font-size: 2.2rem; font-weight: 800; line-height: 1.2; margin: 0 0 1rem 0; letter-spacing: -0.02em;">
      Transform Your Documents<br><span style="color: #93c5fd;">into Intelligent Insights</span>
    </h2>
    <p style="color: rgba(255,255,255,0.92) !important; font-size: 0.98rem; line-height: 1.6; margin: 0 0 2rem 0; max-width: 500px;">
      Upload PDFs, Word documents, and text files. Our AI analyzes your repository using grounded Retrieval-Augmented Generation (RAG) with verifiable citations.
    </p>
    <div style="display: flex; flex-direction: column; gap: 0.85rem; margin-bottom: 2rem;">
      <div style="display: flex; align-items: flex-start; gap: 14px; background: rgba(255,255,255,0.12); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.18); border-radius: 14px; padding: 12px 16px;">
        <span style="font-size: 1.5rem; line-height: 1;">📊</span>
        <div>
          <div style="color: #ffffff; font-weight: 700; font-size: 0.95rem;">Smart Semantic Analysis</div>
          <div style="color: rgba(255,255,255,0.82); font-size: 0.82rem; margin-top: 2px;">Recursive chunking with token boundary preservation & vector indexing</div>
        </div>
      </div>
      <div style="display: flex; align-items: flex-start; gap: 14px; background: rgba(255,255,255,0.12); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.18); border-radius: 14px; padding: 12px 16px;">
        <span style="font-size: 1.5rem; line-height: 1;">🔍</span>
        <div>
          <div style="color: #ffffff; font-weight: 700; font-size: 0.95rem;">Verifiable Source Citations</div>
          <div style="color: rgba(255,255,255,0.82); font-size: 0.82rem; margin-top: 2px;">Exact file, page, paragraph and relevance scoring in every response</div>
        </div>
      </div>
      <div style="display: flex; align-items: flex-start; gap: 14px; background: rgba(255,255,255,0.12); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.18); border-radius: 14px; padding: 12px 16px;">
        <span style="font-size: 1.5rem; line-height: 1;">🛡️</span>
        <div>
          <div style="color: #ffffff; font-weight: 700; font-size: 0.95rem;">Enterprise RBAC & Isolation</div>
          <div style="color: rgba(255,255,255,0.82); font-size: 0.82rem; margin-top: 2px;">Strict private vs public document vector scoping and security controls</div>
        </div>
      </div>
    </div>
  </div>
  <div style="display: flex; gap: 16px; flex-wrap: wrap; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 1.25rem;">
    <div style="display: inline-flex; align-items: center; gap: 6px; color: rgba(255,255,255,0.92); font-size: 0.82rem; font-weight: 600;">
      <span style="color: #4ade80; font-size: 1rem;">●</span> 100% Grounded
    </div>
    <div style="display: inline-flex; align-items: center; gap: 6px; color: rgba(255,255,255,0.92); font-size: 0.82rem; font-weight: 600;">
      <span style="color: #93c5fd; font-size: 1rem;">●</span> Zero Hallucination Mode
    </div>
    <div style="display: inline-flex; align-items: center; gap: 6px; color: rgba(255,255,255,0.92); font-size: 0.82rem; font-weight: 600;">
      <span style="color: #facc15; font-size: 1rem;">●</span> Multi-Format Ingestion
    </div>
  </div>
</div>""",
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        brand()

        login_tab, register_tab = st.tabs(["🔐 Sign In", "📝 Create Account"])

        with login_tab:
            with st.form("login_form", border=True):
                st.markdown("### Welcome back")
                st.caption("Sign in to access your enterprise workspace.")
                email = st.text_input("Email address", placeholder="admin@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

                if submitted:
                    if not email.strip() or not password:
                        st.warning("Please provide your email address and password.")
                    else:
                        with st.spinner("Verifying credentials..."):
                            result = api_call("Authentication", backend_client.login, email.strip(), password)
                        if result.get("success"):
                            set_logged_in(result)
                        else:
                            st.error(result.get("error", "Invalid email or password."))

        with register_tab:
            with st.form("register_form", border=True):
                st.markdown("### Create Account")
                st.caption("Register a new user account on the platform.")
                full_name = st.text_input("Full Name", placeholder="Jane Doe")
                email = st.text_input("Email address", placeholder="jane@example.com", key="reg_email")
                password = st.text_input("Password", type="password", placeholder="••••••••", key="reg_pass")
                submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)

                if submitted:
                    if not full_name.strip() or not email.strip() or not password:
                        st.warning("Please fill in all registration fields.")
                    else:
                        with st.spinner("Registering user..."):
                            result = api_call("Registration", backend_client.register, email.strip(), password, full_name.strip(), "USER")
                        if result.get("success"):
                            st.success("Account created successfully! You can now sign in.")
                        else:
                            st.error(result.get("error", "Registration failed."))

# ---------------------------------------------------------------------------
# Dialogs
# ---------------------------------------------------------------------------

def _find_updater():
    return (
        getattr(backend_client, "update_user", None)
        or getattr(backend_client, "update_admin_user", None)
        or getattr(backend_client, "edit_user", None)
    )

@st.dialog("Edit User Account", width="medium")
def edit_user_dialog(user_record, token):
    st.caption("Update user profile, permissions, or credentials.")
    with st.form(f"edit_user_form_{user_record.get('id')}"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full name", value=str(user_record.get("full_name") or ""))
        with col2:
            email = st.text_input("Email address", value=str(user_record.get("email") or ""))

        current_role = str(user_record.get("role") or "USER").upper()
        roles = ["USER", "ADMIN"]
        role_idx = roles.index(current_role) if current_role in roles else 0
        role = st.selectbox("Role", roles, index=role_idx)

        submitted = st.form_submit_button("Save Changes", type="primary", use_container_width=True)

    if submitted:
        if not full_name.strip() or not email.strip():
            st.warning("Name and email are required.")
            return
        updater = _find_updater()
        if not callable(updater):
            st.error("Admin user update service is not available.")
            return
        try:
            try:
                result = updater(token, user_record.get("id"), full_name=full_name.strip(), email=email.strip(), role=role)
            except TypeError:
                result = updater(token, user_record.get("id"), {"full_name": full_name.strip(), "email": email.strip(), "role": role})
        except Exception as e:
            st.error(f"Update failed: {str(e)}")
            return

        if isinstance(result, dict) and result.get("success"):
            show_notification("User account updated successfully.", "success")
            st.rerun()
        else:
            st.error(result.get("error", "Backend rejected update.") if isinstance(result, dict) else "Update failed.")

@st.dialog("Delete User Account", width="small")
def delete_user_dialog(user_record, token):
    st.warning(f"Permanently delete user account **{user_record.get('email')}**?")
    st.caption("All documents, vectors, and chat history owned by this user will be purged.")
    confirmed = st.checkbox("I confirm permanent deletion", key=f"del_u_{user_record.get('id')}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Delete User", type="primary", disabled=not confirmed, use_container_width=True):
            result = api_call("Delete User", backend_client.delete_user, token, user_record.get("id"))
            if isinstance(result, dict) and result.get("success"):
                show_notification("User purged successfully.", "success")
                st.rerun()
            else:
                st.error(result.get("error", "Failed to delete user."))
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

@st.dialog("Delete Document", width="small")
def delete_document_dialog(document, token):
    st.warning(f"Delete **{document.get('filename', 'this document')}**?")
    st.caption("Vector chunks and metadata will be permanently purged from ChromaDB and SQLite.")
    confirmed = st.checkbox("I confirm permanent removal", key=f"del_d_{document.get('document_uuid')}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Delete Document", type="primary", disabled=not confirmed, use_container_width=True):
            result = api_call("Delete Document", backend_client.delete_document, token, document.get("document_uuid"))
            if isinstance(result, dict) and result.get("success"):
                st.session_state["dl_cache"].pop(document.get("document_uuid"), None)
                show_notification("Document deleted successfully.", "success")
                st.rerun()
            else:
                st.error(result.get("error", "Delete failed."))
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

# ---------------------------------------------------------------------------
# Sidebar Navigation & Workspace Controls
# ---------------------------------------------------------------------------

def render_sidebar():
    """Render workspace sidebar navigation and profile controls"""
    user = st.session_state["user"]
    brand()

    nav = ["Documents", "AI Assistant"] + (["Admin"] if user.get("role") == "ADMIN" else [])
    labels = {"Documents": "📄 Documents", "AI Assistant": "🤖 AI Assistant", "Admin": "⚙️ Administration"}

    if st.session_state.get("workspace_nav") not in nav:
        st.session_state["workspace_nav"] = "Documents"

    selected = st.radio("Navigate", nav, label_visibility="collapsed", key="workspace_nav", format_func=labels.get)

    st.markdown('<div class="side-label">Quick Actions</div>', unsafe_allow_html=True)
    if st.button("➕ New Conversation", use_container_width=True, key="sb_btn_new_chat"):
        cb_new_chat()
    if st.button("📤 Upload Document", use_container_width=True, key="sb_btn_upload"):
        cb_upload()

    st.markdown('<div class="side-label">System Health</div>', unsafe_allow_html=True)
    nonce = st.session_state.get("health_nonce", 0)
    try:
        health = cached_health(nonce)
    except Exception:
        health = None
    online = isinstance(health, dict) and health.get("online")

    status_col1, status_col2 = st.columns([3, 1])
    with status_col1:
        if online:
            st.markdown('<span class="badge b-public">● Backend Online</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge b-personal">● Backend Offline</span>', unsafe_allow_html=True)
    with status_col2:
        if st.button("↻", key="refresh_api_health", help="Check server health"):
            st.session_state["health_nonce"] = nonce + 1
            st.rerun()

    st.markdown("---")

    initials = "".join(p[0] for p in str(user.get("full_name") or "User").split()[:2]).upper()
    st.markdown(
        f'<div class="doc-card"><div class="ftype ft-txt" style="border-radius:50%; font-size:1rem;">{safe(initials)}</div>'
        f'<div style="min-width:0"><div class="doc-name">{safe(user.get("full_name", "User"))}</div>'
        f'<div class="doc-meta">{safe(user.get("email", ""))}</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div style="margin:8px 0"><span class="badge b-neutral">{safe(user.get("role", "USER"))}</span></div>', unsafe_allow_html=True)

    if st.button("🚪 Sign Out", use_container_width=True, key="sb_signout"):
        for key in ("token", "user", "current_session_uuid"):
            st.session_state[key] = None
        st.session_state.update(chat_messages=[], dl_cache={})
        for key in ("suggested_prompt", "open_upload_panel"):
            st.session_state.pop(key, None)
        show_notification("Signed out successfully.", "info")
        st.rerun()

    return selected

# ---------------------------------------------------------------------------
# Documents Page
# ---------------------------------------------------------------------------

def render_documents():
    """Render documents repository, multi-format upload, and index management"""
    token = st.session_state["token"]
    user = st.session_state["user"]
    page_head("Workspace", "Document Repository", "Upload files, set visibility scopes, and manage content indexed for RAG retrieval.")

    all_docs = backend_client.list_documents(token, scope="all") or []
    personal_docs = [d for d in all_docs if str(d.get("visibility", "")).upper() == "PERSONAL" and str(d.get("owner_id", "")) == str(user.get("id", ""))]
    public_docs = [d for d in all_docs if str(d.get("visibility", "")).upper() == "PUBLIC"]
    total_bytes = sum((d.get("file_size_bytes") or 0) for d in all_docs)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Accessible Files", len(all_docs))
    m2.metric("Personal Files", len(personal_docs))
    m3.metric("Public Library", len(public_docs))
    m4.metric("Storage Used", fmt_size(total_bytes))

    st.markdown("")
    with st.expander("📤 Upload New Document", expanded=st.session_state.pop("open_upload_panel", False)):
        up_col, set_col = st.columns([2, 1], gap="large")
        with up_col:
            uploaded = st.file_uploader("Select PDF, DOCX or TXT file (up to 25 MB)", type=["pdf", "docx", "txt"], key="document_upload")
        with set_col:
            visibility = st.selectbox(
                "Access Scope", ["PERSONAL", "PUBLIC"],
                format_func=lambda v: "🔒 Personal (Only Me)" if v == "PERSONAL" else "🌍 Public (All Authorized Users)",
            )
            st.caption("Personal documents are strictly isolated to your own user ID. Public documents are indexed for team-wide queries.")

        if st.button("🚀 Upload & Index", type="primary", disabled=uploaded is None, key="btn_upload_doc"):
            payload = uploaded.getvalue() if uploaded is not None else b""
            if not payload:
                st.warning("Selected file is empty.")
            elif len(payload) > 25 * 1024 * 1024:
                st.warning("File exceeds 25 MB limit.")
            else:
                with st.spinner("Extracting text, chunking, and indexing into vector store..."):
                    result = api_call("Document Ingestion", backend_client.upload_document, token, uploaded.name, payload, visibility)
                if result.get("success"):
                    show_notification(f"Uploaded and indexed '{uploaded.name}' successfully!", "success")
                    st.rerun()
                else:
                    st.error(result.get("error", "Upload failed."))

    if all_docs:
        mix = Counter(ext_of(d).upper() or "OTHER" for d in all_docs)
        with st.expander("📊 Library Format Distribution", expanded=False):
            st.bar_chart(pd.DataFrame({"Count": mix}), horizontal=True, height=130, color="#2563eb")

    st.markdown("### 📚 Document Library")
    search_col, type_col, view_col = st.columns([2.5, 1, 1])
    with search_col:
        search = st.text_input("Search", placeholder="Search by filename...", key="document_search", label_visibility="collapsed")
    with type_col:
        file_type = st.selectbox("Format", ["All formats", "PDF", "DOCX", "TXT"], key="document_type", label_visibility="collapsed")
    with view_col:
        view = st.radio("View", ["Table", "Cards"], horizontal=True, key="document_view", label_visibility="collapsed")

    tabs = st.tabs([f"🔒 Personal ({len(personal_docs)})", f"🌍 Public ({len(public_docs)})", f"📋 All Files ({len(all_docs)})"])

    def show_docs(docs, prefix):
        filtered = [
            d for d in docs
            if search.lower() in str(d.get("filename", "")).lower()
            and (file_type == "All formats" or ext_of(d) == file_type.lower())
        ]
        if not filtered:
            empty_state("No Documents Found", "No documents matched your current search and format filters.")
            return

        if view == "Table":
            rows = [{
                "Filename": d.get("filename", "Untitled"),
                "Format": ext_of(d).upper(),
                "Visibility": str(d.get("visibility", "")).title(),
                "Size": fmt_size(d.get("file_size_bytes")),
                "Added": str(d.get("created_at", ""))[:10] or "—",
            } for d in filtered]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            with st.container(border=True):
                st.markdown("**Inspect & Manage Selected Document**")
                idx = st.selectbox(
                    "Choose Document", list(range(len(filtered))),
                    format_func=lambda i: filtered[i].get("filename", "Untitled"),
                    key=f"{prefix}_tbl_select",
                )
                sel = filtered[idx]
                col1, col2, col3 = st.columns([1, 1.4, 1], gap="medium")
                with col1:
                    st.caption("Download")
                    download_control(token, sel, f"{prefix}_tbl_{sel.get('document_uuid')}", full_width=True)
                with col2:
                    st.caption("Change Scope")
                    vis_col1, vis_col2 = st.columns([1.3, 1])
                    new_vis = vis_col1.selectbox(
                        "Visibility", ["PERSONAL", "PUBLIC"],
                        index=0 if sel.get("visibility") == "PERSONAL" else 1,
                        key=f"{prefix}_vis_{sel.get('document_uuid')}",
                        label_visibility="collapsed",
                    )
                    if vis_col2.button("Save", key=f"{prefix}_btn_save_vis_{sel.get('document_uuid')}", use_container_width=True):
                        result = backend_client.update_document(token, sel["document_uuid"], visibility=new_vis)
                        if result.get("success"):
                            show_notification("Document visibility updated.", "success")
                            st.rerun()
                        else:
                            st.error(result.get("error", "Update failed."))
                with col3:
                    st.caption("Danger Zone")
                    if st.button("Delete", key=f"{prefix}_tbl_del_{sel.get('document_uuid')}", use_container_width=True):
                        delete_document_dialog(sel, token)
        else:
            # 3-column Card Grid with clean containers
            cols = st.columns(3)
            for i, doc in enumerate(filtered):
                with cols[i % 3]:
                    with st.container(border=True):
                        ext = ext_of(doc)
                        cls = {"pdf": "ft-pdf", "docx": "ft-docx"}.get(ext, "ft-txt")
                        pub = str(doc.get("visibility", "")).upper() == "PUBLIC"

                        st.markdown(
                            f'<div class="doc-card"><div class="ftype {cls}">{safe(ext.upper())}</div>'
                            f'<div style="min-width:0"><div class="doc-name">{safe(doc.get("filename", "Untitled"))}</div>'
                            f'<div class="doc-meta">{fmt_size(doc.get("file_size_bytes"))} · {safe(str(doc.get("created_at", ""))[:10])}</div></div></div>',
                            unsafe_allow_html=True,
                        )
                        badge_html = f'<span class="badge b-public">🌍 Public</span>' if pub else f'<span class="badge b-personal">🔒 Personal</span>'
                        st.markdown(f'<div style="margin: 8px 0 12px 0;">{badge_html}</div>', unsafe_allow_html=True)

                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            download_control(token, doc, f"{prefix}_card_{doc['document_uuid']}", full_width=True)
                        with btn_col2:
                            if st.button("Delete", key=f"{prefix}_c_del_{doc['document_uuid']}", use_container_width=True):
                                delete_document_dialog(doc, token)

    with tabs[0]:
        show_docs(personal_docs, "personal")
    with tabs[1]:
        show_docs(public_docs, "public")
    with tabs[2]:
        show_docs(all_docs, "all")

# ---------------------------------------------------------------------------
# AI Assistant & Conversational RAG
# ---------------------------------------------------------------------------

def render_chat():
    """Render RAG conversational assistant with verified citations"""
    token = st.session_state["token"]
    page_head("Workspace", "AI Conversational Assistant", "Ask questions across your documents. Answers include verifiable source citations.")

    col1, col2 = st.columns([2.5, 1], gap="large")
    with col1:
        search_mode = st.radio(
            "Search Scope", ["PRIVATE", "PUBLIC", "COMBINED"], horizontal=True, key="chat_search_mode",
            format_func=lambda v: {"PRIVATE": "🔒 Personal Documents", "PUBLIC": "🌍 Public Library", "COMBINED": "📋 Entire Repository"}[v],
        )
    with col2:
        if st.button("➕ New Chat Session", use_container_width=True, type="primary"):
            result = backend_client.create_chat_session(token, search_mode=search_mode)
            st.session_state["current_session_uuid"] = result.get("session_uuid") if result else None
            st.session_state["chat_messages"] = []
            show_notification("Started new chat session.", "success")
            st.rerun()

    with st.expander("📝 Previous Conversation Sessions", expanded=False):
        sessions = backend_client.list_chat_sessions(token) or []
        if sessions:
            labels = {f"{str(s.get('created_at', ''))[:19].replace('T', ' ')} · {s.get('session_uuid', '')[:8]}": s.get("session_uuid") for s in sessions}
            chosen = st.selectbox("Select Session", list(labels.keys()), key="chat_history_select")
            if st.button("📂 Load Session", key="btn_load_chat"):
                uuid = labels[chosen]
                session = backend_client.get_chat_session(token, uuid)
                if session:
                    st.session_state["current_session_uuid"] = uuid
                    st.session_state["chat_messages"] = [
                        {"role": m.get("sender_role", "assistant").lower(), "content": m.get("message_text", ""), "sources": m.get("source_documents", [])}
                        for m in session.get("messages", [])
                    ]
                    st.rerun()
        else:
            st.caption("No previous chat history found.")

    if not st.session_state["chat_messages"]:
        empty_state("Start a Conversation", "Select a search scope and ask any question grounded in your uploaded documents.")
        st.markdown("**Suggested queries:**")
        prompts = [
            "What are the main topics and objectives discussed in the uploaded documents?",
            "Summarize the key requirements and constraints outlined in the files.",
            "List any financial, budgetary, or deadline specifications found in the documents."
        ]
        p_cols = st.columns(3)
        for i, p in enumerate(prompts):
            if p_cols[i].button(p, key=f"sug_prompt_{i}", use_container_width=True):
                st.session_state["suggested_prompt"] = p
                st.rerun()

    for mi, msg in enumerate(st.session_state["chat_messages"]):
        role = "user" if msg.get("role") == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(msg.get("content", ""))
            sources = msg.get("sources") or []
            if role == "assistant" and sources:
                chips_html = "".join(f'<span class="src-chip">📄 {safe(s.get("filename", "Document"))}</span>' for s in sources)
                st.markdown(f'<div style="margin-top: 8px;">{chips_html}</div>', unsafe_allow_html=True)
                with st.expander(f"🔍 Grounded Source Citations ({len(sources)} references)"):
                    for si, s in enumerate(sources):
                        fname = s.get("filename", "Source Document")
                        st.markdown(f"**{safe(fname)}**")
                        if s.get("snippet"):
                            st.markdown(f'<div class="snippet">{safe(s["snippet"])}</div>', unsafe_allow_html=True)
                        if s.get("document_uuid"):
                            download_control(token, {"document_uuid": s["document_uuid"], "filename": fname}, f"chat_src_{mi}_{si}")

    prompt = st.chat_input("Ask a question about your documents...")
    if not prompt and st.session_state.get("suggested_prompt"):
        prompt = st.session_state["suggested_prompt"]
        st.session_state["suggested_prompt"] = ""

    if prompt:
        st.session_state["chat_messages"].append({"role": "user", "content": prompt, "sources": []})
        with st.spinner("Searching semantic embeddings and generating grounded answer..."):
            result = api_call(
                "RAG Retrieval", backend_client.query_rag_chat,
                token=token, query=prompt, search_mode=search_mode,
                session_uuid=st.session_state.get("current_session_uuid"),
            )
        if result.get("success"):
            data = result["data"]
            st.session_state["current_session_uuid"] = data.get("session_uuid")
            st.session_state["chat_messages"].append({
                "role": "assistant",
                "content": data.get("answer", "No answer was returned."),
                "sources": data.get("sources", []),
            })
            st.rerun()
        else:
            st.error(result.get("error", "Failed to retrieve grounded answer."))

# ---------------------------------------------------------------------------
# Administration Portal
# ---------------------------------------------------------------------------

def render_admin():
    """Render platform administration, AI status, and user management"""
    token = st.session_state["token"]
    user = st.session_state["user"]
    page_head("Workspace", "Platform Administration", "Monitor system analytics, configure AI engine credentials, and manage user accounts.")

    overview_tab, ai_tab, users_tab = st.tabs(["📊 Analytics Overview", "🤖 AI Engine & Provider", "👥 User Management"])

    with overview_tab:
        stats = backend_client.get_admin_stats(token) or {}
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Registered Users", stats.get("total_users", 0))
        c2.metric("Total Documents", stats.get("total_documents", 0))
        c3.metric("Vector Chunks", stats.get("total_chunks", 0))
        c4.metric("Chat Messages", stats.get("total_messages", 0))

        st.markdown("")
        chart = pd.DataFrame({"Count": {
            "Users": stats.get("total_users", 0),
            "Documents": stats.get("total_documents", 0),
            "Chunks": stats.get("total_chunks", 0),
            "Messages": stats.get("total_messages", 0),
        }})
        with st.container(border=True):
            st.markdown("**Platform Activity Totals**")
            st.bar_chart(chart, height=220, color="#2563eb")

    with ai_tab:
        status = backend_client.get_ai_status(token) or {}
        left, right = st.columns(2, gap="large")
        with left:
            with st.container(border=True):
                st.markdown("**AI Provider Connection Status**")
                state = status.get("status", "unknown")
                if state == "connected":
                    st.success("✅ OpenAI Cloud Engine Connected")
                elif state == "invalid_key":
                    st.warning("⚠️ OpenAI API Key Invalid or Inactive")
                elif state == "error":
                    st.error("❌ Connection Check Error")
                else:
                    st.info("ℹ️ Local Deterministic Fallback Mode Active")
                st.caption(status.get("message", "No status details available."))
        with right:
            with st.container(border=True):
                st.markdown("**Update OpenAI API Key**")
                with st.form("form_update_ai_key"):
                    api_key = st.text_input("API Key", type="password", placeholder="sk-...")
                    submitted = st.form_submit_button("Verify & Activate", type="primary", use_container_width=True)
                if submitted:
                    if not api_key.strip():
                        st.warning("Please provide a valid API key.")
                    else:
                        res = api_call("AI Key Update", backend_client.update_ai_key, token, api_key.strip())
                        if res.get("success"):
                            show_notification("API key updated successfully!", "success")
                            st.rerun()
                        else:
                            st.error(res.get("error", "Failed to update key."))

    with users_tab:
        users = api_call("User Retrieval", backend_client.get_admin_users_overview, token) or []
        if not users or isinstance(users, dict):
            st.info("No user records available.")
            return

        user_df = pd.DataFrame(users)
        q = st.text_input("Search Users", placeholder="Search by name or email...", key="admin_user_search", label_visibility="collapsed")
        preferred = ["id", "full_name", "email", "role", "created_at"]
        columns = [c for c in preferred if c in user_df.columns] + [c for c in user_df.columns if c not in preferred]
        editor_df = user_df[columns].copy()

        if q.strip():
            mask = pd.Series(False, index=editor_df.index)
            for col in ("full_name", "email"):
                if col in editor_df.columns:
                    mask |= editor_df[col].astype(str).str.contains(q.strip(), case=False, na=False)
            editor_df = editor_df[mask]

        config = {
            "id": st.column_config.TextColumn("User ID"),
            "full_name": st.column_config.TextColumn("Full Name"),
            "email": st.column_config.TextColumn("Email Address"),
            "role": st.column_config.SelectboxColumn("Role", options=["USER", "ADMIN"]),
        }
        if "created_at" in editor_df.columns:
            config["created_at"] = st.column_config.TextColumn("Created At")

        editable = [f for f in ("full_name", "email", "role") if f in editor_df.columns]
        st.caption("Edit account details directly in the table below, then click **Save Table Changes**.")
        edited_df = st.data_editor(
            editor_df, use_container_width=True, hide_index=True, num_rows="fixed",
            key="admin_users_inline_editor", disabled=[c for c in columns if c not in editable], column_config=config,
        )

        if st.button("💾 Save Table Changes", type="primary", key="btn_save_user_table"):
            updater = _find_updater()
            if not callable(updater):
                st.error("User update method not available.")
            else:
                original_by_id = {str(u.get("id")): u for u in users}
                saved, failures = 0, []
                for _, row in edited_df.iterrows():
                    uid = str(row.get("id", ""))
                    orig = original_by_id.get(uid)
                    if not orig:
                        continue
                    changes = {}
                    for field in editable:
                        old, new = orig.get(field), row.get(field)
                        if pd.isna(new):
                            new = None
                        elif field == "role" and new is not None:
                            new = str(new).upper()
                        elif new is not None:
                            new = str(new).strip()
                        if old != new:
                            changes[field] = new
                    if not changes:
                        continue
                    try:
                        try:
                            result = updater(token, orig.get("id"), **changes)
                        except TypeError:
                            result = updater(token, orig.get("id"), changes)
                        if isinstance(result, dict) and result.get("success"):
                            saved += 1
                        else:
                            failures.append(str(orig.get("email") or uid))
                    except Exception:
                        failures.append(str(orig.get("email") or uid))
                if failures:
                    st.warning(f"Saved {saved} account(s). Could not save: {', '.join(failures)}.")
                elif saved:
                    show_notification(f"Updated {saved} account(s) successfully.", "success")
                    st.rerun()
                else:
                    st.info("No modifications detected.")

        st.markdown("### 👤 User Actions")
        eligible = [u for u in users if str(u.get("id")) != str(user.get("id"))]
        if eligible:
            options = {f"{u.get('full_name') or 'User'} ({u.get('email', '')})": u for u in eligible}
            label = st.selectbox("Select Account", list(options.keys()), key="admin_selected_user")
            target = options[label]
            col1, col2, col3 = st.columns([1, 1, 2])
            if col1.button("✏️ Edit Account", type="primary", use_container_width=True):
                edit_user_dialog(target, token)
            if col2.button("🗑️ Delete Account", use_container_width=True):
                delete_user_dialog(target, token)
            col3.caption("Your own administrator account cannot be self-deleted.")
        else:
            st.caption("No other user accounts currently exist.")

# ---------------------------------------------------------------------------
# Main Routing Logic
# ---------------------------------------------------------------------------

if not st.session_state.get("token"):
    render_auth()
else:
    with st.sidebar:
        page = render_sidebar()

    if page == "Documents":
        render_documents()
    elif page == "AI Assistant":
        render_chat()
    elif page == "Admin":
        if st.session_state["user"].get("role") == "ADMIN":
            render_admin()
        else:
            st.error("Access denied. Administrator privileges required.")
