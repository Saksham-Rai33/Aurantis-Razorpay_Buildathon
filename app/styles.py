CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #0f1117;
    --sidebar: #1a1d27;
    --card: #1e2130;
    --card-border: #2a2d3e;
    --primary: #6c63ff;
    --success: #00d46a;
    --warning: #ffa500;
    --danger: #ff4d4d;
    --text: #ffffff;
    --text-muted: #a0a3b1;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

#MainMenu, footer {
    visibility: hidden;
}

[data-testid="stToolbar"] [data-testid="stMainMenuButton"],
[data-testid="stToolbar"] [data-testid="stBaseButton-header"] {
    visibility: hidden;
}

[data-testid="stHeader"] {
    background-color: transparent;
}

/* ---------- base surfaces ---------- */
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
.stApp {
    background-color: var(--bg);
    color: var(--text);
}

[data-testid="stMain"] {
    background-color: var(--bg);
}

[data-testid="stSidebar"] {
    background-color: var(--sidebar);
    border-right: 1px solid var(--card-border);
}

[data-testid="stSidebar"] * {
    color: var(--text);
}

h1, h2, h3, h4, h5, h6, p, span, label, div {
    color: var(--text);
}

.stCaption, [data-testid="stCaptionContainer"], small {
    color: var(--text-muted) !important;
}

/* ---------- sidebar nav pills ---------- */
[data-testid="stSidebarNav"] {
    padding-top: 4px;
}

[data-testid="stSidebarNav"] ul {
    gap: 4px;
    display: flex;
    flex-direction: column;
}

[data-testid="stSidebarNav"] a,
[data-testid="stSidebarNavLink"] {
    border-radius: 10px !important;
    margin: 2px 0;
    padding: 10px 14px !important;
    font-weight: 600;
    font-size: 0.92rem;
    color: var(--text-muted) !important;
    background: transparent;
    transition: background 0.15s ease, color 0.15s ease;
}

[data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebarNavLink"]:hover {
    background: rgba(108, 99, 255, 0.12);
    color: var(--text) !important;
}

[data-testid="stSidebarNav"] a[aria-current="page"],
[data-testid="stSidebarNavLink"][aria-current="page"] {
    background: var(--primary) !important;
    color: #ffffff !important;
    box-shadow: 0 0 16px rgba(108, 99, 255, 0.45);
}

[data-testid="stSidebarNav"] a[aria-current="page"] span,
[data-testid="stSidebarNavLink"][aria-current="page"] span {
    color: #ffffff !important;
}

/* ---------- sidebar model status ---------- */
.sidebar-status {
    margin-top: 18px;
    padding: 14px 16px;
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: 12px;
}

.sidebar-status .status-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text-muted);
    margin-bottom: 6px;
}

.sidebar-status .status-row:last-child {
    margin-bottom: 0;
}

.sidebar-status .status-value {
    color: var(--success);
    font-weight: 700;
}

.sidebar-status .status-value.threshold {
    color: var(--primary);
}

/* ---------- inputs ---------- */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input {
    background-color: var(--card) !important;
    color: var(--text) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 10px !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 1px var(--primary) !important;
}

[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
    background-color: var(--card) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}

div[data-baseweb="popover"] li,
div[data-baseweb="menu"] li {
    background-color: var(--card) !important;
    color: var(--text) !important;
}

[data-testid="stSlider"] [data-baseweb="slider"] > div > div {
    background: var(--card-border) !important;
}

[data-testid="stSlider"] [role="slider"] {
    background-color: var(--primary) !important;
    border-color: var(--primary) !important;
}

[data-testid="stTickBar"] {
    color: var(--text-muted);
}

[data-testid="stWidgetLabel"] p {
    color: var(--text-muted) !important;
    font-weight: 600;
    font-size: 0.85rem;
}

[data-testid="stCheckbox"] label p {
    color: var(--text) !important;
}

/* ---------- buttons ---------- */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
    border-radius: 10px;
    font-weight: 600;
    border: 1px solid var(--card-border);
    background-color: var(--card);
    color: var(--text);
    transition: box-shadow 0.15s ease, transform 0.05s ease, border-color 0.15s ease;
}

.stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {
    border-color: var(--primary);
    color: var(--text);
}

.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
    background-color: var(--primary);
    border: none;
    color: #ffffff;
    box-shadow: 0 0 18px rgba(108, 99, 255, 0.4);
}

.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {
    background-color: #7d75ff;
    box-shadow: 0 0 24px rgba(108, 99, 255, 0.6);
}

.st-key-confirm_order_wrap .stButton > button[kind="primary"] {
    background-color: var(--success) !important;
    box-shadow: 0 0 18px rgba(0, 212, 106, 0.4) !important;
}

.st-key-confirm_order_wrap .stButton > button[kind="primary"]:hover {
    background-color: #10e57e !important;
    box-shadow: 0 0 24px rgba(0, 212, 106, 0.6) !important;
}

/* ---------- alerts ---------- */
[data-testid="stAlert"] {
    background-color: var(--card) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 12px !important;
}

[data-testid="stAlert"] p {
    color: var(--text) !important;
}

/* ---------- bordered containers -> dark cards ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card);
    border: 1px solid var(--card-border) !important;
    border-radius: 16px !important;
}

[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-radius: 16px !important;
}

.stVerticalBlockBorderWrapper, [data-testid="stVerticalBlockBorderWrapper"] {
    padding: 4px;
}

[data-testid="stExpander"] {
    background: var(--card);
    border: 1px solid var(--card-border) !important;
    border-radius: 12px !important;
}

/* ---------- Aurantis brand header ---------- */
.aurantis-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 4px 0 20px 0;
}

.aurantis-header img {
    width: 40px;
    height: 40px;
    border-radius: 10px;
}

.aurantis-header .brand-name {
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--primary);
    letter-spacing: -0.01em;
    line-height: 1.1;
}

.aurantis-header .brand-tagline {
    font-size: 0.82rem;
    color: var(--text-muted);
    margin-top: 2px;
}

/* sidebar logo block, rendered above the nav */
.sidebar-brand {
    padding: 6px 4px 18px 4px;
    border-bottom: 1px solid var(--card-border);
    margin-bottom: 12px;
}

.sidebar-brand .brand-name {
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--primary);
    letter-spacing: -0.01em;
    line-height: 1.15;
}

.sidebar-brand .brand-tagline {
    font-size: 0.76rem;
    color: var(--text-muted);
    margin-top: 4px;
    line-height: 1.3;
}

/* ---------- metric cards ---------- */
.metric-card-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}

.metric-card {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent-color, var(--primary));
    box-shadow: 0 0 12px var(--accent-color, var(--primary));
}

.metric-card.accent-purple { --accent-color: var(--primary); }
.metric-card.accent-red { --accent-color: var(--danger); }
.metric-card.accent-green { --accent-color: var(--success); }
.metric-card.accent-orange { --accent-color: var(--warning); }

.metric-card .metric-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.03em;
    margin-bottom: 8px;
}

.metric-card .metric-value {
    font-size: 1.95rem;
    font-weight: 800;
    color: var(--text);
    line-height: 1.15;
}

.metric-card .metric-delta {
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 8px;
    display: flex;
    align-items: center;
    gap: 4px;
}

.metric-delta.positive { color: var(--success); }
.metric-delta.negative { color: var(--danger); }
.metric-delta.neutral { color: var(--text-muted); }

/* ---------- section card wrapper (markup-based) ---------- */
.section-card {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: 16px;
    padding: 22px 24px;
    margin-bottom: 20px;
}

.section-card h3 {
    margin-top: 0;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text);
}

h3 {
    font-size: 1.05rem;
    font-weight: 700;
}

/* ---------- badges ---------- */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    white-space: nowrap;
}

.badge-green { background: rgba(0, 212, 106, 0.15); color: var(--success); }
.badge-yellow { background: rgba(255, 165, 0, 0.15); color: var(--warning); }
.badge-red { background: rgba(255, 77, 77, 0.15); color: var(--danger); }
.badge-grey { background: rgba(160, 163, 177, 0.15); color: var(--text-muted); }
.badge-blue { background: rgba(108, 99, 255, 0.18); color: var(--primary); }

/* ---------- order rows / table ---------- */
.order-row {
    padding: 12px 0;
    border-bottom: 1px solid var(--card-border);
}

.order-row:last-child {
    border-bottom: none;
}

.order-id {
    font-weight: 700;
    color: var(--text);
    font-size: 0.92rem;
}

.order-meta {
    font-size: 0.8rem;
    color: var(--text-muted);
}

.risk-score-text {
    font-weight: 700;
    font-size: 0.92rem;
}

.risk-green { color: var(--success); }
.risk-yellow { color: var(--warning); }
.risk-red { color: var(--danger); }

.table-header {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--card-border);
}

/* ---------- risk circle (New order results) ---------- */
.risk-circle-wrap {
    display: flex;
    justify-content: center;
    padding: 12px 0 4px 0;
}

.risk-circle {
    width: 176px;
    height: 176px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.risk-circle-inner {
    width: 138px;
    height: 138px;
    border-radius: 50%;
    background: var(--card);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.risk-circle-value {
    font-size: 2.1rem;
    font-weight: 800;
    color: var(--text);
    line-height: 1;
}

.risk-circle-label {
    font-size: 0.68rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 6px;
}

/* ---------- action box ---------- */
.action-box {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 14px 16px;
    border-radius: 12px;
    font-size: 0.88rem;
    font-weight: 600;
    margin: 10px 0 16px 0;
    border: 1px solid var(--card-border);
}

.action-box.tier-low { background: rgba(0, 212, 106, 0.10); color: var(--success); border-color: rgba(0, 212, 106, 0.3); }
.action-box.tier-medium { background: rgba(255, 165, 0, 0.10); color: var(--warning); border-color: rgba(255, 165, 0, 0.3); }
.action-box.tier-high { background: rgba(255, 77, 77, 0.10); color: var(--danger); border-color: rgba(255, 77, 77, 0.3); }

/* ---------- reason list ---------- */
.reason-list {
    list-style: none;
    padding: 0;
    margin: 8px 0 16px 0;
}

.reason-list li {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-size: 0.86rem;
    color: var(--text-muted);
    padding: 6px 0;
    border-bottom: 1px solid var(--card-border);
}

.reason-list li:last-child { border-bottom: none; }

.reason-list li .reason-icon { color: var(--warning); flex-shrink: 0; }

.placeholder-panel {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 60px 20px;
    color: var(--text-muted);
}

.placeholder-panel .placeholder-icon {
    font-size: 2.4rem;
    margin-bottom: 12px;
    opacity: 0.5;
}

/* ---------- delivery order cards ---------- */
.order-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 14px;
}

/* ---------- evidence vault stat cards ---------- */
.vault-stat-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}

.vault-stat-card {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 18px 20px;
    text-align: left;
}

.vault-stat-card .vault-stat-value {
    font-size: 1.7rem;
    font-weight: 800;
    color: var(--text);
}

.vault-stat-card .vault-stat-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.03em;
    margin-top: 4px;
}

/* ---------- tabs ---------- */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid var(--card-border);
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    color: var(--text-muted);
    font-weight: 600;
    background: transparent;
    border-radius: 10px 10px 0 0;
}

[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--text) !important;
    background: var(--card);
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background-color: var(--primary);
}

/* ---------- phone mockup (customer delivery screen) ---------- */
.st-key-phone_screen_card {
    max-width: 380px !important;
    margin: 4px auto !important;
    background: #000000 !important;
    border: 10px solid #050608 !important;
    border-radius: 42px !important;
    padding: 14px 16px 22px 16px !important;
    box-shadow: 0 25px 70px rgba(0, 0, 0, 0.55);
}

.phone-notch {
    width: 120px;
    height: 22px;
    background: #050608;
    border-radius: 0 0 16px 16px;
    margin: -14px auto 12px auto;
}

.phone-statusbar {
    display: flex;
    justify-content: space-between;
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--text-muted);
    padding: 0 4px 10px 4px;
}

.phone-app-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--card-border);
    margin-bottom: 14px;
}

.phone-app-header .avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: var(--primary);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    color: #ffffff;
    font-size: 0.9rem;
    flex-shrink: 0;
}

.phone-app-header .contact-name {
    font-weight: 700;
    font-size: 0.92rem;
    color: var(--text);
}

.phone-app-header .contact-sub {
    font-size: 0.72rem;
    color: var(--text-muted);
}

.msg-bubble {
    max-width: 88%;
    padding: 10px 14px;
    border-radius: 16px;
    border-bottom-left-radius: 4px;
    font-size: 0.83rem;
    line-height: 1.45;
    color: var(--text);
    background: var(--card);
    border: 1px solid var(--card-border);
    margin-bottom: 12px;
}

.msg-bubble a { color: var(--primary); word-break: break-all; }

.msg-bubble .msg-time {
    display: block;
    font-size: 0.62rem;
    color: var(--text-muted);
    margin-top: 6px;
}

.phone-section-label {
    margin: 6px 0 10px 0;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.st-key-phone_otp_input_wrap input {
    text-align: center !important;
    letter-spacing: 6px !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
}

/* ---------- key-targeted card accents ---------- */
.st-key-recent_orders_card,
.st-key-new_order_form_card,
.st-key-risk_assessment_card,
.st-key-delivery_queue_card,
.st-key-delivery_detail_card,
.st-key-evidence_vault_card {
    border-radius: 16px !important;
}
</style>
"""
