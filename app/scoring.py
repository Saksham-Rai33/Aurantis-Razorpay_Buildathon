import math
import random

import pandas as pd

from src.features.engineer import FEATURE_COLS
from app.services import explain_order, get_risk_tier

PRODUCT_CATEGORY_LABELS = {
    "H": "H — Home & garden",
    "S": "S — Software/digital",
    "R": "R — Retail/general",
}
PRODUCT_CATEGORIES = list(PRODUCT_CATEGORY_LABELS)

# Matches src/data/labeling.py HIGH_RISK_PRODUCTS exactly — these are the
# IEEE-CIS ProductCD codes the original heuristic already flags as risky.
HIGH_RISK_CATEGORIES = {"H", "S", "R"}

CARD_TYPES = ["Visa", "Mastercard", "American Express", "Discover", "RuPay", "Diners Club"]

DISPOSABLE_EMAIL_DOMAINS = {
    "guerrillamail.com", "mailinator.com", "tempmail.com",
    "yopmail.com", "trashmail.com", "maildrop.cc",
}

MAX_RULE_ESCALATION = 0.85
ESCALATION_PER_FLAG = 0.15


def build_feature_vector(amount, pool):
    """Real model input: amount-driven fields set directly; opaque behavioral
    signals (C/D/V) sampled from a comparable historical order, since a live
    checkout form can't reproduce Vesta's proprietary velocity features."""
    seed_order = random.choice(pool)
    features = {col: seed_order[col] for col in FEATURE_COLS}
    features["TransactionAmt"] = float(amount)
    features["amt_log"] = math.log1p(amount)
    features["amt_is_high"] = 1.0 if amount >= 500 else 0.0
    features["card1_freq_log"] = math.log1p(1)
    features["addr1_freq_log"] = math.log1p(1)
    return features


def evaluate_rules(amount, category, email, billing_city, shipping_city, card_type, order_hour):
    flags = []

    billing = billing_city.strip().lower()
    shipping = shipping_city.strip().lower()
    if billing and shipping and billing != shipping:
        flags.append("Billing and shipping cities differ")

    domain = email.split("@")[-1].lower() if "@" in email else ""
    if domain in DISPOSABLE_EMAIL_DOMAINS:
        flags.append("Disposable email domain used")

    if category in HIGH_RISK_CATEGORIES:
        label = PRODUCT_CATEGORY_LABELS.get(category, category)
        flags.append(f"High-return-risk product category ({label})")

    if amount >= 500:
        flags.append(f"High order value (₹{amount:,.0f})")

    if amount > 0 and amount % 50 == 0:
        flags.append("Round transaction amount")

    if order_hour >= 20 or order_hour < 2:
        flags.append("Order placed late at night")

    if card_type == "Discover":
        flags.append("Discover card used")

    return flags


def score_new_order(model, pool, *, amount, category, email, billing_city,
                     shipping_city, card_type, order_hour):
    features = build_feature_vector(amount, pool)
    row = pd.DataFrame([features])[FEATURE_COLS]
    model_score = float(model.predict_proba(row)[:, 1][0])

    rule_flags = evaluate_rules(
        amount, category, email, billing_city, shipping_city, card_type, order_hour
    )
    escalation = min(MAX_RULE_ESCALATION, ESCALATION_PER_FLAG * len(rule_flags))
    final_score = min(1.0, model_score + escalation)

    shap_reasons = explain_order(model, features)["top_reasons"]
    top_reasons = (rule_flags + shap_reasons)[:3] if rule_flags else shap_reasons[:3]

    return {
        "features": features,
        "model_score": model_score,
        "rule_flags": rule_flags,
        "final_score": final_score,
        "tier": get_risk_tier(final_score),
        "top_reasons": top_reasons,
    }
