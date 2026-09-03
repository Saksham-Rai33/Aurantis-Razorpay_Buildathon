CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

#MainMenu, footer {
    visibility: hidden;
}

/* Hide only the Deploy button and hamburger menu — keep the sidebar
   expand/collapse arrow (which also lives in the toolbar) visible. */
[data-testid="stToolbar"] [data-testid="stMainMenuButton"],
[data-testid="stToolbar"] [data-testid="stBaseButton-header"] {
    visibility: hidden;
}

[data-testid="stAppViewContainer"] {
    background-color: #FAFBFC;
}

[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E8EAED;
}

[data-testid="stSidebarNav"] a, [data-testid="stSidebarNav"] span {
    font-weight: 500;
    font-size: 0.92rem;
}

/* Buttons */
.stButton > button, .stFormSubmitButton > button {
    border-radius: 10px;
    font-weight: 600;
    border: 1px solid #E8EAED;
    transition: box-shadow 0.15s ease, transform 0.05s ease;
}

.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
    background-color: #1a73e8;
    border: none;
    box-shadow: 0 1px 2px rgba(26, 115, 232, 0.35);
}

.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {
    background-color: #1557b0;
    box-shadow: 0 2px 6px rgba(26, 115, 232, 0.45);
}

/* Aurantis brand header */
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
    font-size: 1.5rem;
    font-weight: 800;
    color: #202124;
    letter-spacing: -0.01em;
    line-height: 1.1;
}

.aurantis-header .brand-tagline {
    font-size: 0.82rem;
    color: #5F6368;
    margin-top: 2px;
}

/* Metric cards */
.metric-card-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}

.metric-card {
    background: #FFFFFF;
    border: 1px solid #E8EAED;
    border-radius: 14px;
    padding: 20px 22px;
    box-shadow: 0 1px 3px rgba(60, 64, 67, 0.08);
}

.metric-card .metric-label {
    font-size: 0.82rem;
    font-weight: 600;
    color: #5F6368;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    margin-bottom: 8px;
}

.metric-card .metric-value {
    font-size: 1.85rem;
    font-weight: 700;
    color: #202124;
    line-height: 1.15;
}

.metric-card .metric-delta {
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 6px;
}

.metric-delta.positive { color: #137333; }
.metric-delta.negative { color: #C5221F; }
.metric-delta.neutral { color: #5F6368; }

/* Section card wrapper */
.section-card {
    background: #FFFFFF;
    border: 1px solid #E8EAED;
    border-radius: 14px;
    padding: 22px 24px;
    box-shadow: 0 1px 3px rgba(60, 64, 67, 0.06);
    margin-bottom: 20px;
}

.section-card h3 {
    margin-top: 0;
    font-size: 1.05rem;
    font-weight: 700;
    color: #202124;
}

/* Risk badges */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.01em;
    white-space: nowrap;
}

.badge-green { background: #E6F4EA; color: #137333; }
.badge-yellow { background: #FEF7E0; color: #B06000; }
.badge-red { background: #FCE8E6; color: #C5221F; }
.badge-grey { background: #F1F3F4; color: #5F6368; }
.badge-blue { background: #E8F0FE; color: #1a73e8; }

/* Order row */
.order-row {
    padding: 12px 0;
    border-bottom: 1px solid #F1F3F4;
}

.order-row:last-child {
    border-bottom: none;
}

.order-id {
    font-weight: 600;
    color: #202124;
    font-size: 0.92rem;
}

.order-meta {
    font-size: 0.8rem;
    color: #5F6368;
}

.risk-score-text {
    font-weight: 700;
    font-size: 0.92rem;
}

.risk-green { color: #137333; }
.risk-yellow { color: #B06000; }
.risk-red { color: #C5221F; }

.st-key-recent_orders_card,
.st-key-new_order_form_card,
.st-key-risk_assessment_card {
    box-shadow: 0 1px 3px rgba(60, 64, 67, 0.08);
    border-radius: 14px !important;
}

.table-header {
    font-size: 0.75rem;
    font-weight: 700;
    color: #5F6368;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding-bottom: 10px;
    border-bottom: 2px solid #E8EAED;
}
</style>
"""
