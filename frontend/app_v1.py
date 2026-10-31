import html

from collections import Counter



import pandas as pd

import streamlit as st

from api_client import backend_client



# ---------------------------------------------------------------------------

# DocMind AI — v3 workspace UI with improved UI/UX

# Modern design with better accessibility, visual hierarchy, and user experience

# Improvements include:

#   * Enhanced visual design with modern color palette

#   * Improved component styling with better spacing and typography

#   * Better responsive design

#   * Enhanced accessibility features

#   * Modern UI patterns and micro-interactions

#   * Improved dark mode implementation

#   * Better error handling and user feedback

# ---------------------------------------------------------------------------



st.set_page_config(

    page_title="DocMind AI", 

    page_icon="◆", 

    layout="wide", 

    initial_sidebar_state="expanded",

    menu_items={

        'Get Help': 'mailto:support@docmind.ai',

        'Report a bug': 'mailto:bugs@docmind.ai',

        'About': "DocMind AI - Advanced Document Analysis Platform"

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

    "notification": None,

    "notification_type": None,

}

for k, v in DEFAULTS.items():

    st.session_state.setdefault(k, v)



# Modern color palette with better contrast and accessibility

LIGHT = dict(

    # Base colors

    canvas="#f8f9fa",  # Light background

    surface="#ffffff",  # White cards

    surface2="#f1f3f4",  # Secondary surfaces

    ink="#1a1a1a",  # Primary text

    muted="#6b7280",  # Secondary text

    faint="#9ca3af",  # Faint text

    line="#e5e7eb",  # Dividers/borders

    accent="#3b82f6",  # Primary accent (blue)

    accent_h="#2563eb",  # Accent hover

    accent_soft="#dbeafe",  # Accent background

    accent_ink="#1e40af",  # Accent text



    # Status colors

    mark="#fef3c7",  # Highlight/marker

    mark_ink="#92400e",  # Marker text

    ok="#d1fae5",  # Success

    ok_soft="#10b981",  # Success text

    warn="#fed7aa",  # Warning

    warn_soft="#f59e0b",  # Warning text

    bad="#fee2e2",  # Error

    bad_soft="#ef4444",  # Error text



    # Shadows

    shadow="0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",

    shadow_md="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",

    shadow_lg="0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",



    # Sidebar

    side="#ffffff",  # Sidebar background

    side_hover="#f3f4f6",  # Sidebar hover

    side_active="#dbeafe",  # Sidebar active

)



DARK = dict(

    # Base colors

    canvas="#0f172a",  # Dark background

    surface="#1e293b",  # Card background

    surface2="#334155",  # Secondary surfaces

    ink="#f1f5f9",  # Primary text

    muted="#94a3b8",  # Secondary text

    faint="#cbd5e1",  # Faint text

    line="#334155",  # Dividers/borders

    accent="#60a5fa",  # Primary accent (blue)

    accent_h="#3b82f6",  # Accent hover

    accent_soft="#1e3a8a",  # Accent background

    accent_ink="#eff6ff",  # Accent text



    # Status colors

    mark="#451a03",  # Highlight/marker

    mark_ink="#fbbf24",  # Marker text

    ok="#064e3b",  # Success

    ok_soft="#10b981",  # Success text

    warn="#78350f",  # Warning

    warn_soft="#f59e0b",  # Warning text

    bad="#7f1d1d",  # Error

    bad_soft="#ef4444",  # Error text



    # Shadows

    shadow="0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 1px 2px 0 rgba(0, 0, 0, 0.2)",

    shadow_md="0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3)",

    shadow_lg="0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.4)",



    # Sidebar

    side="#1e293b",  # Sidebar background

    side_hover="#334155",  # Sidebar hover

    side_active="#1e3a8a",  # Sidebar active

)





def inject_css():

    """Inject improved CSS with modern design patterns"""

    t = DARK if st.session_state.get("dark_mode") else LIGHT

    css_vars = []
    for k, v in t.items():
        css_vars.append(f"--{k.replace('_', '-')}: {v};")
        css_vars.append(f"--{k}: {v};")
    root = "\n".join(css_vars)



    st.markdown(

        f"""

<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');



:root {{ {root} --r: 12px; }}

html, body, [class*="css"], [data-testid="stAppViewContainer"] {{ 

    font-family: 'Inter', system-ui, -apple-system, sans-serif; 

    color: var(--ink);

    -webkit-font-smoothing: antialiased;

    -moz-osx-font-smoothing: grayscale;

}}



/* Base app styling */

.stApp {{ 

    background: var(--canvas); 

    color: var(--ink);

    background-attachment: fixed;

}}



[data-testid="stHeader"] {{ 

    background: transparent; 

    padding: 1rem 0;

}}



.block-container {{ 

    max-width: 1400px; 

    padding-top: 1.5rem; 

    padding-bottom: 3rem;

    margin: 0 auto;

}}



/* Typography improvements */

h1, h2, h3, h4, h5, h6 {{ 

    font-family: 'Inter', system-ui, -apple-system, sans-serif; 

    color: var(--ink); 

    font-weight: 700;

    line-height: 1.2;

    letter-spacing: -0.02em;

}}



h1 {{ 

    font-size: clamp(2rem, 3vw, 2.75rem); 

    margin-bottom: 1rem;

}}



h2 {{ 

    font-size: 1.75rem; 

    margin-bottom: 0.75rem;

}}



h3 {{ 

    font-size: 1.25rem; 

    margin-bottom: 0.5rem;

}}



p, li, label, .stMarkdown {{ 

    color: var(--ink); 

    line-height: 1.6;

}}



/* Color utilities */

[data-testid="stCaptionContainer"], .muted {{ 

    color: var(--muted) !important; 

}}



.faint {{ 

    color: var(--faint) !important; 

}}



a {{ 

    color: var(--accent); 

    text-decoration: none;

    transition: opacity 0.2s ease;

}}



a:hover {{ 

    opacity: 0.8;

}}



/* Modern sidebar styling */

[data-testid="stSidebar"] {{ 

    background: var(--side); 

    border-right: 1px solid var(--line);

    padding: 0;

    height: 100vh;

    overflow-y: auto;

}}



[data-testid="stSidebar"] > div:first-child {{ 

    padding: 1.5rem 1rem 1rem;

}}



[data-testid="stSidebar"] [role="radiogroup"] {{ 

    gap: 0.5rem;

    margin-top: 1rem;

}}



[data-testid="stSidebar"] [role="radiogroup"] label {{ 

    border-radius: var(--r); 

    padding: 0.75rem 1rem; 

    border: 1px solid transparent;

    transition: all 0.2s ease;

    cursor: pointer;

    background: var(--surface);

    margin: 0;

}}



[data-testid="stSidebar"] [role="radiogroup"] label:hover {{ 

    background: var(--side-hover);

    border-color: var(--line);

    transform: translateX(2px);

}}



[data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] {{ 

    background: var(--accent-soft); 

    border-color: var(--accent);

    color: var(--accent-ink);

    font-weight: 600;

    box-shadow: var(--shadow);

}}



[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {{ 

    display: none; 

}}



/* Modern sidebar sections */

.side-section {{ 

    margin: 1.5rem 0;

    padding: 0 1rem;

}}



.side-label {{ 

    color: var(--muted); 

    font-size: 11px; 

    font-weight: 600; 

    letter-spacing: 0.08em;

    text-transform: uppercase;

    margin-bottom: 0.75rem;

    padding: 0 0.5rem;

}}



/* Enhanced brand styling */

.brand {{ 

    display: flex; 

    align-items: center; 

    gap: 12px; 

    padding: 0.5rem 1rem 1.5rem;

    margin-bottom: 1rem;

    border-bottom: 1px solid var(--line);

}}



.brand-mark {{ 

    width: 44px; 

    height: 44px; 

    border-radius: 12px; 

    background: var(--accent); 

    color: var(--canvas); 

    display: grid; 

    place-items: center;

    font-family: 'Inter', sans-serif;

    font-weight: 700; 

    font-size: 20px;

    box-shadow: var(--shadow);

}}



.brand-name {{ 

    font-family: 'Inter', sans-serif; 

    font-size: 1.25rem; 

    font-weight: 700; 

    letter-spacing: -0.01em; 

    line-height: 1.2;

}}



.brand-sub {{ 

    color: var(--muted); 

    font-size: 0.75rem; 

    margin-top: 2px;

}}



/* Modern page header */

.page-head {{ 

    margin-bottom: 2rem;

    padding: 0 1rem;

}}



.page-head .crumb {{ 

    color: var(--muted); 

    font-size: 0.875rem; 

    font-weight: 500;

    margin-bottom: 0.5rem;

}}



.page-head h1 {{ 

    font-size: 2rem;

    font-weight: 700;

    margin-bottom: 0.5rem;

}}



.page-head p {{ 

    color: var(--muted); 

    max-width: 720px; 

    margin: 0;

    font-size: 1rem;

    line-height: 1.6;

}}



/* Enhanced card styling */

.card {{ 

    background: var(--surface); 

    border: 1px solid var(--line); 

    border-radius: var(--r); 

    padding: 1.5rem;

    box-shadow: var(--shadow);

    transition: all 0.2s ease;

}}



.card:hover {{ 

    box-shadow: var(--shadow_md);

    transform: translateY(-1px);

}}



.card + .card {{ 

    margin-top: 1rem;

}}



.card-title {{ 

    font-weight: 600; 

    font-size: 1rem; 

    margin-bottom: 0.5rem;

    color: var(--ink);

}}



.card-sub {{ 

    color: var(--muted); 

    font-size: 0.875rem; 

    line-height: 1.5;

}}



/* Enhanced empty state */

.empty {{ 

    text-align: center; 

    padding: 3rem 2rem; 

    border: 2px dashed var(--line); 

    border-radius: var(--r); 

    background: var(--surface2);

    transition: all 0.2s ease;

}}



.empty:hover {{ 

    border-color: var(--accent);

    background: var(--surface);

}}



.empty .card-title {{ 

    font-size: 1.125rem;

    font-weight: 600;

    margin-bottom: 0.5rem;

}}



/* Modern metric styling */

div[data-testid="stMetric"] {{ 

    background: var(--surface); 

    border: 1px solid var(--line); 

    border-radius: var(--r); 

    padding: 1.25rem;

    box-shadow: var(--shadow);

    transition: all 0.2s ease;

}}



div[data-testid="stMetric"]:hover {{ 

    box-shadow: var(--shadow_md);

    transform: translateY(-1px);

}}



div[data-testid="stMetricLabel"] p {{ 

    color: var(--muted); 

    font-size: 0.875rem; 

    font-weight: 500;

    text-transform: uppercase;

    letter-spacing: 0.05em;

}}



div[data-testid="stMetricValue"] {{ 

    font-family: 'Inter', sans-serif; 

    font-size: 2rem; 

    font-weight: 700; 

    letter-spacing: -0.02em; 

    color: var(--ink);

    margin-top: 0.25rem;

}}



/* Modern badge styling */

.badge {{ 

    display: inline-flex; 

    align-items: center; 

    gap: 0.375rem; 

    padding: 0.375rem 0.75rem; 

    border-radius: 9999px; 

    font-size: 0.75rem; 

    font-weight: 500;

    font-family: 'Inter', sans-serif;

    transition: all 0.2s ease;

}}



.badge:hover {{ 

    transform: scale(1.05);

}}



.b-personal {{ 

    background: var(--warn-soft); 

    color: var(--warn);

}}



.b-public {{ 

    background: var(--ok-soft); 

    color: var(--ok);

}}



.b-neutral {{ 

    background: var(--accent-soft); 

    color: var(--accent-ink);

}}



/* File type badges */

.ftype {{ 

    width: 48px; 

    height: 48px; 

    border-radius: 12px; 

    display: grid; 

    place-items: center; 

    font-size: 0.875rem; 

    font-weight: 600; 

    flex: none;

    transition: all 0.2s ease;

}}



.ftype:hover {{ 

    transform: scale(1.1);

}}



.ft-pdf {{ 

    background: var(--bad-soft); 

    color: var(--bad);

}}



.ft-docx {{ 

    background: #dbeafe; 

    color: #1e40af;

}}



.ft-txt {{ 

    background: var(--accent-soft); 

    color: var(--accent-ink);

}}



/* Modern document card */

.doc-card {{ 

    display: flex; 

    gap: 1rem; 

    align-items: center;

    padding: 0.75rem;

    border-radius: var(--r);

    transition: all 0.2s ease;

    background: var(--surface);

    border: 1px solid var(--line);

    margin-bottom: 0.75rem;

}}



.doc-card:hover {{ 

    background: var(--surface2);

    box-shadow: var(--shadow);

}}



.doc-name {{ 

    font-weight: 600; 

    overflow-wrap: anywhere; 

    line-height: 1.4;

    flex: 1;

}}



.doc-meta {{ 

    color: var(--muted); 

    font-size: 0.75rem; 

    margin-top: 0.25rem;

}}



/* Enhanced source chips */

.src-chip {{ 

    display: inline-flex; 

    gap: 0.5rem; 

    align-items: center; 

    background: var(--mark); 

    color: var(--mark-ink); 

    border-radius: 8px; 

    padding: 0.5rem 0.75rem; 

    font-size: 0.875rem; 

    font-weight: 500; 

    margin: 0 0.5rem 0.5rem 0;

    transition: all 0.2s ease;

}}



.src-chip:hover {{ 

    transform: translateY(-1px);

    box-shadow: var(--shadow);

}}



.snippet {{ 

    border-left: 3px solid var(--mark); 

    padding: 0.75rem 0 0.75rem 1rem; 

    color: var(--muted); 

    font-size: 0.875rem; 

    margin: 0.75rem 0 1rem;

    background: var(--surface2);

    border-radius: 0 0.5rem 0.5rem 0;

}}



/* Modern auth panel */

.auth-panel, div[class*="auth-panel"] {{ 

    background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #4f46e5 100%) !important;

    background-color: #1e3a8a !important;

    color: #ffffff !important; 

    border-radius: 24px !important; 

    padding: clamp(2rem, 4vw, 3rem) !important; 

    min-height: 560px !important; 

    display: flex !important; 

    flex-direction: column !important; 

    justify-content: space-between !important; 

    gap: 1.5rem !important;

    box-shadow: 0 20px 25px -5px rgba(30, 58, 138, 0.35), 0 8px 10px -6px rgba(30, 58, 138, 0.2) !important;

    position: relative !important;

    overflow: hidden !important;

    border: 1px solid rgba(255, 255, 255, 0.18) !important;

}}



.auth-panel::before {{

    content: '';

    position: absolute;

    top: -50%;

    right: -50%;

    width: 200%;

    height: 200%;

    background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%);

    pointer-events: none;

    z-index: 0;

}}



.auth-panel h2 {{ 

    color: #ffffff !important; 

    font-size: clamp(1.8rem, 3vw, 2.4rem) !important; 

    font-weight: 800 !important;

    line-height: 1.2 !important; 

    margin: 0 0 1rem 0 !important;

    position: relative !important;

    z-index: 1 !important;

    letter-spacing: -0.02em !important;

}}



.auth-panel p {{ 

    color: rgba(255, 255, 255, 0.92) !important; 

    font-size: 0.98rem !important;

    line-height: 1.6 !important;

    margin: 0 !important; 

    max-width: 520px !important; 

    position: relative !important;

    z-index: 1 !important;

}}



/* Modern demo cards */

.demo {{ 

    background: var(--surface); 

    color: var(--ink); 

    border-radius: 16px; 

    padding: 1.5rem; 

    box-shadow: var(--shadow_md);

    transition: all 0.2s ease;

}}



.demo:hover {{ 

    box-shadow: var(--shadow_lg);

    transform: translateY(-2px);

}}



.demo .q {{ 

    font-size: 0.875rem; 

    color: var(--muted); 

    margin-bottom: 0.5rem;

    font-weight: 500;

}}



.demo .a {{ 

    font-size: 1rem; 

    line-height: 1.6;

}}



.demo .a mark {{ 

    background: var(--mark); 

    color: var(--mark-ink); 

    padding: 0.125rem 0.375rem; 

    border-radius: 4px;

    font-weight: 500;

}}



/* Enhanced button styling */

.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] button {{

    min-height: 44px; 

    border-radius: var(--r); 

    font-weight: 500; 

    font-size: 0.875rem;

    background: var(--surface); 

    color: var(--ink); 

    border: 1px solid var(--line); 

    transition: all 0.2s ease;

    padding: 0.75rem 1.5rem;

    font-family: 'Inter', sans-serif;

    position: relative;

    overflow: hidden;

}}



.stButton > button::before {{

    content: '';

    position: absolute;

    top: 50%;

    left: 50%;

    width: 0;

    height: 0;

    border-radius: 50%;

    background: rgba(255, 255, 255, 0.1);

    transform: translate(-50%, -50%);

    transition: width 0.6s, height 0.6s;

}}



.stButton > button:hover::before {{

    width: 300px;

    height: 300px;

}}



.stButton > button:hover {{ 

    border-color: var(--accent); 

    color: var(--accent); 

    transform: translateY(-1px);

    box-shadow: var(--shadow);

}}



.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"] {{ 

    background: var(--accent); 

    border-color: var(--accent); 

    color: var(--canvas); 

    font-weight: 600;

    position: relative;

    overflow: hidden;

}}



.stButton > button[kind="primary"]:hover {{ 

    background: var(--accent_h); 

    border-color: var(--accent_h); 

    color: var(--canvas); 

    transform: translateY(-1px);

    box-shadow: var(--shadow_md);

}}



.stButton > button:active {{ 

    transform: translateY(0);

}}



/* Focus states */

.stButton > button:focus-visible, input:focus-visible, textarea:focus-visible {{ 

    outline: 2px solid var(--accent) !important; 

    outline-offset: 2px; 

}}



/* Enhanced input styling */

.stTextInput input, .stTextArea textarea, .stNumberInput input, .stSelectbox [data-baseweb="select"] > div {{

    border-radius: var(--r) !important; 

    background: var(--surface) !important; 

    color: var(--ink) !important; 

    border-color: var(--line) !important;

    transition: all 0.2s ease;

    font-family: 'Inter', sans-serif;

}}



.stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {{

    border-color: var(--accent) !important;

    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);

}}



/* Enhanced file uploader */

[data-testid="stFileUploader"] section {{ 

    background: var(--surface2); 

    border: 2px dashed var(--line); 

    border-radius: var(--r); 

    transition: all 0.2s ease;

    padding: 2rem;

}}



[data-testid="stFileUploader"] section:hover {{ 

    border-color: var(--accent);

    background: var(--surface);

}}



/* Enhanced data table */

[data-testid="stDataFrame"] {{ 

    border: 1px solid var(--line); 

    border-radius: var(--r); 

    overflow: hidden;

    box-shadow: var(--shadow);

}}



/* Enhanced chat styling */

[data-testid="stChatMessage"] {{ 

    background: var(--surface); 

    border: 1px solid var(--line); 

    border-radius: var(--r); 

    padding: 1.25rem; 

    margin-bottom: 1rem;

    transition: all 0.2s ease;

}}



[data-testid="stChatMessage"]:hover {{ 

    box-shadow: var(--shadow_md);

}}



[data-testid="stChatInput"] {{ 

    border-radius: var(--r); 

    border-color: var(--line); 

    background: var(--surface);

    padding: 1rem;

    box-shadow: var(--shadow);

}}



div[data-testid="stExpander"] {{ 

    border: 1px solid var(--line); 

    border-radius: var(--r); 

    background: var(--surface);

    transition: all 0.2s ease;

}}



div[data-testid="stExpander"]:hover {{ 

    box-shadow: var(--shadow_md);

}}



[data-testid="stTabs"] [role="tab"] {{ 

    font-weight: 500; 

    padding: 0.75rem 1.5rem;

    border-radius: var(--r) var(--r) 0 0;

    transition: all 0.2s ease;

}}



[data-testid="stTabs"] [aria-selected="true"] {{ 

    color: var(--accent); 

    background: var(--accent-soft);

}}



[data-testid="stAlert"] {{ 

    border-radius: var(--r); 

    border: 1px solid var(--line);

    box-shadow: var(--shadow);

}}



[data-testid="stVerticalBlockBorderWrapper"] {{ 

    border-color: var(--line); 

    border-radius: var(--r); 

}}



hr {{ 

    border-color: var(--line); 

    border: none;

    height: 1px;

    margin: 2rem 0;

}}



footer {{ 

    visibility: hidden; 

}}



/* Notification styling */

.notification {{

    position: fixed;

    top: 20px;

    right: 20px;

    z-index: 1000;

    min-width: 300px;

    max-width: 500px;

    padding: 1rem;

    border-radius: var(--r);

    box-shadow: var(--shadow_lg);

    animation: slideIn 0.3s ease-out;

    margin-bottom: 20px;

}}



@keyframes slideIn {{

    from {{

        transform: translateX(100%);

        opacity: 0;

    }}

    to {{

        transform: translateX(0);

        opacity: 1;

    }}

}}



/* Responsive improvements */

@media (max-width: 768px) {{

    .block-container {{ 

        padding: 1rem 0.75rem 2rem;

    }}



    .auth-panel {{ 

        min-height: auto;

        padding: 1.5rem;

    }}



    .page-head h1 {{

        font-size: 1.5rem;

    }}



    .doc-card {{

        flex-direction: column;

        align-items: flex-start;

        gap: 0.75rem;

    }}



    [data-testid="stSidebar"] {{

        width: 100%;

        max-height: 50vh;

    }}

}}



/* Reduced motion support */

@media (prefers-reduced-motion: reduce) {{

    * {{ 

        transition: none !important; 

        animation: none !important; 

    }}

}}

</style>

""",

        unsafe_allow_html=True,

    )





inject_css()





# ---------------------------------------------------------------------------

# Enhanced Helper Functions

# ---------------------------------------------------------------------------

def safe(value):

    """Escape HTML safely"""

    return html.escape(str(value if value is not None else ""))





def show_notification(message, type="info"):

    """Show modern notification"""

    colors = {

        "success": {"bg": "#d1fae5", "text": "#064e3b", "border": "#10b981"},

        "error": {"bg": "#fee2e2", "text": "#7f1d1d", "border": "#ef4444"},

        "warning": {"bg": "#fed7aa", "text": "#78350f", "border": "#f59e0b"},

        "info": {"bg": "#dbeafe", "text": "#1e40af", "border": "#3b82f6"}

    }



    color = colors.get(type, colors["info"])

    st.markdown(

        f"""

        <div class="notification" style="

            background: {color['bg']}; 

            color: {color['text']}; 

            border-left: 4px solid {color['border']};

        ">

            <div style="display: flex; align-items: center; gap: 0.5rem;">

                <div style="font-weight: 600; font-size: 0.875rem;">{type.upper()}</div>

                <div style="flex: 1;">{safe(message)}</div>

            </div>

        </div>

        """,

        unsafe_allow_html=True

    )





def api_call(label, callback, *args, **kwargs):

    """Enhanced API call with better error handling"""

    try:

        return callback(*args, **kwargs)

    except Exception as exc:

        error_msg = f"{label} failed. Retry, and contact your administrator if it keeps happening."

        st.error(error_msg)

        show_notification(error_msg, "error")

        return {"success": False, "error": str(exc)}





def fmt_size(n):

    """Enhanced file size formatting"""

    n = n or 0

    if n >= 1024 * 1024 * 1024:

        return f"{n / (1024 * 1024 * 1024):.1f} GB"

    if n >= 1024 * 1024:

        return f"{n / (1024 * 1024):.1f} MB"

    if n >= 1024:

        return f"{n / 1024:.1f} KB"

    return f"{n} B"





def ext_of(doc):

    """Get file extension with better handling"""

    return str(doc.get("file_type", "")).lower().replace(".", "") or "unknown"





def brand():

    """Enhanced brand component"""

    st.markdown(

        '<div class="brand"><div class="brand-mark">D</div><div><div class="brand-name">DocMind</div>'

        '<div class="brand-sub">Advanced Document Analysis</div></div></div>',

        unsafe_allow_html=True,

    )





def page_head(crumb, title, description):

    """Enhanced page header with better typography"""

    st.markdown(

        f'<div class="page-head"><div class="crumb">{safe(crumb)}</div><h1>{safe(title)}</h1><p>{safe(description)}</p></div>',

        unsafe_allow_html=True,

    )





def empty_state(title, body):

    """Enhanced empty state with better styling"""

    st.markdown(f'<div class="empty"><div class="card-title">{safe(title)}</div><div class="card-sub">{safe(body)}</div></div>', unsafe_allow_html=True)





def fetch_download(token, doc_uuid, key):

    """Enhanced download with caching"""

    cache = st.session_state["dl_cache"]

    if doc_uuid in cache:

        return cache[doc_uuid]

    return None





def download_control(token, doc, key, full_width=False):

    """Enhanced download control with better UX"""

    uuid = doc.get("document_uuid")

    name = doc.get("filename", "document")

    cache = st.session_state["dl_cache"]



    if uuid in cache:

        col1, col2 = st.columns([1, 0.1])

        with col1:

            st.download_button("Download file", cache[uuid], file_name=name, key=f"dl_{key}", use_container_width=full_width)

        with col2:

            if st.button("↻", key=f"refresh_{key}", help="Refresh download"):

                cache.pop(uuid, None)

                st.rerun()

    else:

        if st.button("Download", key=f"prep_{key}", use_container_width=full_width):

            with st.spinner("Preparing download..."):

                data = backend_client.download_document(token, uuid)

                if data is None:

                    st.error("This file could not be downloaded.")

                    show_notification("Download failed. Please try again.", "error")

                else:

                    cache[uuid] = data

                    st.rerun()





def go(page):

    """Navigation helper"""

    st.session_state["workspace_nav"] = page





def cb_new_chat():

    """Enhanced chat reset"""

    st.session_state.update(

        workspace_nav="AI Assistant", 

        current_session_uuid=None, 

        chat_messages=[], 

        suggested_prompt="",

        notification=None

    )

    show_notification("New chat started", "success")





def cb_upload():

    """Enhanced upload trigger"""

    st.session_state.update(

        workspace_nav="Documents", 

        open_upload_panel=True,

        notification=None

    )





def set_logged_in(result):

    """Enhanced login handler"""

    st.session_state["token"] = result["data"]["access_token"]

    st.session_state["user"] = result["data"]["user"]

    st.session_state.update(

        chat_messages=[], 

        current_session_uuid=None, 

        workspace_nav="Documents", 

        dl_cache={},

        notification=None

    )

    show_notification("Successfully logged in!", "success")

    st.rerun()





@st.cache_data(ttl=20, show_spinner=False)

def cached_health(nonce):

    """Enhanced health check with caching"""

    return backend_client.get_health()





# ---------------------------------------------------------------------------

# Enhanced Authentication

# ---------------------------------------------------------------------------

def render_auth():

    """Enhanced authentication with modern design"""

    left, right = st.columns([1.2, 1], gap="large")



    with left:
        st.markdown(
            """<div class="auth-panel" style="background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #4f46e5 100%); background-color: #1e3a8a; color: #ffffff; border-radius: 24px; padding: 2.75rem 2.25rem; min-height: 570px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 20px 25px -5px rgba(30, 58, 138, 0.35), 0 8px 10px -6px rgba(30, 58, 138, 0.2); border: 1px solid rgba(255,255,255,0.18); position: relative; overflow: hidden;">
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

        st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)

        brand()



        # Modern tabs

        login_tab, register_tab = st.tabs(["🔐 Sign In", "📝 Create Account"])



        with login_tab:

            with st.form("login_form", border=True):

                st.markdown("### Welcome back")

                email = st.text_input("Email address", placeholder="you@company.com", type="email")

                password = st.text_input("Password", type="password", placeholder="Enter your password")

                submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)



                if submitted:

                    if not email.strip() or not password:

                        st.warning("Please enter both your email and password.")

                    else:

                        with st.spinner("Signing in..."):

                            result = api_call("Sign in", backend_client.login, email.strip(), password)

                        if result.get("success"):

                            set_logged_in(result)

                        else:

                            st.error(result.get("error", "Unable to sign in."))

                            show_notification("Login failed. Please check your credentials.", "error")



        with register_tab:

            with st.form("register_form", border=True):

                st.markdown("### Create your account")

                full_name = st.text_input("Full name", placeholder="John Doe")

                email = st.text_input("Email address", placeholder="you@company.com", type="email", key="register_email")

                password = st.text_input("Password", type="password", placeholder="Create a password", key="register_password")

                submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)



                if submitted:

                    if not full_name.strip() or not email.strip() or not password:

                        st.warning("Please fill in all fields to continue.")

                    else:

                        result = api_call("Account creation", backend_client.register, email.strip(), password, full_name.strip(), "USER")

                        if result.get("success"):

                            show_notification("Account created successfully! Please sign in.", "success")

                        else:

                            st.error(result.get("error", "Registration failed."))

                            show_notification("Registration failed. Please try again.", "error")





# ---------------------------------------------------------------------------

# Enhanced Dialogs

# ---------------------------------------------------------------------------

def _find_updater():

    return (

        getattr(backend_client, "update_user", None)

        or getattr(backend_client, "update_admin_user", None)

        or getattr(backend_client, "edit_user", None)

    )





@st.dialog("Edit user", width="medium")

def edit_user_dialog(user_record, token):

    st.caption("Changes apply as soon as you save.")

    with st.form(f"edit_user_form_{user_record.get('id')}"):

        col1, col2 = st.columns(2)

        with col1:

            full_name = st.text_input("Full name", value=str(user_record.get("full_name") or ""))

        with col2:

            email = st.text_input("Email address", value=str(user_record.get("email") or ""))



        current_role = str(user_record.get("role") or "USER").upper()

        roles = ["USER", "ADMIN"] if current_role in {"USER", "ADMIN"} else [current_role, "USER", "ADMIN"]

        role = st.selectbox("Role", roles, index=roles.index(current_role))



        submitted = st.form_submit_button("Save changes", type="primary", use_container_width=True)



    if submitted:

        if not full_name.strip() or not email.strip():

            st.warning("Name and email are required.")

            return

        updater = _find_updater()

        if not callable(updater):

            st.error("Editing users isn't available yet. Add an admin update-user endpoint and expose it through BackendClient.")

            return

        try:

            try:

                result = updater(token, user_record.get("id"), full_name=full_name.strip(), email=email.strip(), role=role)

            except TypeError:

                result = updater(token, user_record.get("id"), {"full_name": full_name.strip(), "email": email.strip(), "role": role})

        except Exception:

            st.error("Could not update this account. Check the backend logs and try again.")

            return

        if isinstance(result, dict) and result.get("success"):

            show_notification("User updated successfully!", "success")

            st.rerun()

        else:

            st.error(result.get("error", "The backend did not confirm the update.") if isinstance(result, dict) else "The backend did not confirm the update.")





@st.dialog("Delete account", width="small")

def delete_user_dialog(user_record, token):

    st.warning(f"Delete {user_record.get('full_name') or user_record.get('email') or 'this account'}? This can't be undone.")

    st.caption("Documents and indexed content owned by this user may also be removed, depending on backend behavior.")

    confirmed = st.checkbox("I understand this is permanent.", key=f"confirm_user_delete_{user_record.get('id')}")

    a, b = st.columns(2)

    with a:

        if st.button("Delete account", type="primary", disabled=not confirmed, use_container_width=True):

            result = api_call("Delete account", backend_client.delete_user, token, user_record.get("id"))

            if isinstance(result, dict) and result.get("success"):

                show_notification("Account deleted successfully.", "success")

                st.rerun()

            else:

                st.error(result.get("error", "Could not delete account.") if isinstance(result, dict) else "Could not delete account.")

    with b:

        if st.button("Cancel", use_container_width=True):

            st.rerun()





@st.dialog("Delete document", width="small")

def delete_document_dialog(document, token):

    st.warning(f"Delete **{document.get('filename', 'this document')}**? This can't be undone.")

    st.caption("The document and all of its indexed chunks will be removed.")

    confirmed = st.checkbox("I understand this is permanent.", key=f"confirm_doc_delete_{document.get('document_uuid')}")

    a, b = st.columns(2)

    with a:

        if st.button("Delete document", type="primary", disabled=not confirmed, use_container_width=True):

            result = api_call("Delete document", backend_client.delete_document, token, document.get("document_uuid"))

            if isinstance(result, dict) and result.get("success"):

                st.session_state["dl_cache"].pop(document.get("document_uuid"), None)

                show_notification("Document deleted successfully.", "success")

                st.rerun()

            else:

                st.error(result.get("error", "Delete failed.") if isinstance(result, dict) else "Delete failed.")

    with b:

        if st.button("Cancel", use_container_width=True):

            st.rerun()





# ---------------------------------------------------------------------------

# Enhanced Sidebar

# ---------------------------------------------------------------------------

def render_sidebar():

    """Enhanced sidebar with modern design"""

    user = st.session_state["user"]

    brand()



    nav = ["Documents", "AI Assistant"] + (["Admin"] if user.get("role") == "ADMIN" else [])

    labels = {"Documents": "📄 Documents", "AI Assistant": "🤖 AI Assistant", "Admin": "⚙️ Administration"}

    if st.session_state["workspace_nav"] not in nav:

        st.session_state["workspace_nav"] = "Documents"

    selected = st.radio("Navigate", nav, label_visibility="collapsed", key="workspace_nav", format_func=labels.get)



    # Quick actions section

    st.markdown('<div class="side-label">Quick Actions</div>', unsafe_allow_html=True)

    if st.button("➕ New conversation", use_container_width=True, key="sb_chat"):

        cb_new_chat()

    if st.button("📤 Upload a document", use_container_width=True, key="sb_upload"):

        cb_upload()



    # Status section

    st.markdown('<div class="side-label">Status</div>', unsafe_allow_html=True)

    nonce = st.session_state.get("health_nonce", 0)

    try:

        health = cached_health(nonce)

    except Exception:

        health = None

    online = isinstance(health, dict) and health.get("online")



    status_col1, status_col2 = st.columns([3, 1])

    with status_col1:

        status_color = "b-public" if online else "b-personal"

        status_text = "API connected" if online else "API unavailable"

        st.markdown(f'<span class="badge {status_color}">● {status_text}</span>', unsafe_allow_html=True)

    with status_col2:

        if st.button("↻", key="refresh_api_health", help="Re-check the connection"):

            st.session_state["health_nonce"] = nonce + 1

            st.rerun()



    # Appearance section

    st.markdown('<div class="side-label">Appearance</div>', unsafe_allow_html=True)

    dark_mode = st.toggle("🌙 Dark mode", key="dark_mode")

    if dark_mode != st.session_state.get("dark_mode"):

        st.session_state["dark_mode"] = dark_mode

        st.rerun()



    st.markdown("---")



    # User profile section

    initials = "".join(p[0] for p in str(user.get("full_name") or "User").split()[:2]).upper()

    st.markdown(

        f'<div class="doc-card"><div class="ftype ft-txt" style="border-radius:50%">{safe(initials)}</div>'

        f'<div style="min-width:0"><div class="doc-name">{safe(user.get("full_name", "User"))}</div>'

        f'<div class="doc-meta" style="overflow-wrap:anywhere">{safe(user.get("email", ""))}</div></div></div>',

        unsafe_allow_html=True,

    )

    st.markdown(f'<div style="margin:10px 0"><span class="badge b-neutral">{safe(user.get("role", "USER"))}</span></div>', unsafe_allow_html=True)



    if st.button("🚪 Sign out", use_container_width=True):

        for key in ("token", "user", "current_session_uuid"):

            st.session_state[key] = None

        st.session_state.update(chat_messages=[], dl_cache={})

        for key in ("suggested_prompt", "open_upload_panel"):

            st.session_state.pop(key, None)

        show_notification("Successfully signed out.", "success")

        st.rerun()



    return selected





# ---------------------------------------------------------------------------

# Enhanced Documents Page

# ---------------------------------------------------------------------------

def render_documents():

    """Enhanced documents page with modern design"""

    token = st.session_state["token"]

    user = st.session_state["user"]

    page_head("Workspace", "Documents", "Upload files, choose who can see them, and manage everything your assistant can read.")



    # Fetch documents

    all_docs = backend_client.list_documents(token, scope="all") or []

    personal_docs = [d for d in all_docs if str(d.get("visibility", "")).upper() == "PERSONAL" and str(d.get("owner_id", "")) == str(user.get("id", ""))]

    public_docs = [d for d in all_docs if str(d.get("visibility", "")).upper() == "PUBLIC"]

    total_bytes = sum((d.get("file_size_bytes") or 0) for d in all_docs)



    # Modern metrics cards

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric("Accessible files", len(all_docs))

    with col2:

        st.metric("Personal", len(personal_docs))

    with col3:

        st.metric("Public", len(public_docs))

    with col4:

        st.metric("Storage used", fmt_size(total_bytes))



    # Upload section

    st.markdown("")

    with st.expander("📤 Add documents", expanded=st.session_state.pop("open_upload_panel", False)):

        up_col, set_col = st.columns([2, 1], gap="large")

        with up_col:

            uploaded = st.file_uploader("PDF, DOCX or TXT, up to 25 MB", type=["pdf", "docx", "txt"], key="document_upload")

        with set_col:

            visibility = st.selectbox(

                "Who can see it", ["PERSONAL", "PUBLIC"],

                format_func=lambda v: "🔒 Only me" if v == "PERSONAL" else "🌍 Everyone in the workspace",

            )

            st.caption("Personal files stay private to you. Public files are searchable by authorized users.")



        if st.button("🚀 Upload and index", type="primary", disabled=uploaded is None):

            payload = uploaded.getvalue() if uploaded is not None else b""

            if not payload:

                st.warning("This file is empty. Choose a file that has content.")

            elif len(payload) > 25 * 1024 * 1024:

                st.warning("Files over 25 MB can't be uploaded here. Choose a smaller file, or raise the limit in both the backend and this UI.")

            else:

                with st.spinner("Uploading and indexing..."):

                    result = api_call("Upload", backend_client.upload_document, token, uploaded.name, payload, visibility)

                if result.get("success"):

                    show_notification("Uploaded successfully! Indexing has started.", "success")

                    st.rerun()

                else:

                    st.error(result.get("error", "Upload failed."))



    # Library overview

    if all_docs:

        mix = Counter(ext_of(d).upper() or "OTHER" for d in all_docs)

        with st.expander("📊 Library overview", expanded=False):

            st.caption("Files by format")

            st.bar_chart(pd.DataFrame({"Files": mix}), horizontal=True, height=140, color="#3b82f6")



    # Search and filters

    st.markdown("### 📚 Library")

    search_col, type_col, view_col = st.columns([2.4, 1, 1.1])

    with search_col:

        search = st.text_input("🔍 Search", placeholder="Search by file name", key="document_search", label_visibility="collapsed")

    with type_col:

        file_type = st.selectbox("📄 Format", ["All formats", "PDF", "DOCX", "TXT"], key="document_type", label_visibility="collapsed")

    with view_col:

        view = st.radio("👁️ View", ["Table", "Cards"], horizontal=True, key="document_view", label_visibility="collapsed")



    # Tabs for different document types

    tabs = st.tabs([f"🔒 Personal ({len(personal_docs)})", f"🌍 Public ({len(public_docs)})", "📋 All accessible"])



    def show_docs(docs, prefix):

        filtered = [

            d for d in docs

            if search.lower() in str(d.get("filename", "")).lower()

            and (file_type == "All formats" or ext_of(d) == file_type.lower())

        ]

        if not filtered:

            empty_state("No documents match", "Clear the search or format filter, or upload a document to get started.")

            return



        if view == "Table":

            rows = [{

                "Document": d.get("filename", "Untitled document"),

                "Format": ext_of(d).upper(),

                "Access": str(d.get("visibility", "")).title(),

                "Size": fmt_size(d.get("file_size_bytes")),

                "Added": str(d.get("created_at", ""))[:10] or "—",

            } for d in filtered]

            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)



            with st.container(border=True):

                idx = st.selectbox(

                    "Manage a document", list(range(len(filtered))),

                    format_func=lambda i: filtered[i].get("filename", "Untitled"), key=f"{prefix}_selected_document",

                )

                sel = filtered[idx]

                col1, col2, col3 = st.columns([1, 1.4, 1], gap="medium")

                with col1:

                    st.caption("📄 File")

                    download_control(token, sel, f"{prefix}_tbl_{sel.get('document_uuid')}", full_width=True)

                with col2:

                    st.caption("🔒 Access")

                    vis_col1, vis_col2 = st.columns([1.3, 1])

                    new_vis = vis_col1.selectbox(

                        "Visibility", ["PERSONAL", "PUBLIC"],

                        index=0 if sel.get("visibility") == "PERSONAL" else 1,

                        key=f"{prefix}_visibility_{sel.get('document_uuid')}", label_visibility="collapsed",

                    )

                    if vis_col2.button("💾 Save", key=f"{prefix}_save_visibility", use_container_width=True):

                        result = backend_client.update_document(token, sel["document_uuid"], visibility=new_vis)

                        if result.get("success"):

                            show_notification("Visibility updated.", "success")

                            st.rerun()

                        else:

                            st.error(result.get("error", "Could not update visibility."))

                with col3:

                    st.caption("⚠️ Danger zone")

                    if st.button("🗑️ Delete", key=f"{prefix}_delete", use_container_width=True):

                        delete_document_dialog(sel, token)

        else:

            cols = st.columns(3)

            for i, doc in enumerate(filtered):

                with cols[i % 3]:

                    ext = ext_of(doc) or "file"

                    cls = {"pdf": "ft-pdf", "docx": "ft-docx"}.get(ext, "ft-txt")

                    pub = str(doc.get("visibility", "")).upper() == "PUBLIC"

                    st.markdown(

                        f'<div class="card"><div class="doc-card"><div class="ftype {cls}">{safe(ext.upper())}</div>'

                        f'<div style="min-width:0"><div class="doc-name">{safe(doc.get("filename", "Untitled"))}</div>'

                        f'<div class="doc-meta">{fmt_size(doc.get("file_size_bytes"))} · {safe(str(doc.get("created_at", ""))[:10])}</div></div></div>'

                        f'<div style="margin-top:12px"><span class="badge {"b-public" if pub else "b-personal"}">{"🌍 Public" if pub else "🔒 Personal"}</span></div></div>',

                        unsafe_allow_html=True,

                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        download_control(token, doc, f"{prefix}_card_{doc['document_uuid']}", full_width=True)

                    with col2:

                        if st.button("🗑️", key=f"{prefix}_card_del_{doc['document_uuid']}", use_container_width=True):

                            delete_document_dialog(doc, token)



    with tabs[0]:

        show_docs(personal_docs, "personal")

    with tabs[1]:

        show_docs(public_docs, "public")

    with tabs[2]:

        combined = backend_client.list_documents(

            token, scope="all", search=search or None,

            file_type=None if file_type == "All formats" else file_type.lower(),

        ) or []

        show_docs(combined, "combined")





# ---------------------------------------------------------------------------

# Enhanced Chat Interface

# ---------------------------------------------------------------------------

def render_chat():

    """Enhanced chat interface with modern design"""

    token = st.session_state["token"]

    page_head("Workspace", "AI Assistant", "Ask a question in plain language. Answers list the files they came from.")



    # Chat controls

    col1, col2 = st.columns([2.2, 1], gap="large")

    with col1:

        search_mode = st.radio(

            "🔍 Search in", ["PRIVATE", "PUBLIC", "COMBINED"], horizontal=True, key="chat_search_mode",

            format_func=lambda v: {"PRIVATE": "🔒 My files", "PUBLIC": "🌍 Public library", "COMBINED": "📋 Both"}[v],

        )

    with col2:

        if st.button("➕ New chat", use_container_width=True, type="primary"):

            result = backend_client.create_chat_session(token, search_mode=search_mode)

            st.session_state["current_session_uuid"] = result.get("session_uuid") if result else None

            st.session_state["chat_messages"] = []

            show_notification("New chat started", "success")

            st.rerun()



    # Chat history

    with st.expander("📝 Conversation history", expanded=False):

        sessions = backend_client.list_chat_sessions(token) or []

        if sessions:

            labels = {f"{str(s.get('created_at', ''))[:10]} · {str(s.get('session_uuid', ''))[:8]}": s.get("session_uuid") for s in sessions}

            chosen = st.selectbox("Previous conversations", list(labels.keys()), key="chat_history_select")

            if st.button("📂 Open conversation", key="load_chat_history"):

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

            st.caption("Past conversations will show up here.")



    # Chat messages

    if not st.session_state["chat_messages"]:

        empty_state("Ask your first question", "The assistant searches the library you selected, writes an answer, and lists the source files.")

        st.markdown("")

        prompts = [

            "Summarize the key points in my documents",

            "What requirements do these files describe?",

            "Which documents mention a specific topic?",

        ]

        cols = st.columns(3)

        for i, p in enumerate(prompts):

            if cols[i].button(f"💡 {p}", key=f"chat_prompt_{i}", use_container_width=True):

                st.session_state["suggested_prompt"] = p

                st.rerun()



    # Display chat messages

    for mi, msg in enumerate(st.session_state["chat_messages"]):

        role = "user" if msg.get("role") == "user" else "assistant"

        with st.chat_message(role):

            st.markdown(msg.get("content", ""))

            sources = msg.get("sources") or []

            if role == "assistant" and sources:

                chips = "".join(f'<span class="src-chip">📄 {safe(s.get("filename", "Source"))}</span>' for s in sources)

                st.markdown(f'<div style="margin-top:8px">{chips}</div>', unsafe_allow_html=True)

                with st.expander(f"🔍 View {len(sources)} source{'s' if len(sources) != 1 else ''}"):

                    for si, s in enumerate(sources):

                        name = s.get("filename", "Source document")

                        st.markdown(f"**{safe(name)}**")

                        if s.get("snippet"):

                            st.markdown(f'<div class="snippet">{safe(s["snippet"])}</div>', unsafe_allow_html=True)

                        if s.get("document_uuid"):

                            download_control(token, {"document_uuid": s["document_uuid"], "filename": name}, f"src_{mi}_{si}_{s['document_uuid']}")



    # Chat input

    prompt = st.chat_input("Ask a question about your documents...")

    if not prompt and st.session_state.get("suggested_prompt"):

        prompt = st.session_state["suggested_prompt"]

        st.session_state["suggested_prompt"] = ""



    if prompt:

        st.session_state["chat_messages"].append({"role": "user", "content": prompt, "sources": []})

        with st.spinner("🔍 Searching your documents..."):

            result = api_call(

                "AI request", backend_client.query_rag_chat,

                token=token, query=prompt, search_mode=search_mode,

                session_uuid=st.session_state.get("current_session_uuid"),

            )

        if result.get("success"):

            data = result["data"]

            st.session_state["current_session_uuid"] = data.get("session_uuid")

            st.session_state["chat_messages"].append({

                "role": "assistant", "content": data.get("answer", "No answer was returned."), "sources": data.get("sources", []),

            })

            st.rerun()

        else:

            st.error(result.get("error", "The assistant couldn't complete this request. Try again."))

            show_notification("Request failed. Please try again.", "error")





# ---------------------------------------------------------------------------

# Enhanced Admin Interface

# ---------------------------------------------------------------------------

def render_admin():

    """Enhanced admin interface with modern design"""

    token = st.session_state["token"]

    user = st.session_state["user"]

    page_head("Workspace", "Administration", "Monitor usage, connect the AI provider, and manage who has access.")



    overview_tab, ai_tab, users_tab = st.tabs(["📊 Overview", "🤖 AI provider", "👥 Users"])



    with overview_tab:

        stats = backend_client.get_admin_stats(token) or {}

        cols = st.columns(4)

        cols[0].metric("👥 Users", stats.get("total_users", 0))

        cols[1].metric("📄 Documents", stats.get("total_documents", 0))

        cols[2].metric("📦 Indexed chunks", stats.get("total_chunks", 0))

        cols[3].metric("💬 Chat messages", stats.get("total_messages", 0))

        st.markdown("")

        chart = pd.DataFrame({"Count": {

            "Users": stats.get("total_users", 0), "Documents": stats.get("total_documents", 0),

            "Chunks": stats.get("total_chunks", 0), "Messages": stats.get("total_messages", 0),

        }})

        with st.container(border=True):

            st.markdown("**📈 Platform totals**")

            st.bar_chart(chart, height=220, color="#3b82f6")



    with ai_tab:

        status = backend_client.get_ai_status(token) or {}

        left, right = st.columns(2, gap="large")

        with left:

            with st.container(border=True):

                st.markdown("**🔗 Connection status**")

                state = status.get("status", "unknown")

                if state == "connected":

                    st.success("✅ AI provider connected")

                elif state == "invalid_key":

                    st.warning("⚠️ The API key was rejected")

                elif state == "error":

                    st.error("❌ Couldn't check the provider status")

                else:

                    st.info("ℹ️ Running in fallback or local mode")

                st.caption(status.get("message", "No status message available."))

        with right:

            with st.container(border=True):

                st.markdown("**🔑 Update API key**")

                with st.form("update_api_key"):

                    api_key = st.text_input("OpenAI API key", type="password", placeholder="Paste your key")

                    submitted = st.form_submit_button("Verify and save", type="primary", use_container_width=True)

                if submitted:

                    if not api_key.strip():

                        st.warning("⚠️ Enter an API key.")

                    else:

                        result = api_call("AI provider update", backend_client.update_ai_key, token, api_key.strip())

                        if result.get("success"):

                            show_notification("API key updated successfully!", "success")

                            st.rerun()

                        else:

                            st.error(result.get("error", "Could not update the API key."))



    with users_tab:

        users = api_call("Load users", backend_client.get_admin_users_overview, token) or []

        if not users or isinstance(users, dict):

            st.info("ℹ️ No user accounts were returned.")

            return



        user_df = pd.DataFrame(users)

        q = st.text_input("🔍 Search users", placeholder="Name or email", key="admin_user_search", label_visibility="collapsed")

        preferred = ["id", "full_name", "email", "role", "is_active", "created_at", "last_login"]

        columns = [c for c in preferred if c in user_df.columns] + [c for c in user_df.columns if c not in preferred]

        editor_df = user_df[columns].copy()

        if "role" in editor_df.columns:

            editor_df["role"] = editor_df["role"].astype(str).str.upper()

        if q.strip():

            mask = pd.Series(False, index=editor_df.index)

            for col in ("full_name", "email"):

                if col in editor_df.columns:

                    mask |= editor_df[col].astype(str).str.contains(q.strip(), case=False, na=False)

            editor_df = editor_df[mask]



        config = {

            "id": st.column_config.TextColumn("User ID"),

            "full_name": st.column_config.TextColumn("Full name"),

            "email": st.column_config.TextColumn("Email"),

            "role": st.column_config.SelectboxColumn("Role", options=["USER", "ADMIN"]),

            "is_active": st.column_config.CheckboxColumn("Active"),

        }

        for date_col in ("created_at", "last_login"):

            if date_col in editor_df.columns:

                config[date_col] = st.column_config.TextColumn(date_col.replace("_", " ").capitalize())

        editable = [f for f in ("full_name", "email", "role", "is_active") if f in editor_df.columns]



        st.caption("✏️ Edit full name, email, role or active status directly in the table, then save.")

        edited_df = st.data_editor(

            editor_df, use_container_width=True, hide_index=True, num_rows="fixed",

            key="admin_users_inline_editor", disabled=[c for c in columns if c not in editable], column_config=config,

        )

        if st.button("💾 Save table changes", type="primary", key="save_admin_user_table"):

            updater = _find_updater()

            if not callable(updater):

                st.error("💾 Saving isn't available yet. Add an authenticated update-user method to api_client.py and a matching FastAPI admin endpoint.")

            else:

                original_by_id = {str(u.get("id")): u for u in users}

                saved, failures = 0, []

                for _, row in edited_df.iterrows():

                    uid = str(row.get("id", ""))

                    original = original_by_id.get(uid)

                    if not original:

                        continue

                    changes = {}

                    for field in editable:

                        old, new = original.get(field), row.get(field)

                        if pd.isna(new):

                            new = None

                        if field == "is_active" and new is not None:

                            new = bool(new)

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

                            result = updater(token, original.get("id"), **changes)

                        except TypeError:

                            result = updater(token, original.get("id"), changes)

                        if isinstance(result, dict) and result.get("success"):

                            saved += 1

                        else:

                            failures.append(str(original.get("email") or uid))

                    except Exception:

                        failures.append(str(original.get("email") or uid))

                if failures:

                    st.warning(f"💾 Saved {saved} account(s). Couldn't save: {', '.join(failures)}.")

                elif saved:

                    show_notification(f"✅ Updated {saved} account(s).", "success")

                    st.rerun()

                else:

                    st.info("ℹ️ No changes to save.")



        st.markdown("### 👤 Manage an account")

        eligible = [u for u in users if str(u.get("id")) != str(user.get("id"))]

        if eligible:

            options = {f"{u.get('full_name') or 'User'} ({u.get('email', '')})": u for u in eligible}

            label = st.selectbox("Account", list(options.keys()), key="admin_selected_user")

            target = options[label]

            col1, col2, col3 = st.columns([1, 1, 2])

            if col1.button("✏️ Edit user", type="primary", use_container_width=True):

                edit_user_dialog(target, token)

            if col2.button("🗑️ Delete user", use_container_width=True):

                delete_user_dialog(target, token)

            col3.caption("🔒 Your own account isn't listed, so you can't delete yourself.")

        else:

            st.caption("ℹ️ There are no other accounts to manage.")





# ---------------------------------------------------------------------------

# Main Router

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

            st.error("🚫 You don't have permission to open Administration.")

            show_notification("Access denied. Admin privileges required.", "error")