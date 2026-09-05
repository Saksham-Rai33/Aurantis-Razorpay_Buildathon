# Aurantis — AI-Powered Return Risk Protection

> **Razorpay AI Buildathon 2026 — Track 2: AI Risk Manager**
> Scores every order for return-abuse risk at checkout, then verifies delivery with real OTP + e-signature — so merchants stop the loss before it happens, and have proof when it doesn't.

**Live app:** https://aurantis-return-risk.streamlit.app/

## The problem

Return abuse costs Indian e-commerce merchants thousands of crores a year. Unlike card fraud, the transaction itself looks completely legitimate — the abuse happens *after* the sale, when the order is refused, swapped, or falsely disputed at the doorstep. Merchants have no real-time signal at checkout telling them "this order is likely to become a loss," and no tamper-proof record when a delivery *is* disputed.

## The solution — score, act, prove

1. **Score** — every order is scored 0–1 for return risk by a LightGBM model at checkout.
2. **Act** — the score routes the order down a risk-appropriate path: low risk ships as-is, medium risk requires an OTP + DocuSign e-signature at delivery, high risk adds a manual review on top.
3. **Prove** — every completed delivery lands in a tamper-proof Evidence Vault with its risk score, SHAP explanation, OTP verification timestamp, and signature — real evidence for chargeback/dispute defense.

The OTP and e-signature steps are **real, working integrations** (Twilio Verify, DocuSign), not simulated mockups — verified live end-to-end during development.

## The app

Four pages, built as a dark-themed Streamlit SaaS dashboard:

| Page | What it does |
|---|---|
| **Dashboard** | Live metrics (orders, high-risk count, delivered, money saved) + a risk-distribution chart + recent orders table |
| **New order** | Score a fresh transaction — amount, category, email, city, card, hour — and see the risk score, tier, top SHAP reasons, and recommended action |
| **Delivery** | Merchant queue of pending orders + a phone-mockup view of exactly what the customer sees (real OTP SMS, real DocuSign link) |
| **Evidence vault** | Every delivered order's proof: OTP verified, signature status, risk score, timestamp — downloadable per-order or as a full CSV report |

## The model

Trained on the IEEE-CIS Fraud Detection dataset (Kaggle, 590,540 transactions), with synthetic return-risk labels generated via a domain-driven heuristic (`src/data/labeling.py`) — 5.89% positive rate.

Evaluated on a held-out test set of 118,108 transactions never seen during training:

| Metric | Score |
|--------|-------|
| ROC-AUC | 0.9837 |
| PR-AUC | 0.7291 |
| Precision | 0.5046 |
| Recall | 0.9954 |
| F1 | 0.6697 |
| Optimal threshold | 0.95 |
| Flag rate at optimal threshold | 6.92% |

The threshold isn't arbitrary — it minimizes total business cost across a cost curve (`src/evaluation/cost_curve.py`) that prices a false positive (blocking a legitimate customer) at ₹800 and a false negative (missing an abuser) at ₹600. Every score also ships with a SHAP explanation (`src/evaluation/explain.py`) so the "why" is never a black box.

## Real integrations, not mockups

- **OTP** — Twilio Verify generates and validates the delivery OTP over real SMS. (Plain Twilio SMS was tried first but blocked by trial-account template restrictions on dynamic content — Verify is Twilio's purpose-built OTP product and isn't subject to that limit.)
- **E-signature** — DocuSign creates and sends a real signing envelope via JWT grant auth, with the customer receiving an actual email and completing a live DocuSign signing session.

Both integrations gracefully fall back to a clearly-labeled simulated mode when credentials aren't configured (e.g. on a fresh clone with no secrets set).

## Tech stack

LightGBM · scikit-learn · imbalanced-learn (SMOTE) · SHAP · Streamlit · Plotly · Twilio (Verify) · DocuSign eSignature SDK · pandas / numpy

## Repo structure

```
src/
  data/          raw data loading + return-risk labeling heuristic
  features/      feature engineering + preprocessing (train/test split, SMOTE)
  models/        LightGBM training
  evaluation/    business cost curve, SHAP explainability
app/
  streamlit_app.py    entry point — sidebar nav, theme, session state
  app_pages/          Dashboard, New order, Delivery, Evidence vault
  scoring.py          rule-based risk escalation on top of the model score
  services.py         risk tiers, OTP/e-sign state helpers
  integrations.py     real Twilio Verify + DocuSign clients
  data_gen.py         demo order generation (falls back to a cached
                      snapshot when the raw dataset isn't present)
  styles.py           dark theme CSS
results/         trained model, metrics, cost curve + SHAP plots
tests/           model unit tests
```

## Running locally

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

To enable the real Twilio/DocuSign integrations, create a `.env` in the project root:

```env
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
TWILIO_VERIFY_SERVICE_SID=
CUSTOMER_PHONE=

DOCUSIGN_INTEGRATION_KEY=
DOCUSIGN_USER_ID=
DOCUSIGN_ACCOUNT_ID=
DOCUSIGN_PRIVATE_KEY_PATH=.docusign_private_key.pem
DOCUSIGN_AUTH_SERVER=account-d.docusign.com
```

Without a `.env`, the app runs fully functional in simulated mode.

## Deploying (Streamlit Community Cloud)

The app is deployed straight from this repo — main file `app/streamlit_app.py`, branch `main`. Two things make that possible without shipping the ~700MB raw Kaggle dataset:

- `results/model.pkl` (1.7MB) is committed directly.
- `app/demo_orders_cache.json` is a pre-scored snapshot of the 50 demo orders; `app/data_gen.py` falls back to it whenever `data/raw/` isn't present.

Secrets (same keys as `.env` above, plus `DOCUSIGN_PRIVATE_KEY` as the raw PEM text instead of a file path, since a hosted app has no local `.pem` file) are set via the Cloud dashboard's **Secrets** panel, not committed.

## Challenges along the way

- **Data leakage** — an early model scored suspiciously close to perfect. It turned out the fraud label was partly generated from product-category flags that were *also* still in the feature table — the model was reading its own answer key. Fixed by stripping every feature that overlapped with the label-generation heuristic and retraining on signals genuinely available at checkout.
- **Twilio trial restrictions** — plain SMS blocked dynamic OTP content on a trial account; solved by moving OTP delivery to Twilio Verify.
- **DocuSign consent** — JWT auth failed with `consent_required` until the one-time OAuth consent grant was completed (redirect URI registration + a single authorization).
- **Cloud deployment size** — the raw dataset couldn't ship to a hosted environment; solved with the cached demo-orders snapshot described above.

## Author

Saksham Rai | UPES
Razorpay AI Buildathon 2026 — Track 2: AI Risk Manager
