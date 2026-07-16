"""
MietCheck – reife Multipage-App mit Bottom-Navigation
=====================================================
Seiten:  Check · Markt-Explorer · Modell & Qualität · Über
Navigation über eine fixierte Bottom-Bar (Query-Parameter).

Start:  streamlit run app.py
"""
import streamlit as st

from views import about, budget, check, explorer, insights
from views.common import LOGO_MARK, apply_plotly_theme, render_sidebar

st.set_page_config(page_title="MietCheck – Zahle ich zu viel Miete?",
                   page_icon="🏠", layout="centered",
                   initial_sidebar_state="expanded")
apply_plotly_theme()

PAGES = {
    "check":    ("🏠", "Check",   check.render),
    "explorer": ("🗺️", "Markt",   explorer.render),
    "budget":   ("🧮", "Budget",  budget.render),
    "insights": ("📈", "Modell",  insights.render),
    "about":    ("ℹ️", "Über",    about.render),
}

# --- Globales Styling (helles Theme) ----------------------------------------
st.markdown("""
<style>
  header[data-testid="stHeader"] { background: transparent; }
  [data-testid="stToolbar"] { display: none; }
  #MainMenu, footer { visibility: hidden; }
  [data-testid="stAppViewContainer"], .main { background: #f5f7fa; }
  /* Sidebar-Umschalter immer sichtbar & gut erkennbar */
  [data-testid="stSidebarCollapsedControl"] { display: flex !important; }
  [data-testid="stSidebarCollapsedControl"] button { color: #059669; }
  [data-testid="stSidebarCollapseButton"] { display: flex !important; }
  .block-container { padding-top: 1.2rem !important; padding-bottom: 6.5rem !important;
                     max-width: 760px; }

  /* Sidebar */
  [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e2e8f0; }
  .sb-h { font-size: 12px; letter-spacing: 1px; text-transform: uppercase;
          color: #0f172a; font-weight: 700; margin-bottom: 6px; }
  .sb-ok { font-size: 11.5px; color: #047857; background: #ecfdf5;
           border: 1px solid #6ee7b7; border-radius: 8px; padding: 7px 10px;
           margin-top: 8px; }
  .sb-warn { font-size: 11.5px; color: #b45309; background: #fffbeb;
             border: 1px solid #fcd34d; border-radius: 8px; padding: 7px 10px;
             margin-top: 8px; }
  .sb-info { display: flex; flex-direction: column; gap: 10px; margin-top: 8px; }
  .sb-info > div { background: #f8fafc; border: 1px solid #e2e8f0;
                   border-radius: 8px; padding: 9px 11px; font-size: 12px;
                   color: #0f172a; }
  .sb-info b { color: #059669; font-size: 15px; }
  .sb-info span { font-size: 10.5px; color: #64748b; }

  /* Standort-Leiste (Check) */
  .locbar { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px;
            padding: 9px 13px; font-size: 12.5px; color: #0f172a; margin-bottom: 4px;
            box-shadow: 0 1px 3px rgba(15,23,42,.05); }
  .locbar-x { font-size: 11px; color: #64748b; }

  /* Topbar (eigener Header) */
  .topbar { display:flex; align-items:center; justify-content:space-between;
            padding: 4px 2px 14px; }
  .brand { display:flex; align-items:center; gap:10px; }
  .brandtxt { font-weight:800; font-size:19px; color:#0f172a; line-height:1.05; }
  .brandtxt span { color:#059669; }
  .brand .tag { font-size:10.5px; color:#64748b; font-weight:500; letter-spacing:.4px;
                display:block; margin-top:1px; }
  .live { display:flex; align-items:center; gap:6px; font-size:11px; color:#64748b; }
  .dot { width:7px; height:7px; border-radius:50%; background:#10b981;
         animation:blink 2s ease-in-out infinite; }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

  /* Hero pro Seite */
  .hero { margin: 2px 0 18px; }
  .hero-t { font-size: 24px; font-weight: 800; color:#0f172a; line-height:1.15; }
  .hero-s { font-size: 13px; color:#64748b; margin-top:5px; }

  /* Sektionsüberschrift */
  .sec { display:flex; align-items:baseline; gap:10px; margin: 20px 0 10px;
         border-bottom:1px solid #e2e8f0; padding-bottom:7px; }
  .sec-t { font-size:12px; letter-spacing:1.2px; text-transform:uppercase;
           color:#0f172a; font-weight:700; }
  .sec-s { font-size:11px; color:#64748b; }

  /* KPI-Karten */
  .kpi { background:#ffffff; border:1px solid #e2e8f0; border-radius:12px;
         padding:14px 15px; height:100%; box-shadow: 0 1px 3px rgba(15,23,42,.05); }
  .kpi-l { font-size:11px; color:#64748b; letter-spacing:.4px; }
  .kpi-v { font-size:24px; font-weight:800; margin:4px 0 1px; }
  .kpi-s { font-size:11px; color:#94a3b8; }

  /* Urteil-Boxen */
  .verdict { border-radius:12px; padding:16px 18px; font-size:15px; margin-top:6px;
             border:1px solid; }
  .v-good { background:#ecfdf5; border-color:#6ee7b7; color:#047857; }
  .v-ok   { background:#fffbeb; border-color:#fcd34d; color:#b45309; }
  .v-bad  { background:#fef2f2; border-color:#fca5a5; color:#b91c1c; }

  /* dezente Hinweis-Boxen (Regionsvergleich) */
  .note { border-radius:10px; padding:11px 14px; font-size:13px; margin-top:4px;
          border:1px solid; }
  .n-good { background:#ecfdf5; border-color:#a7f3d0; color:#047857; }
  .n-ok   { background:#f8fafc; border-color:#e2e8f0; color:#334155; }
  .n-warn { background:#fffbeb; border-color:#fde68a; color:#b45309; }

  .divider { height:1px; background:#e2e8f0; margin:22px 0 6px; }

  /* QUA3CK-Steps */
  .steps { display:flex; flex-direction:column; gap:9px; }
  .step { display:flex; gap:12px; background:#ffffff; border:1px solid #e2e8f0;
          border-radius:10px; padding:11px 13px; align-items:center;
          box-shadow: 0 1px 3px rgba(15,23,42,.04); }
  .step-b { width:30px; height:30px; border-radius:8px; color:#ffffff;
            font-weight:800; display:flex; align-items:center; justify-content:center;
            flex-shrink:0; font-size:15px; }
  .step-t { font-size:13px; font-weight:700; color:#0f172a; }
  .step-d { font-size:11.5px; color:#64748b; margin-top:1px; }

  /* Bottom-Navigation */
  .bottom-nav { position:fixed; left:0; right:0; bottom:0; height:62px;
                background:#ffffff; border-top:1px solid #e2e8f0; z-index:1000;
                display:flex; justify-content:center;
                box-shadow:0 -2px 16px rgba(15,23,42,.08); }
  .bottom-nav .inner { display:flex; width:100%; max-width:760px; }
  .nav-item { flex:1; display:flex; flex-direction:column; align-items:center;
              justify-content:center; gap:2px; text-decoration:none;
              color:#64748b; font-size:10.5px; letter-spacing:.3px;
              border-top:2px solid transparent; transition:all .15s; }
  .nav-item .ico { font-size:19px; }
  .nav-item:hover { color:#0f172a; background:#f1f5f9; }
  .nav-item.active { color:#059669; border-top-color:#10b981; background:#f0fdf4; }
</style>
""", unsafe_allow_html=True)

# --- Aktive Seite bestimmen -------------------------------------------------
page = st.query_params.get("page", "check")
if page not in PAGES:
    page = "check"

# --- Globale Sidebar (Standort + Datenbasis) --------------------------------
loc = render_sidebar()

# --- Topbar -----------------------------------------------------------------
st.markdown(
    f"<div class='topbar'><div class='brand'>{LOGO_MARK}"
    "<div class='brandtxt'>Miet<span>Check</span>"
    "<span class='tag'>Faire Miete, datenbasiert</span></div></div>"
    "<div class='live'><span class='dot'></span>202.908 Angebote</div></div>",
    unsafe_allow_html=True)

# --- Seiteninhalt -----------------------------------------------------------
PAGES[page][2](loc)

# --- Bottom-Navigation ------------------------------------------------------
nav = "<div class='bottom-nav'><div class='inner'>"
for key, (ico, label, _) in PAGES.items():
    cls = "nav-item active" if key == page else "nav-item"
    nav += (f"<a class='{cls}' href='?page={key}' target='_self'>"
            f"<span class='ico'>{ico}</span>{label}</a>")
nav += "</div></div>"
st.markdown(nav, unsafe_allow_html=True)
