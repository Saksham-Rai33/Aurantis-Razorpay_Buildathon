import random
from datetime import datetime, timezone

LOW_MAX = 0.3
MEDIUM_MAX = 0.6

TIER_BADGE_CLASS = {"low": "badge-green", "medium": "badge-yellow", "high": "badge-red"}
TIER_SCORE_CLASS = {"low": "risk-green", "medium": "risk-yellow", "high": "risk-red"}

RECOMMENDED_ACTION_TEXT = {
    "low": "Send OTP via Twilio to confirm delivery.",
    "medium": "Send OTP via Twilio and a DocuSign e-signature link.",
    "high": "Flag for manual review, then require OTP and a DocuSign e-signature.",
}


def recommended_action_text(tier):
    return RECOMMENDED_ACTION_TEXT[tier]


def _now():
    return datetime.now(timezone.utc).isoformat()


def get_risk_tier(score):
    if score < LOW_MAX:
        return "low"
    if score < MEDIUM_MAX:
        return "medium"
    return "high"


def required_actions(tier):
    if tier == "low":
        return ["otp"]
    if tier == "medium":
        return ["otp", "esign"]
    return ["manual_review", "otp", "esign"]


def simulate_send_otp(order):
    code = f"{random.randint(0, 999999):06d}"
    order["otp_code"] = code
    order["otp_sent_at"] = _now()
    order["otp_verified"] = False
    order["otp_verified_at"] = None
    return code


def verify_otp(order, entered_code):
    if order.get("otp_code") is not None and entered_code == order["otp_code"]:
        order["otp_verified"] = True
        order["otp_verified_at"] = _now()
        return True
    return False


def simulate_send_esign(order):
    token = f"docusign-sim-{random.randint(100000, 999999)}"
    order["esign_sent_at"] = _now()
    order["esign_signed"] = False
    order["esign_signer"] = None
    order["esign_signed_at"] = None
    return f"https://demo.docusign.net/sign/{token}"


def sign_esign(order, signer_name):
    order["esign_signed"] = True
    order["esign_signer"] = signer_name
    order["esign_signed_at"] = _now()


def is_ready_for_delivery(order):
    tier = get_risk_tier(order["risk_score"])
    actions = required_actions(tier)
    if "otp" in actions and not order.get("otp_verified"):
        return False
    if "esign" in actions and not order.get("esign_signed"):
        return False
    return True


def mark_delivered(order):
    if not is_ready_for_delivery(order):
        raise ValueError("order not ready for delivery — required actions incomplete")
    order["delivered"] = True
    order["delivered_at"] = _now()


def explain_order(model, order):
    from src.evaluation.explain import explain_single_order
    return explain_single_order(model, order)


if __name__ == "__main__":
    sample = {"risk_score": 0.72, "otp_code": None, "otp_verified": False,
              "esign_signed": False, "delivered": False}
    tier = get_risk_tier(sample["risk_score"])
    print("tier:", tier, "actions:", required_actions(tier))

    code = simulate_send_otp(sample)
    print("otp sent:", code)
    print("wrong verify:", verify_otp(sample, "000000"))
    print("right verify:", verify_otp(sample, code))

    link = simulate_send_esign(sample)
    print("esign link:", link)
    sign_esign(sample, "Vihaan Sharma")
    print("ready:", is_ready_for_delivery(sample))
    mark_delivered(sample)
    print("delivered:", sample["delivered"], sample["delivered_at"])
