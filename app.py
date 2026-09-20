import streamlit as st
import pandas as pd
import plotly.express as px

from utils.preprocessing import load_transactions
from utils.analysis import (
    get_income,
    get_expenses,
    get_net_cash_flow,
    get_category_spending,
    get_monthly_summary,
    get_monthly_comparison,
    get_recurring_expenses,
    get_upcoming_obligations,
    detect_unusual_spending,
    get_budget_status,
    generate_financial_insights,
)
from utils.simulator import (
    calculate_monthly_savings,
    calculate_goal_timeline,
    calculate_what_if,
)
from utils.agent import answer_question

# Page Configuration
st.set_page_config(
    page_title="FinPilot — Financial Intelligence Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper function to render HTML cleanly without Markdown code-block escaping
def render_html(html_str):
    clean_lines = [line.strip() for line in html_str.strip().splitlines()]
    st.markdown("".join(clean_lines), unsafe_allow_html=True)

# Initialize session states
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# Theme variables configuration
if st.session_state.theme == "dark":
    theme_css = """
    :root {
        --bg-base: #0A0D13;
        --surface-card: #12161F;
        --surface-border: #232939;
        --surface-elevated: #1B2130;
        --primary-accent: #5B8DEF;
        --secondary-accent: #8B7CF6;
        --success: #34D399;
        --danger: #F87171;
        --warning: #F5B75B;
        --text-primary: #F2F4F8;
        --text-muted: #8B93A6;
        --divider: #1E2433;
    }
    """
else:
    theme_css = """
    :root {
        --bg-base: #F8FAFC;
        --surface-card: #FFFFFF;
        --surface-border: #E2E8F0;
        --surface-elevated: #F1F5F9;
        --primary-accent: #2563EB;
        --secondary-accent: #7C3AED;
        --success: #059669;
        --danger: #DC2626;
        --warning: #D97706;
        --text-primary: #0F172A;
        --text-muted: #64748B;
        --divider: #E2E8F0;
    }
    """

# Consolidated CSS Injection
css_imports = "<style>\n@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700;800&display=swap');\n"
css_body = """
    /* Global Resets */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--bg-base) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 15px !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    .block-container {
        max-width: 1300px !important;
        padding-top: 1.25rem !important;
        padding-bottom: 4rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    #MainMenu, footer, header {
        visibility: hidden;
    }

    /* DOPE LOGO STYLING */
    .finpilot-dope-logo {
        display: inline-flex;
        align-items: center;
        gap: 12px;
    }

    .logo-icon-glow {
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, rgba(91, 141, 239, 0.15) 0%, rgba(139, 124, 246, 0.15) 100%);
        border: 1px solid rgba(91, 141, 239, 0.3);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 20px rgba(91, 141, 239, 0.25);
    }

    .logo-title-text {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 26px;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -0.5px;
    }

    .logo-highlight {
        background: linear-gradient(135deg, #5B8DEF 0%, #8B7CF6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Typography Utilities */
    .font-heading {
        font-family: 'Space Grotesk', sans-serif !important;
    }

    .tabular-num {
        font-family: 'Space Grotesk', sans-serif !important;
        font-variant-numeric: tabular-nums !important;
    }

    /* Login Page Styling */
    .login-brand-panel {
        background: radial-gradient(circle at 10% 20%, rgba(91, 141, 239, 0.15) 0%, transparent 50%),
                    radial-gradient(circle at 90% 80%, rgba(139, 124, 246, 0.15) 0%, transparent 50%),
                    var(--surface-card);
        border: 1px solid var(--surface-border);
        border-radius: 20px;
        padding: 52px;
        position: relative;
        overflow: hidden;
    }

    .login-hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 38px;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.18;
        letter-spacing: -0.5px;
        margin: 24px 0 14px 0;
    }

    .login-hero-sub {
        font-size: 16px;
        color: var(--text-muted);
        line-height: 1.6;
        margin-bottom: 0;
    }

    .login-form-panel {
        background-color: var(--surface-card);
        border: 1px solid var(--surface-border);
        border-radius: 20px;
        padding: 36px 40px 24px 40px;
        margin-bottom: 16px;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: var(--surface-card) !important;
        border-right: 1px solid var(--surface-border) !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--text-muted) !important;
        font-size: 14px !important;
    }

    .sidebar-brand-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding-bottom: 20px;
        margin-bottom: 20px;
        border-bottom: 1px solid var(--divider);
    }

    /* KPI Tiles with Glow */
    .kpi-row-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 28px;
    }

    .kpi-glow-card {
        background-color: var(--surface-card);
        border: 1px solid var(--surface-border);
        border-radius: 14px;
        padding: 22px 24px;
        position: relative;
        overflow: hidden;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }

    .kpi-glow-card:hover {
        border-color: var(--primary-accent);
    }

    .kpi-glow-income::before {
        content: '';
        position: absolute;
        top: -20px;
        right: -20px;
        width: 90px;
        height: 90px;
        background: radial-gradient(circle, rgba(52, 211, 153, 0.25) 0%, transparent 70%);
        pointer-events: none;
    }

    .kpi-glow-expense::before {
        content: '';
        position: absolute;
        top: -20px;
        right: -20px;
        width: 90px;
        height: 90px;
        background: radial-gradient(circle, rgba(248, 113, 113, 0.25) 0%, transparent 70%);
        pointer-events: none;
    }

    .kpi-glow-net::before {
        content: '';
        position: absolute;
        top: -20px;
        right: -20px;
        width: 90px;
        height: 90px;
        background: radial-gradient(circle, rgba(91, 141, 239, 0.25) 0%, transparent 70%);
        pointer-events: none;
    }

    .kpi-glow-savings::before {
        content: '';
        position: absolute;
        top: -20px;
        right: -20px;
        width: 90px;
        height: 90px;
        background: radial-gradient(circle, rgba(139, 124, 246, 0.25) 0%, transparent 70%);
        pointer-events: none;
    }

    .kpi-top-meta {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }

    .kpi-label-text {
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-muted);
    }

    .kpi-big-num {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 34px;
        font-weight: 700;
        color: var(--text-primary);
        font-variant-numeric: tabular-nums;
        letter-spacing: -0.5px;
        margin-bottom: 10px;
    }

    .delta-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 13px;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 6px;
    }

    .delta-pill.pos {
        background: rgba(52, 211, 153, 0.12);
        color: var(--success);
    }

    .delta-pill.neg {
        background: rgba(248, 113, 113, 0.12);
        color: var(--danger);
    }

    /* Content Cards */
    .content-card-box {
        background-color: var(--surface-card);
        border: 1px solid var(--surface-border);
        border-radius: 14px;
        padding: 26px;
        margin-bottom: 24px;
    }

    .card-header-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 21px;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 6px 0;
    }

    .card-header-sub {
        font-size: 14px;
        color: var(--text-muted);
        margin: 0 0 20px 0;
    }

    /* File Dropzone Card */
    .file-dropzone-box {
        background-color: var(--surface-card);
        border: 1.5px dashed var(--surface-border);
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 24px;
    }

    .file-success-badge {
        background: rgba(52, 211, 153, 0.08);
        border: 1px solid rgba(52, 211, 153, 0.25);
        border-radius: 10px;
        padding: 14px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 14px;
    }

    /* Simulator Lab Treatment */
    .simulator-lab-container {
        background: linear-gradient(180deg, var(--surface-elevated) 0%, var(--surface-card) 100%);
        border: 1.5px solid rgba(139, 124, 246, 0.35);
        border-radius: 16px;
        padding: 32px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
        margin-bottom: 28px;
        position: relative;
    }

    .simulator-lab-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #5B8DEF 0%, #8B7CF6 50%, #34D399 100%);
        border-radius: 16px 16px 0 0;
    }

    .lab-tag-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(90deg, rgba(91, 141, 239, 0.2) 0%, rgba(139, 124, 246, 0.2) 100%);
        border: 1px solid rgba(139, 124, 246, 0.4);
        color: #8B7CF6;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 4px 12px;
        border-radius: 6px;
        margin-bottom: 16px;
    }

    .sim-output-highlight {
        background-color: var(--surface-elevated);
        border: 1px solid var(--surface-border);
        border-radius: 12px;
        padding: 24px;
    }

    /* Executive Brief */
    .executive-brief-card {
        background: linear-gradient(180deg, var(--surface-elevated) 0%, var(--surface-card) 100%);
        border: 1px solid var(--surface-border);
        border-left: 4px solid var(--primary-accent);
        border-radius: 12px;
        padding: 28px;
        margin-bottom: 24px;
    }

    .brief-bullet-row {
        background: rgba(125, 125, 125, 0.05);
        border: 1px solid var(--divider);
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        font-size: 15px;
        color: var(--text-primary);
        line-height: 1.55;
    }

    /* AI Agent Panel */
    .agent-chat-wrapper {
        background-color: var(--surface-card);
        border: 1px solid var(--surface-border);
        border-radius: 16px;
        padding: 30px;
        margin-bottom: 24px;
    }

    .agent-header-row {
        display: flex;
        align-items: center;
        gap: 12px;
        padding-bottom: 18px;
        border-bottom: 1px solid var(--divider);
        margin-bottom: 22px;
    }

    .agent-avatar-circle {
        width: 42px;
        height: 42px;
        background: linear-gradient(135deg, #5B8DEF 0%, #8B7CF6 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFF;
    }

    .agent-bubble-bot {
        background-color: var(--surface-elevated);
        border: 1px solid var(--surface-border);
        border-radius: 14px 14px 14px 2px;
        padding: 20px 24px;
        margin-top: 16px;
        color: var(--text-primary);
        font-size: 15px;
        line-height: 1.65;
    }

    /* Badge Pills */
    .tag-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
    }

    .tag-blue { background: rgba(91, 141, 239, 0.15); color: var(--primary-accent); }
    .tag-green { background: rgba(52, 211, 153, 0.15); color: var(--success); }
    .tag-amber { background: rgba(245, 183, 91, 0.15); color: var(--warning); }
    .tag-violet { background: rgba(139, 124, 246, 0.15); color: var(--secondary-accent); }

    /* Streamlit Native Label & Input High-Contrast Visibility */
    label,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span,
    [data-testid="stWidgetLabel"] label,
    .stSelectbox label,
    .stTextInput label,
    .stNumberInput label {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span {
        color: var(--text-primary) !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--text-muted) !important;
    }

    /* Radio button options */
    div[role="radiogroup"] label,
    div[role="radiogroup"] label p,
    div[role="radiogroup"] label span,
    [data-testid="stRadio"] label p {
        color: var(--text-primary) !important;
        font-size: 14.5px !important;
        font-weight: 500 !important;
    }

    /* Selectbox dropdown & popover menu options */
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div,
    ul[role="listbox"],
    ul[role="listbox"] li,
    div[role="option"] {
        color: var(--text-primary) !important;
        background-color: var(--surface-card) !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="menu"] {
        background-color: var(--surface-card) !important;
        border: 1px solid var(--surface-border) !important;
        color: var(--text-primary) !important;
    }

    /* Metric values and labels */
    [data-testid="stMetricLabel"] p {
        color: var(--text-muted) !important;
    }
    [data-testid="stMetricValue"] div {
        color: var(--text-primary) !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    /* Override Input and Password Eye Toggle Styling */
    div[data-baseweb="input"] {
        background-color: var(--surface-elevated) !important;
        border: 1px solid var(--surface-border) !important;
        border-radius: 8px !important;
    }

    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] > div {
        background-color: transparent !important;
        color: var(--text-primary) !important;
        font-size: 15px !important;
    }

    div[data-baseweb="input"] button {
        background-color: transparent !important;
        border: none !important;
        color: var(--text-muted) !important;
    }

    div[data-baseweb="input"] button:hover {
        color: var(--text-primary) !important;
    }

    .stButton button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        padding: 8px 18px !important;
        transition: all 0.15s ease !important;
    }
    """

render_html(css_imports + theme_css + css_body)

# Helper function for Plotly theme matching active mode
def apply_plotly_theme(fig):
    text_color = "#F2F4F8" if st.session_state.theme == "dark" else "#0F172A"
    grid_color = "#1E2433" if st.session_state.theme == "dark" else "#E2E8F0"
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=text_color, size=13),
        title_font=dict(color=text_color),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            font=dict(color=text_color, size=13),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            gridcolor=grid_color,
            zerolinecolor=grid_color,
            tickfont=dict(color=text_color, size=12),
            title=dict(font=dict(color=text_color, size=13))
        ),
        yaxis=dict(
            gridcolor=grid_color,
            zerolinecolor=grid_color,
            tickfont=dict(color=text_color, size=12),
            title=dict(font=dict(color=text_color, size=13))
        ),
        colorway=["#5B8DEF", "#34D399", "#F5B75B", "#F87171", "#8B7CF6", "#38BDF8"]
    )
    return fig


# =========================================================
# VIEW ROUTING: LOGIN SCREEN VS DASHBOARD
# =========================================================

if not st.session_state.logged_in:
    # -----------------------------
    # LOGIN SCREEN (UI-ONLY GATE)
    # -----------------------------
    col_brand, col_form = st.columns([1.2, 1], gap="large")

    with col_brand:
        render_html("""
        <div class="login-brand-panel">
            <div class="finpilot-dope-logo">
                <div class="logo-icon-glow">
                    <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="url(#logoGrad)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M2 17L12 22L22 17" stroke="url(#logoGrad)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M2 12L12 17L22 12" stroke="url(#logoGrad)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <defs>
                            <linearGradient id="logoGrad" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                                <stop stop-color="#5B8DEF"/>
                                <stop offset="0.5" stop-color="#8B7CF6"/>
                                <stop offset="1" stop-color="#34D399"/>
                            </linearGradient>
                        </defs>
                    </svg>
                </div>
                <span class="logo-title-text" style="font-size: 28px;">Fin<span class="logo-highlight">Pilot</span></span>
            </div>
            <h1 class="login-hero-title">Autonomous Financial Decision Intelligence</h1>
            <p class="login-hero-sub">Engineered analytics, predictive scenario modeling, and copilot insights for personal wealth management.</p>
        </div>
        """)

    with col_form:
        render_html("""
        <div class="login-form-panel">
            <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 700; margin: 0 0 6px 0; color: var(--text-primary);">Log in to FinPilot</h2>
            <p style="font-size: 14px; color: var(--text-muted); margin: 0 0 24px 0;">Enter your credentials to access the intelligence dashboard</p>
        </div>
        """)

        login_email = st.text_input("Work or Personal Email", value="alex.morgan@finpilot.io", key="login_email_input")
        login_pass = st.text_input("Password", value="••••••••••••", type="password", key="login_pass_input")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Log in to FinPilot", type="primary", use_container_width=True, key="btn_login_submit"):
                st.session_state.logged_in = True
                st.rerun()

        with c2:
            if st.button("Continue with Google", use_container_width=True, key="btn_login_google"):
                st.session_state.logged_in = True
                st.rerun()

        st.markdown('<div style="margin-top: 16px;"></div>', unsafe_allow_html=True)
        if st.button("Start free interactive demo", type="secondary", use_container_width=True, key="btn_login_demo"):
            st.session_state.logged_in = True
            st.rerun()

else:
    # =========================================================
    # LOGGED IN DASHBOARD VIEW
    # =========================================================

    # -----------------------------
    # TOP HEADER BAR WITH TOP-RIGHT ICON-ONLY THEME TOGGLE
    # -----------------------------
    c_brand, c_theme = st.columns([6, 1])

    with c_brand:
        render_html("""
        <div class="finpilot-dope-logo">
            <div class="logo-icon-glow">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="url(#logoGradTop)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 17L12 22L22 17" stroke="url(#logoGradTop)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 12L12 17L22 12" stroke="url(#logoGradTop)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                    <defs>
                        <linearGradient id="logoGradTop" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                            <stop stop-color="#5B8DEF"/>
                            <stop offset="0.5" stop-color="#8B7CF6"/>
                            <stop offset="1" stop-color="#34D399"/>
                        </linearGradient>
                    </defs>
                </svg>
            </div>
            <div>
                <span class="logo-title-text" style="font-size: 24px;">Fin<span class="logo-highlight">Pilot</span></span>
                <span style="font-size: 13px; color: var(--text-muted); margin-left: 10px; font-weight: 500;">Financial Intelligence Engine</span>
            </div>
        </div>
        """)

    with c_theme:
        theme_icon = "☀️" if st.session_state.theme == "dark" else "🌙"
        if st.button(theme_icon, key="btn_top_theme_icon_only", help="Toggle Light / Dark Mode"):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()

    st.markdown('<div style="margin-bottom: 20px;"></div>', unsafe_allow_html=True)

    # -----------------------------
    # SIDEBAR NAVIGATION & PROFILE
    # -----------------------------
    with st.sidebar:
        render_html("""
        <div class="sidebar-brand-header">
            <div class="finpilot-dope-logo">
                <div class="logo-icon-glow">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="url(#logoGradSb)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M2 17L12 22L22 17" stroke="url(#logoGradSb)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M2 12L12 17L22 12" stroke="url(#logoGradSb)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <defs>
                            <linearGradient id="logoGradSb" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                                <stop stop-color="#5B8DEF"/>
                                <stop offset="0.5" stop-color="#8B7CF6"/>
                                <stop offset="1" stop-color="#34D399"/>
                            </linearGradient>
                        </defs>
                    </svg>
                </div>
                <div>
                    <span class="logo-title-text" style="font-size: 20px;">Fin<span class="logo-highlight">Pilot</span></span>
                    <div style="font-size: 10px; color: var(--primary-accent); font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;">ENTERPRISE EDITION</div>
                </div>
            </div>
        """)

        nav_selection = st.radio(
            "NAVIGATION",
            [
                "Overview & Brief",
                "Spending & Trends",
                "Subscriptions & Risks",
                "Budgets & Goals",
                "What-If Simulator",
                "Ask FinPilot AI"
            ],
            label_visibility="visible"
        )

        st.markdown('<div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--divider);">', unsafe_allow_html=True)
        render_html("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
            <div style="width: 32px; height: 32px; background: var(--surface-elevated); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; color: var(--primary-accent);">AM</div>
            <div>
                <div style="font-size: 13px; font-weight: 600; color: var(--text-primary);">Alex Morgan</div>
                <div style="font-size: 11px; color: var(--text-muted);">Pro Tier Subscriber</div>
            </div>
        </div>
        """)

        if st.button("Log Out", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------
    # FEATURE 1: CSV/XLSX TRANSACTION UPLOAD & LOAD
    # -----------------------------
    render_html('<div class="file-dropzone-box">')
    uploaded_file = st.file_uploader(
        "Drag & drop or browse transaction statement (CSV / XLSX)",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:
        df = load_transactions(uploaded_file)
        source_name = uploaded_file.name
    else:
        FILE_PATH = "data/personal_transactions_dashboard_ready (2).xlsx"
        df = load_transactions(FILE_PATH)
        source_name = "personal_transactions_dashboard_ready (2).xlsx (Demo Statement)"

    render_html(f"""
    <div class="file-success-badge">
        <span style="color: var(--success); font-size: 14px; font-weight: 600; display: flex; align-items: center; gap: 6px;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
            Active Statement: {source_name}
        </span>
        <span style="color: var(--text-muted); font-size: 13px; font-family: 'Space Grotesk', sans-serif;">{len(df):,} transactions indexed</span>
    </div>
    """)
    render_html('</div>')

    # -----------------------------
    # CALCULATE METRICS
    # -----------------------------
    income = get_income(df)
    expenses = get_expenses(df)
    net_cash_flow = get_net_cash_flow(df)
    savings_rate = ((income - expenses) / income * 100) if income > 0 else 0.0

    # -----------------------------
    # FEATURE 2: INCOME, EXPENSES, NET CASH FLOW (HERO KPI ROW)
    # -----------------------------
    net_class = "pos" if net_cash_flow >= 0 else "neg"
    net_symbol = "▲" if net_cash_flow >= 0 else "▼"

    render_html(f"""
    <div class="kpi-row-grid">
        <div class="kpi-glow-card kpi-glow-income">
            <div class="kpi-top-meta">
                <span class="kpi-label-text">Total Income</span>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
            </div>
            <div class="kpi-big-num">${income:,.2f}</div>
            <span class="delta-pill pos">▲ Total Inflow</span>
        </div>
        
        <div class="kpi-glow-card kpi-glow-expense">
            <div class="kpi-top-meta">
                <span class="kpi-label-text">Total Expenses</span>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F87171" stroke-width="2"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg>
            </div>
            <div class="kpi-big-num">${expenses:,.2f}</div>
            <span class="delta-pill neg">▼ Total Outflow</span>
        </div>
        
        <div class="kpi-glow-card kpi-glow-net">
            <div class="kpi-top-meta">
                <span class="kpi-label-text">Net Cash Flow</span>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5B8DEF" stroke-width="2"><path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"></path><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"></path><path d="M18 12a2 2 0 0 0 0 4h4v-4z"></path></svg>
            </div>
            <div class="kpi-big-num">${net_cash_flow:,.2f}</div>
            <span class="delta-pill {net_class}">{net_symbol} Net Balance</span>
        </div>
        
        <div class="kpi-glow-card kpi-glow-savings">
            <div class="kpi-top-meta">
                <span class="kpi-label-text">Savings Efficiency</span>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#8B7CF6" stroke-width="2"><path d="M19 5c-1.5 0-2.8 1.4-3 2-3.5-1.5-11-.3-11 5 0 1.8 0 3 2 4.5V20h4v-2h3v2h4v-3.5c1-.5 1.5-1 2.5-2 2.5-2.5 2.5-6 0-8.5-1-1-1.5-1-1.5-1z"></path><circle cx="16" cy="11" r="1"></circle></svg>
            </div>
            <div class="kpi-big-num">{savings_rate:.1f}%</div>
            <span class="delta-pill pos">▲ Retention Rate</span>
        </div>
    </div>
    """)

    # -----------------------------
    # VIEW ROUTING BASED ON SIDEBAR NAV
    # -----------------------------

    # =========================================================
    # VIEW 1: OVERVIEW & EXECUTIVE BRIEF
    # =========================================================
    if nav_selection == "Overview & Brief":
        # FEATURE 15: FINANCIAL BRIEF
        render_html("""
        <div class="executive-brief-card">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--primary-accent)" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                    <h3 style="font-family: 'Space Grotesk', sans-serif; margin: 0; font-size: 21px; font-weight: 700; color: var(--text-primary);">FinPilot Executive Financial Brief</h3>
                </div>
                <span class="tag-badge tag-blue">SYNTHESIZED INSIGHTS</span>
            </div>
        """)

        brief = generate_financial_insights(df, 3000.0)
        if brief:
            for insight in brief:
                render_html(f'<div class="brief-bullet-row">• {insight}</div>')
        else:
            st.info("Not enough transaction data to generate insights.")
        render_html('</div>')

        c_rec, c_sch = st.columns([1, 1])

        with c_rec:
            render_html("""
            <div class="content-card-box">
                <h3 class="card-header-title">Recent Transactions</h3>
                <p class="card-header-sub">Latest 20 activity records sorted chronologically</p>
            """)
            # FEATURE 13: RECENT TRANSACTIONS
            st.dataframe(
                df.sort_values("Date", ascending=False).head(20),
                use_container_width=True,
                hide_index=True
            )
            render_html('</div>')

        with c_sch:
            render_html("""
            <div class="content-card-box">
                <h3 class="card-header-title">Search Transactions</h3>
                <p class="card-header-sub">Filter ledger by vendor description, category, or account</p>
            """)
            # FEATURE 12: TRANSACTION SEARCH
            search = st.text_input(
                "Search query",
                placeholder="Type Vendor name, Uber, Rent...",
                key="tx_search_q"
            )
            if search:
                mask = (
                    df["Description"].astype(str).str.contains(search, case=False, na=False)
                    | df["Category"].astype(str).str.contains(search, case=False, na=False)
                    | df["Account Name"].astype(str).str.contains(search, case=False, na=False)
                )
                results = df[mask]
                st.dataframe(results, use_container_width=True, hide_index=True)
            else:
                st.caption("Enter a string above to run multi-column search on your transactions.")
            render_html('</div>')


    # =========================================================
    # VIEW 2: SPENDING & TRENDS
    # =========================================================
    elif nav_selection == "Spending & Trends":
        category_spending = get_category_spending(df)

        # FEATURE 3: SPENDING CATEGORY ANALYSIS
        sc1, sc2 = st.columns(2)

        with sc1:
            render_html("""
            <div class="content-card-box">
                <h3 class="card-header-title">Top Spending Categories</h3>
                <p class="card-header-sub">Top 10 categories ranked by volume</p>
            """)
            fig_bar = px.bar(
                category_spending.head(10),
                x="Amount",
                y="Category",
                orientation="h"
            )
            apply_plotly_theme(fig_bar)
            fig_bar.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_bar, use_container_width=True)
            render_html('</div>')

        with sc2:
            render_html("""
            <div class="content-card-box">
                <h3 class="card-header-title">Expense Distribution</h3>
                <p class="card-header-sub">Proportional category share</p>
            """)
            fig_pie = px.pie(
                category_spending,
                names="Category",
                values="Amount",
                hole=0.4
            )
            apply_plotly_theme(fig_pie)
            st.plotly_chart(fig_pie, use_container_width=True)
            render_html('</div>')

        # FEATURE 4: MONTHLY ANALYSIS
        render_html("""
        <div class="content-card-box">
            <h3 class="card-header-title">Monthly Trajectory & Breakdown</h3>
            <p class="card-header-sub">Historical monthly debit/credit flow</p>
        """)
        monthly = get_monthly_summary(df)
        monthly_pivot = monthly.pivot(
            index="Month",
            columns="Transaction Type",
            values="Amount"
        ).fillna(0).reset_index()

        mc1, mc2 = st.columns(2)

        with mc1:
            st.caption("Expense Trajectory Line")
            if "debit" in monthly_pivot.columns:
                fig_line = px.line(
                    monthly_pivot,
                    x="Month",
                    y="debit",
                    markers=True
                )
                apply_plotly_theme(fig_line)
                st.plotly_chart(fig_line, use_container_width=True)

        with mc2:
            st.caption("Income vs Expense Grouped Bar")
            avail_cols = [c for c in ["credit", "debit"] if c in monthly_pivot.columns]
            fig_group = px.bar(
                monthly_pivot,
                x="Month",
                y=avail_cols,
                barmode="group"
            )
            apply_plotly_theme(fig_group)
            st.plotly_chart(fig_group, use_container_width=True)

        render_html('</div>')

        # FEATURE 8: MONTH-TO-MONTH COMPARISON
        render_html("""
        <div class="content-card-box">
            <h3 class="card-header-title">Month-to-Month Variance Analysis</h3>
            <p class="card-header-sub">Period-over-period category fluctuations</p>
        """)
        comparison = get_monthly_comparison(df)
        comparison_display = comparison.copy()
        comparison_display["Change"] = comparison_display["Change"].round(2)
        comparison_display["Change_%"] = comparison_display["Change_%"].round(2)
        st.dataframe(comparison_display, use_container_width=True, hide_index=True)
        render_html('</div>')


    # =========================================================
    # VIEW 3: SUBSCRIPTIONS & RISKS
    # =========================================================
    elif nav_selection == "Subscriptions & Risks":
        rc1, rc2 = st.columns(2)

        # FEATURE 5: RECURRING EXPENSES / SUBSCRIPTIONS
        with rc1:
            render_html("""
            <div class="content-card-box">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <h3 class="card-header-title" style="margin: 0;">Recurring Expenses & Subscriptions</h3>
                    <span class="tag-badge tag-blue">ACTIVE PATTERNS</span>
                </div>
                <p class="card-header-sub">Vendor subscription detections</p>
            """)
            recurring = get_recurring_expenses(df)
            if recurring.empty:
                st.info("No recurring expenses detected.")
            else:
                display_recurring = recurring.copy()
                display_recurring["Average_Amount"] = display_recurring["Average_Amount"].round(2)
                display_recurring["Total_Spent"] = display_recurring["Total_Spent"].round(2)
                st.dataframe(display_recurring, use_container_width=True, hide_index=True)
            render_html('</div>')

        # FEATURE 6: UPCOMING FINANCIAL OBLIGATIONS
        with rc2:
            render_html("""
            <div class="content-card-box">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <h3 class="card-header-title" style="margin: 0;">Upcoming Financial Obligations</h3>
                    <span class="tag-badge tag-violet">PROJECTED</span>
                </div>
                <p class="card-header-sub">Anticipated upcoming liabilities</p>
            """)
            obligations = get_upcoming_obligations(df)
            if obligations.empty:
                st.info("No recurring obligations detected.")
            else:
                st.dataframe(obligations, use_container_width=True, hide_index=True)
            render_html('</div>')

        # FEATURE 7: UNUSUAL SPENDING DETECTION
        render_html("""
        <div class="content-card-box">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <h3 class="card-header-title" style="margin: 0;">Unusual Spending Anomaly Detection</h3>
                <span class="tag-badge tag-amber">STATISTICAL OUTLIERS</span>
            </div>
            <p class="card-header-sub">High Z-score variance transaction records</p>
        """)
        unusual = detect_unusual_spending(df)
        if unusual.empty:
            st.success("No unusually large transactions detected.")
        else:
            unusual_display = unusual[
                ["Date", "Description", "Category", "Amount", "Z_Score"]
            ].copy()
            unusual_display["Z_Score"] = unusual_display["Z_Score"].round(2)
            st.dataframe(unusual_display.head(20), use_container_width=True, hide_index=True)
        render_html('</div>')


    # =========================================================
    # VIEW 4: BUDGETS & GOALS
    # =========================================================
    elif nav_selection == "Budgets & Goals":
        bg1, bg2 = st.columns(2)

        # FEATURE 9: BUDGET TRACKING
        with bg1:
            render_html("""
            <div class="content-card-box">
                <h3 class="card-header-title">Monthly Budget Allowance</h3>
                <p class="card-header-sub">Set and track monthly spending target</p>
            """)
            monthly_budget = st.number_input(
                "Monthly Budget Target ($)",
                min_value=0.0,
                value=3000.0,
                step=100.0,
                key="view_budget_input"
            )
            budget_status = get_budget_status(df, monthly_budget)

            b1, b2, b3 = st.columns(3)
            b1.metric("Budget Target", f"${budget_status['budget']:,.2f}")
            b2.metric("Total Spent", f"${budget_status['spent']:,.2f}")
            b3.metric("Remaining", f"${budget_status['remaining']:,.2f}")

            # Visual progress bar
            pct_used = min(max(budget_status['percentage_used'], 0), 100)
            bar_color = "var(--success)" if pct_used < 85 else "var(--warning)" if pct_used <= 100 else "var(--danger)"
            render_html(f"""
            <div style="margin: 16px 0 12px 0;">
                <div style="display: flex; justify-content: space-between; font-size: 13px; color: var(--text-muted); margin-bottom: 6px;">
                    <span>Budget Utilization</span>
                    <span style="font-weight: 700; color: var(--text-primary);">{pct_used:.1f}%</span>
                </div>
                <div style="width: 100%; height: 8px; background: var(--surface-elevated); border-radius: 4px; overflow: hidden;">
                    <div style="width: {pct_used}%; height: 100%; background: {bar_color}; border-radius: 4px;"></div>
                </div>
            </div>
            """)

            if budget_status["remaining"] < 0:
                st.warning("Budget exceeded for this statement period.")
            else:
                st.success(f"Remaining: ${budget_status['remaining']:,.2f} under threshold.")
            render_html('</div>')

        # FEATURE 10: FINANCIAL GOALS
        with bg2:
            render_html("""
            <div class="content-card-box">
                <h3 class="card-header-title">Financial Goal Planning</h3>
                <p class="card-header-sub">Calculate timeline based on savings rate</p>
            """)
            goal_name = st.text_input("Goal Target Name", "Laptop", key="view_goal_name")
            goal_amount = st.number_input(
                "Goal Amount ($)",
                min_value=0.0,
                value=5000.0,
                step=500.0,
                key="view_goal_amt"
            )

            number_of_months = df["Month"].nunique() if "Month" in df.columns else 1
            if number_of_months > 0:
                average_monthly_income = income / number_of_months
                average_monthly_expenses = expenses / number_of_months
                monthly_savings = calculate_monthly_savings(
                    average_monthly_income,
                    average_monthly_expenses
                )
                goal_months = calculate_goal_timeline(
                    goal_amount,
                    max(monthly_savings, 0)
                )

                st.metric("Estimated Monthly Savings Rate", f"${monthly_savings:,.2f}")

                if goal_months is not None:
                    st.info(
                        f"At your current savings rate, you can reach your **{goal_name}** goal "
                        f"in approximately **{goal_months:.1f} months**."
                    )
                else:
                    st.warning("Current spending leaves insufficient monthly savings to reach this goal.")
            render_html('</div>')


    # =========================================================
    # VIEW 5: WHAT-IF SIMULATOR ("LAB" TREATMENT)
    # =========================================================
    elif nav_selection == "What-If Simulator":
        # FEATURE 11: WHAT-IF FINANCIAL SIMULATOR
        category_spending = get_category_spending(df)
        categories = category_spending["Category"].tolist()

        render_html("""
        <div class="simulator-lab-container">
            <span class="lab-tag-pill">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M9 3h6v3E1l5 9a2 2 0 0 1-1.8 2.9H5.8A2 2 0 0 1 4 15l5-9V3z"></path><line x1="9" y1="9" x2="15" y2="9"></line></svg>
                SIMULATION LAB ENGINE
            </span>
            <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 700; color: var(--text-primary); margin: 0 0 6px 0;">What-If Financial Simulator</h2>
            <p style="font-size: 14px; color: var(--text-muted); margin: 0 0 24px 0;">Model proposed category reductions to calculate exact goal timeline acceleration</p>
        """)

        if categories:
            number_of_months = df["Month"].nunique() if "Month" in df.columns else 1
            average_monthly_income = income / number_of_months if number_of_months > 0 else 0
            average_monthly_expenses = expenses / number_of_months if number_of_months > 0 else 0
            monthly_savings = calculate_monthly_savings(average_monthly_income, average_monthly_expenses)
            goal_amount = 5000.0

            s1, s2 = st.columns([1, 1])

            with s1:
                selected_category = st.selectbox(
                    "Choose category to optimize",
                    categories,
                    key="lab_cat_select"
                )

                current_category_total = category_spending[
                    category_spending["Category"] == selected_category
                ]["Amount"].iloc[0]

                current_monthly_category = current_category_total / max(number_of_months, 1)

                render_html(f"""
                <div style="background: rgba(125,125,125,0.05); border: 1px solid var(--surface-border); border-radius: 10px; padding: 14px 18px; margin: 14px 0 18px 0;">
                    <div style="font-size: 13px; color: var(--text-muted); text-transform: uppercase;">Current Monthly Avg for {selected_category}</div>
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 26px; font-weight: 700; color: var(--text-primary); font-variant-numeric: tabular-nums;">${current_monthly_category:,.2f}</div>
                </div>
                """)

                new_monthly_category = st.number_input(
                    "New Target Monthly Spending ($)",
                    min_value=0.0,
                    value=float(round(current_monthly_category, 2)),
                    step=100.0,
                    key="lab_new_spend_input"
                )

            with s2:
                result = calculate_what_if(
                    current_monthly_category,
                    new_monthly_category,
                    max(monthly_savings, 0),
                    goal_amount
                )

                render_html('<div class="sim-output-highlight">')
                render_html("""
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
                    <h4 style="font-family: 'Space Grotesk', sans-serif; margin: 0; font-size: 17px; color: var(--text-primary);">Simulation Forecast</h4>
                    <span class="tag-badge tag-violet">PROJECTED IMPACT</span>
                </div>
                """)

                r1, r2 = st.columns(2)
                r1.metric("Monthly Reduction", f"${result['monthly_reduction']:,.2f}")
                r2.metric("New Monthly Savings", f"${result['new_monthly_savings']:,.2f}")

                if result["months_saved"] is not None:
                    if result["months_saved"] > 0:
                        st.success(
                            f"This reduction accelerates your goal by approximately **{result['months_saved']:.1f} months** earlier!"
                        )
                    elif result["months_saved"] < 0:
                        st.warning("Increasing spending extends your goal timeline.")
                    else:
                        st.info("Timeline remains unchanged at this target.")
                render_html('</div>')

        render_html('</div>')


    # =========================================================
    # VIEW 6: ASK FINPILOT AI
    # =========================================================
    elif nav_selection == "Ask FinPilot AI":
        # FEATURE 14: FINPILOT AI AGENT WITH SUGGESTED QUESTIONS
        render_html("""
        <div class="agent-chat-wrapper">
            <div class="agent-header-row">
                <div class="agent-avatar-circle">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
                </div>
                <div>
                    <h3 style="font-family: 'Space Grotesk', sans-serif; margin: 0; font-size: 20px; font-weight: 700; color: var(--text-primary);">FinPilot Intelligence Copilot</h3>
                    <p style="margin: 0; font-size: 13.5px; color: var(--text-muted);">Ask natural language questions across your financial ledger</p>
                </div>
            </div>
        """)

        suggested_questions = [
            "Where did I spend the most this month?",
            "Which subscriptions am I paying for?",
            "What expenses increased compared with last month?",
            "Show me unusual spending",
            "What is my cash flow?"
        ]

        selected_q = st.selectbox(
            "Explore Suggested Prompts",
            ["Choose a prompt..."] + suggested_questions,
            key="agent_prompt_select"
        )

        default_input = "" if selected_q == "Choose a prompt..." else selected_q

        question = st.text_input(
            "Ask FinPilot Copilot",
            value=default_input,
            placeholder="Type your question about transactions, cash flow, or subscriptions...",
            key="agent_user_text"
        )

        if question:
            render_html(f"""
            <div style="display: flex; justify-content: flex-end; margin-top: 16px; margin-bottom: 14px;">
                <div style="background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); color: #FFF; padding: 12px 18px; border-radius: 14px 14px 2px 14px; font-size: 15px; max-width: 80%;">
                    {question}
                </div>
            </div>
            """)

            analysis_functions = {
                "get_category_spending": get_category_spending,
                "get_recurring_expenses": get_recurring_expenses,
                "get_monthly_comparison": get_monthly_comparison,
                "get_income": get_income,
                "get_expenses": get_expenses,
                "get_net_cash_flow": get_net_cash_flow,
                "detect_unusual_spending": detect_unusual_spending,
            }

            answer = answer_question(
                question,
                df,
                analysis_functions
            )

            render_html(f"""
            <div class="agent-bubble-bot">
                <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 14px; color: var(--primary-accent); margin-bottom: 8px;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
                    FinPilot Answer
                </div>
                <div>{answer}</div>
            </div>
            """)

        render_html('</div>')