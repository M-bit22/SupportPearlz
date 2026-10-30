
import html
from datetime import date, datetime, timedelta


import streamlit as st

from src.config import validate_config, KNOWLEDGE_BASE_DIR
from src.ingestion.build_index import build_vector_index
from src.chains.rag_chain import get_rag_chain
from src.retrieval.vector_store import load_vector_store


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="SupportPearlz",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# SESSION STATE
# =========================================================

DEFAULTS = {
    "messages": [],
    "conversations": [],
    "active_conversation": "New Chat",
    "sidebar_open": True,
    "chat_open": True,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


@st.cache_resource
def get_cached_rag_chain():
    return get_rag_chain()


def toggle_sidebar():
    st.session_state.sidebar_open = not st.session_state.sidebar_open


def toggle_chat():
    st.session_state.chat_open = not st.session_state.chat_open


BRAND_LOGO = (
    '<div class="brand-logo">'
    '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<path d="M6 4h12l4 5-10 11L2 9z" fill="#ffffff" fill-opacity="0.95"/>'
    '<path d="M2 9h20M9 4l-2 5 5 11 5-11-2-5" stroke="#2563eb" '
    'stroke-width="1.2" stroke-linejoin="round"/>'
    '</svg></div>'
)

BRAND_HTML = (
    '<div class="brand-row">'
    + BRAND_LOGO +
    '<div>'
    '<div class="brand-name">Support<span>Pearlz</span></div>'
    '<div class="brand-sub">AI customer support assistant</div>'
    '</div></div>'
)

BRAND_COMPACT_HTML = (
    '<div class="brand-row brand-compact">'
    + BRAND_LOGO +
    '<div class="brand-name">Support<span>Pearlz</span></div>'
    '</div>'
)


# =========================================================
# DISPLAY HELPERS (design only)
# =========================================================

def format_size(num_bytes: int) -> str:
    if num_bytes < 1024 * 1024:
        return f"{max(num_bytes / 1024, 0.1):.0f} KB"
    return f"{num_bytes / (1024 * 1024):.1f} MB"


def format_added(timestamp: float) -> str:
    added = datetime.fromtimestamp(timestamp).date()
    today = date.today()
    if added == today:
        return "Today"
    if added == today - timedelta(days=1):
        return "Yesterday"
    return added.strftime("%b %d")


FILE_ICON_CLASS = {
    ".pdf": "icon-blue",
    ".txt": "icon-orange",
    ".docx": "icon-purple",
}


# =========================================================
# CUSTOM DARK THEME
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --background: #08090b;
    --sidebar: #0d0e11;
    --middle: #09090c;
    --surface: #15171b;
    --surface-light: #1b1d22;
    --border: #1c1e24;
    --border-strong: #2a2d35;
    --text: #e9eaf0;
    --muted: #7d8391;
    --muted-dark: #5c616d;
    --blue: #2563eb;
    --blue-soft: #7fb0ff;
    --green: #2ecf92;
    --amber: #e6b53c;
}

/* ---------- General page ---------- */

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: var(--background);
    color: var(--text);
}

header, footer, #MainMenu {
    visibility: hidden;
}

[data-testid="stSidebar"] {
    display: none;
}

.block-container,
[data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    max-width: 100% !important;
}

/* Marker elements only exist so CSS can find each pane */
[data-testid="stElementContainer"]:has(.pane-marker),
.element-container:has(.pane-marker) {
    display: none !important;
}

/* ---------- Three-pane layout ---------- */

[data-testid="stHorizontalBlock"]:has(.pane-center) {
    display: flex !important;
    align-items: stretch !important;
    gap: 0 !important;
    width: 100% !important;
    min-height: 100vh;
}

[data-testid="stColumn"]:has(.pane-left),
[data-testid="stColumn"]:has(.pane-center),
[data-testid="stColumn"]:has(.pane-right),
[data-testid="column"]:has(.pane-left),
[data-testid="column"]:has(.pane-center),
[data-testid="column"]:has(.pane-right) {
    min-width: 0 !important;
    margin: 0 !important;
    align-self: stretch !important;
    border-right: 1px solid var(--border);
    box-sizing: border-box !important;
}

[data-testid="stColumn"]:has(.pane-left),
[data-testid="column"]:has(.pane-left) {
    background: var(--sidebar);
    padding: 16px 12px 20px !important;
}

[data-testid="stColumn"]:has(.pane-center),
[data-testid="column"]:has(.pane-center) {
    background: var(--middle);
    padding: 24px 22px !important;
}

[data-testid="stColumn"]:has(.pane-right),
[data-testid="column"]:has(.pane-right) {
    background: var(--sidebar);
    padding: 20px 22px 16px !important;
    border-right: none;
}

/* ---------- Left pane: window dots, profile, navigation ---------- */

.window-dots {
    display: flex;
    gap: 6px;
    margin: 0 0 22px 4px;
}

.window-dots span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
}

.dot-red { background: #ee5f57; }
.dot-yellow { background: #f4be3a; }
.dot-green { background: #3bc255; }

.profile {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 4px;
    margin-bottom: 18px;
    font-size: 13px;
    font-weight: 500;
    color: #eceef3;
}

.profile-avatar {
    width: 26px;
    height: 26px;
    border-radius: 6px;
    background: linear-gradient(135deg, #3a3f4b, #20232a);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    flex-shrink: 0;
}

.profile-chevron {
    margin-left: auto;
    color: var(--muted-dark);
    font-size: 11px;
}

.section-label {
    color: #6f7581;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.6px;
    margin: 22px 0 8px 4px;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    margin: 2px 0;
    border-radius: 6px;
    color: #b4b9c4;
    font-size: 12px;
    font-weight: 500;
}

.nav-active {
    color: white;
    background: var(--blue);
}

.nav-child {
    margin: 0 0 0 14px;
    padding: 7px 10px 7px 16px;
    border-left: 1px solid #23262d;
    border-radius: 0 6px 6px 0;
    color: #9aa0ab;
    font-size: 11px;
}

.tag-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    display: inline-block;
    margin: 0 6px 1px 4px;
}

.tag-blue { background: #3b82f6; }
.tag-grey { background: #6b7280; }

.settings-row {
    margin-top: 56px;
    padding-top: 14px;
    border-top: 1px solid var(--border);
}

/* ---------- Buttons ---------- */

.stButton > button {
    background: var(--surface);
    color: var(--text);
    border: 1px solid var(--border-strong);
    border-radius: 7px;
    font-size: 12px;
    font-weight: 600;
    min-height: 36px;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: var(--blue);
    color: white;
    border-color: var(--blue);
}

.stButton > button p {
    font-size: 12px;
}

/* New chat + saved conversations */

.st-key-new_chat button {
    background: transparent;
    border: 1px dashed var(--border-strong);
    color: #b4b9c4;
    justify-content: flex-start;
}

[class*="st-key-conversation_"] button {
    background: transparent;
    border: none;
    color: #b4b9c4;
    justify-content: flex-start;
    min-height: 32px;
    font-weight: 500;
}

[class*="st-key-conversation_"] button:hover {
    background: var(--surface-light);
    color: white;
}

/* Brand */

.brand-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 0 0 18px 4px;
}

.brand-compact {
    margin: 0 0 16px 0;
}

.brand-logo {
    width: 30px;
    height: 30px;
    border-radius: 9px;
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.brand-name {
    color: white;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: -0.4px;
    line-height: 1.1;
}

.brand-name span {
    color: var(--blue-soft);
}

.brand-sub {
    color: var(--muted-dark);
    font-size: 10px;
    margin-top: 3px;
}

/* Sidebar + assistant toggles */

.st-key-toggle_chat button {
    background: var(--surface);
    border: 1px solid var(--border-strong);
    color: #c9ccd6;
    min-height: 34px;
    padding: 0;
    font-size: 14px;
}

.st-key-toggle_chat button:hover {
    background: var(--surface-light);
    border-color: #3a3d46;
    color: white;
}

/* Sidebar toggle */

.st-key-toggle_sidebar button {
    background: var(--surface);
    border: 1px solid var(--border-strong);
    color: #c9ccd6;
    min-height: 34px;
    padding: 0;
    font-size: 15px;
}

.st-key-toggle_sidebar button:hover {
    background: var(--surface-light);
    border-color: #3a3d46;
    color: white;
}

/* Add New */

.st-key-add_documents button {
    background: var(--blue);
    border: 1px solid var(--blue);
    color: white;
    min-height: 36px;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.st-key-add_documents button:hover {
    background: #1d4fd0;
    border-color: #1d4fd0;
}

/* ---------- Center pane: knowledge base ---------- */

.file-heading {
    font-size: 14px;
    color: #f0f1f5;
    font-weight: 600;
    margin-bottom: 14px;
}

/* File uploader restyled as one dashed drop card */

[data-testid="stFileUploader"] {
    background: transparent;
    padding: 0;
}

[data-testid="stFileUploaderDropzone"] {
    position: relative;
    display: flex !important;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 6px;
    min-height: 168px;
    background: #0b0c0f;
    border: 1.5px dashed #3a3d46;
    border-radius: 12px;
    padding: 20px;
    transition: border-color 0.2s ease, background 0.2s ease;
}

[data-testid="stFileUploaderDropzone"]:hover {
    border-color: var(--blue);
    background: #0d1018;
}

[data-testid="stFileUploaderDropzone"]::before {
    content: "⬆";
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: #22242b;
    color: #c9ccd6;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    margin-bottom: 6px;
}

/* Replace the default "Drag and drop files here" copy */
[data-testid="stFileUploaderDropzoneInstructions"] {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

[data-testid="stFileUploaderDropzoneInstructions"] > div {
    align-items: center;
    text-align: center;
}

[data-testid="stFileUploaderDropzoneInstructions"] span {
    font-size: 0 !important;
    line-height: 0;
}

[data-testid="stFileUploaderDropzoneInstructions"] span::after {
    content: "Click to upload or drag and drop";
    font-size: 13px;
    line-height: 1.4;
    font-weight: 500;
    color: #e9eaf0;
}

[data-testid="stFileUploaderDropzoneInstructions"] small {
    font-size: 11px;
    color: var(--muted-dark);
}

/* The browse button stretches invisibly over the whole card */
[data-testid="stFileUploaderDropzone"] button {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    opacity: 0;
    cursor: pointer;
}

/* Uploaded file chips */
[data-testid="stFileUploaderFile"] {
    background: #111317;
    border-radius: 8px;
}

.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--muted);
    font-size: 11px;
}

.breadcrumb {
    display: flex;
    align-items: center;
    height: 36px;
    color: #888e9a;
    font-size: 12px;
}

.breadcrumb b {
    color: #eceef3;
    font-weight: 600;
}

.breadcrumb .sep {
    margin: 0 8px;
    color: var(--muted-dark);
}

/* File table */

.table-head,
.file-row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 84px 76px 58px;
    align-items: center;
    column-gap: 8px;
}

.table-head {
    padding: 0 12px;
    margin: 18px 0 10px;
    color: #626873;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.4px;
}

.table-head span:nth-child(4),
.file-size {
    text-align: right;
}

.file-row {
    padding: 11px 12px;
    margin: 6px 0;
    border: 1px solid var(--border);
    background: #0f1115;
    border-radius: 8px;
    font-size: 12px;
    color: #d7d9e0;
}

.file-name {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
    font-weight: 500;
    color: #eceef3;
}

.file-name b {
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.file-icon {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    flex-shrink: 0;
}

.icon-blue { background: #15233f; }
.icon-orange { background: #3a2415; }
.icon-purple { background: #271a3d; }

.file-status {
    justify-self: start;
    color: #38d99b;
    background: #0f2a20;
    border: 1px solid #1a4a38;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 500;
    white-space: nowrap;
}

.file-added,
.file-size {
    color: var(--muted);
    font-size: 11px;
}

.empty-card {
    border: 1px dashed #2f323b;
    border-radius: 10px;
    padding: 18px;
    margin-top: 14px;
    color: #8b909c;
    font-size: 12px;
    line-height: 1.6;
    text-align: center;
}

/* ---------- Right pane: chat ---------- */

.chat-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0 0 16px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 20px;
}

.chat-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #12254a;
    border: 1px solid #1f3a73;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
}

.chat-title {
    font-size: 13px;
    font-weight: 600;
    color: white;
}

.chat-subtitle {
    font-size: 10px;
    color: var(--green);
    margin-top: 2px;
}

.chat-plus {
    margin-left: auto;
    color: #8b909c;
    font-size: 18px;
    line-height: 1;
}

/* Messages */

.assistant-row,
.user-row {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin: 12px 0 4px;
}

.user-row {
    justify-content: flex-end;
    margin: 18px 0 4px;
}

.bot-avatar,
[class*="st-key-assistant_msg_"]::before {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: #15203a;
    border: 1px solid #1f2d4d;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    flex-shrink: 0;
}

.user-avatar {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: linear-gradient(135deg, #8b7bd8, #5aa0d8);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    flex-shrink: 0;
}

.message {
    max-width: 82%;
    padding: 11px 14px;
    border-radius: 10px;
    font-size: 12px;
    line-height: 1.65;
    overflow-wrap: anywhere;
    white-space: pre-wrap;
}

.assistant-message {
    background: #17181c;
    border: 1px solid #25272d;
    color: #e1e3e8;
}

.user-message {
    background: var(--blue);
    color: white;
    border-radius: 10px;
}

.message-time {
    color: #5d626d;
    font-size: 9px;
    margin: 4px 0 6px 36px;
}

/* Assistant answer bubble (real Markdown rendered inside) */

[class*="st-key-assistant_msg_"] {
    position: relative;
    background: #17181c;
    border: 1px solid #25272d;
    border-radius: 10px;
    padding: 10px 14px 10px 14px;
    margin: 12px 0 6px 36px;
    max-width: calc(88% - 36px);
    color: #e1e3e8;
}

[class*="st-key-assistant_msg_"]::before {
    content: "🎙";
    position: absolute;
    left: -36px;
    top: 0;
}

[class*="st-key-assistant_msg_"] p,
[class*="st-key-assistant_msg_"] li {
    font-size: 12px;
    line-height: 1.65;
    color: #e1e3e8;
}

[class*="st-key-assistant_msg_"] a {
    color: var(--blue-soft);
}

/* Chat input */

[data-testid="stChatInput"] {
    background: #121317;
    border: 1px solid #272a31;
    border-radius: 10px;
}

[data-testid="stChatInput"] > div {
    background: transparent;
}

[data-testid="stChatInput"] textarea {
    color: white !important;
    font-size: 12px;
}

[data-testid="stChatInput"] button {
    background: var(--blue) !important;
    color: white !important;
    border-radius: 6px;
}

.chat-footer-note {
    text-align: center;
    color: #4f545f;
    font-size: 9px;
    margin-top: 10px;
}

/* ---------- Expanders and alerts ---------- */

[data-testid="stExpander"] {
    border: 1px solid var(--border-strong);
    border-radius: 8px;
    background: #121317;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] p {
    font-size: 11px;
}

div[data-testid="stAlert"] {
    font-size: 11px;
}

/* ---------- Small screens ---------- */

@media (max-width: 850px) {
    [data-testid="stHorizontalBlock"]:has(.pane-center) {
        flex-wrap: wrap !important;
    }

    [data-testid="stColumn"]:has(.pane-left),
    [data-testid="stColumn"]:has(.pane-center),
    [data-testid="stColumn"]:has(.pane-right),
    [data-testid="column"]:has(.pane-left),
    [data-testid="column"]:has(.pane-center),
    [data-testid="column"]:has(.pane-right) {
        flex: 1 1 100% !important;
        width: 100% !important;
        border-right: none;
        border-bottom: 1px solid var(--border);
    }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# THREE-COLUMN DASHBOARD
# =========================================================

show_left = st.session_state.sidebar_open
show_right = st.session_state.chat_open

if show_left and show_right:
    weights = [0.21, 0.38, 0.41]
elif show_left:
    weights = [0.21, 0.79]
elif show_right:
    weights = [0.46, 0.54]
else:
    weights = [1]

_panes = iter(
    st.columns(
        weights,
        gap=None,
        vertical_alignment="top",
    )
)

left = next(_panes) if show_left else None
center = next(_panes)
right = next(_panes) if show_right else None


# =========================================================
# LEFT COLUMN — NAVIGATION
# =========================================================

if left is not None:

    with left:

        st.markdown(
            '<div class="pane-marker pane-left"></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="window-dots">'
            '<span class="dot-red"></span>'
            '<span class="dot-yellow"></span>'
            '<span class="dot-green"></span>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            BRAND_HTML,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="profile">'
            '<div class="profile-avatar">👤</div>'
            'Workspace User'
            '<span class="profile-chevron">⌄</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-label">WORKSPACE</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="nav-item nav-active">⌂ &nbsp;Home</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="nav-item">♙ &nbsp;Team</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-label">CONVERSATIONS</div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "＋ New Chat",
            key="new_chat",
            use_container_width=True,
        ):
            if st.session_state.messages:
                st.session_state.conversations.append({
                    "title": st.session_state.active_conversation,
                    "messages": st.session_state.messages.copy(),
                })

            st.session_state.messages = []
            st.session_state.active_conversation = "New Chat"
            st.rerun()

        # Previous conversations
        for i, conversation in enumerate(
            reversed(st.session_state.conversations)
        ):
            if st.button(
                "▤  " + conversation["title"][:22],
                key=f"conversation_{i}",
                use_container_width=True,
            ):
                st.session_state.messages = conversation["messages"].copy()
                st.session_state.active_conversation = conversation["title"]
                st.rerun()

        st.markdown(
            '<div class="section-label">PROJECTS</div>'
            '<div class="nav-item">◈ &nbsp;Design System</div>'
            '<div class="nav-item nav-child">Documentation</div>'
            '<div class="nav-item nav-child">Components</div>'
            '<div class="nav-item nav-child">Tokens</div>'
            '<div class="nav-item">▥ &nbsp;Marketing</div>'
            '<div class="nav-item nav-child">Q3_Assets</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-label">TAGS</div>'
            '<div class="nav-item"><span class="tag-dot tag-blue"></span>Urgent</div>'
            '<div class="nav-item"><span class="tag-dot tag-grey"></span>Reviewed</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="settings-row">'
            '<div class="nav-item">⚙ &nbsp;Settings</div>'
            '</div>',
            unsafe_allow_html=True,
        )


# =========================================================
# CENTER COLUMN — KNOWLEDGE BASE
# =========================================================

with center:

    st.markdown(
        '<div class="pane-marker pane-center"></div>',
        unsafe_allow_html=True,
    )

    # Compact brand when the sidebar (and its logo) is hidden
    if not st.session_state.sidebar_open:
        st.markdown(BRAND_COMPACT_HTML, unsafe_allow_html=True)

    toggle_col, heading_col, chat_toggle_col = st.columns(
        [0.13, 0.74, 0.13],
        gap="small",
        vertical_alignment="center",
    )

    with toggle_col:
        st.button(
            "☰",
            key="toggle_sidebar",
            on_click=toggle_sidebar,
            help=(
                "Hide sidebar"
                if st.session_state.sidebar_open
                else "Show sidebar"
            ),
            use_container_width=True,
        )

    with heading_col:
        st.markdown(
            '<div class="file-heading" style="margin:0">Upload Knowledge</div>',
            unsafe_allow_html=True,
        )

    with chat_toggle_col:
        st.button(
            "💬",
            key="toggle_chat",
            on_click=toggle_chat,
            help=(
                "Hide AI assistant"
                if st.session_state.chat_open
                else "Show AI assistant"
            ),
            use_container_width=True,
        )

    uploaded_files = st.file_uploader(
        "Upload or drag and drop documents",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        st.caption(f"{len(uploaded_files)} document(s) selected")

    # Breadcrumb on the left, Add New button on the right
    breadcrumb_col, add_col = st.columns([0.55, 0.45], gap="small")

    with breadcrumb_col:
        st.markdown(
            '<div class="breadcrumb">Home<span class="sep">›</span>'
            '<b>Knowledge Base</b></div>',
            unsafe_allow_html=True,
        )

    with add_col:
        add_clicked = st.button(
            "＋ Add New",
            key="add_documents",
            use_container_width=True,
        )

    if add_clicked:
        if not uploaded_files:
            st.warning("Please select at least one document first.")
        else:
            try:
                KNOWLEDGE_BASE_DIR.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                for uploaded_file in uploaded_files:
                    destination = (
                        KNOWLEDGE_BASE_DIR / uploaded_file.name
                    )
                    destination.write_bytes(
                        uploaded_file.getbuffer()
                    )

                with st.spinner("Processing and indexing documents..."):
                    build_vector_index()
                     # Clear cached vector store and RAG chain after rebuilding the index.
                    load_vector_store.clear()
                    get_cached_rag_chain.clear()
                    st.session_state.chat_open = True

                get_cached_rag_chain.clear()

                st.success("Documents indexed successfully!")
                st.rerun()

            except Exception as error:
                st.error(f"Document processing failed: {error}")

    KNOWLEDGE_BASE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    documents = [
        path
        for path in KNOWLEDGE_BASE_DIR.iterdir()
        if path.is_file()
        and path.suffix.lower() in [".pdf", ".txt", ".docx"]
    ]

    if documents:

        st.markdown(
            '<div class="table-head">'
            '<span>FILE NAME</span>'
            '<span>STATUS</span>'
            '<span>ADDED</span>'
            '<span>SIZE</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        for document in sorted(documents):

            file_stat = document.stat()
            size_label = format_size(file_stat.st_size)
            added_label = format_added(file_stat.st_mtime)
            safe_name = html.escape(document.name)
            icon_class = FILE_ICON_CLASS.get(
                document.suffix.lower(), "icon-blue"
            )

            st.markdown(
                f"""
                <div class="file-row">
                    <div class="file-name">
                        <span class="file-icon {icon_class}">📄</span>
                        <b title="{safe_name}">{safe_name}</b>
                    </div>
                    <span class="file-status">Indexed</span>
                    <span class="file-added">{added_label}</span>
                    <span class="file-size">{size_label}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:

        st.markdown(
            """
            <div class="empty-card">
                No documents uploaded yet.<br>
                Add documents to build your knowledge base.
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# RIGHT COLUMN — AI CHAT
# =========================================================

if right is not None:

    with right:

        st.markdown(
            '<div class="pane-marker pane-right"></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="chat-header">
                <div class="chat-avatar">🎙</div>
                <div>
                    <div class="chat-title">AI Assistant</div>
                    <div class="chat-subtitle">● RAG Active</div>
                </div>
                <div class="chat-plus">+</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Welcome message
        if not st.session_state.messages:

            st.markdown(
                """
                <div class="assistant-row">
                    <div class="bot-avatar">🎙</div>
                    <div class="message assistant-message">
                        Hello! I'm ready to answer questions about your knowledge
                        base. Upload and index your documents to get started.
                    </div>
                </div>
                <div class="message-time">Just now</div>
                """,
                unsafe_allow_html=True,
            )

        # Display conversation history
        for index, message in enumerate(st.session_state.messages):

            if message["role"] == "user":

                safe_message = html.escape(message["content"])

                st.markdown(
                    f'<div class="user-row">'
                    f'<div class="message user-message">{safe_message}</div>'
                    f'<div class="user-avatar">👤</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            else:

                # Render the assistant's answer as Markdown inside a bubble.
                with st.container(key=f"assistant_msg_{index}"):

                    st.markdown(message["content"])

                    if message.get("sources"):

                        with st.expander("📚 Sources"):
                            for source in message["sources"]:
                                st.write(f"• {source}")

        # Chat input
        question = st.chat_input(
            "Ask a question about your documents..."
        )

        st.markdown(
            '<div class="chat-footer-note">'
            'AI can make mistakes. Verify important information.'
            '</div>',
            unsafe_allow_html=True,
        )

        if question:

            if st.session_state.active_conversation == "New Chat":
                st.session_state.active_conversation = question[:28]

            st.session_state.messages.append({
                "role": "user",
                "content": question,
            })

            try:

                validate_config()

                with st.spinner("Searching your knowledge base..."):

                    chain = get_cached_rag_chain()
                    # Exclude the current question; only pass earlier messages.
                    previous_messages = st.session_state.messages[:-1]

                    result = chain(
                        question,
                        chat_history=previous_messages,
                    )

                answer = result["answer"]
                sources = result.get("sources", [])

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                })

            except FileNotFoundError:

                error_message = (
                    "Your knowledge base is not ready yet. "
                    "Please upload documents and click Add New first."
                )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message,
                    "sources": [],
                })

            except Exception as error:

                error_message = f"An error occurred: {error}"

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message,
                    "sources": [],
                })

            st.rerun()