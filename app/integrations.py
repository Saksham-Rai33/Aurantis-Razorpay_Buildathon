import os

import requests
import streamlit as st

PLACEHOLDER = "PLACEHOLDER_API_KEY"


def _get_config(name, default=PLACEHOLDER):
    value = os.environ.get(name)
    if value:
        return value
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


MSG91_API_KEY = _get_config("MSG91_API_KEY")
MSG91_SENDER_ID = _get_config("MSG91_SENDER_ID", "AURANT")
MSG91_ROUTE = "4"

DOCUSIGN_API_KEY = _get_config("DOCUSIGN_API_KEY")
DOCUSIGN_ACCOUNT_ID = _get_config("DOCUSIGN_ACCOUNT_ID")
DOCUSIGN_BASE_URL = _get_config("DOCUSIGN_BASE_URL", "https://demo.docusign.net/restapi")


def is_msg91_configured():
    return bool(MSG91_API_KEY) and MSG91_API_KEY != PLACEHOLDER


def is_docusign_configured():
    return (
        bool(DOCUSIGN_API_KEY) and DOCUSIGN_API_KEY != PLACEHOLDER
        and bool(DOCUSIGN_ACCOUNT_ID) and DOCUSIGN_ACCOUNT_ID != PLACEHOLDER
    )


def send_sms_msg91(phone, message):
    """Send a real SMS via MSG91's HTTP API when MSG91_API_KEY is configured.
    Falls back to a clearly-labeled simulated result when it's still the
    placeholder, so the app never sends a request with a fake key."""
    if not is_msg91_configured():
        return {
            "success": False,
            "simulated": True,
            "detail": "MSG91_API_KEY not configured — simulated send.",
        }
    mobile = phone if phone.startswith("91") else f"91{phone}"
    try:
        response = requests.get(
            "https://api.msg91.com/api/sendhttp.php",
            params={
                "authkey": MSG91_API_KEY,
                "mobiles": mobile,
                "message": message,
                "sender": MSG91_SENDER_ID,
                "route": MSG91_ROUTE,
                "country": "91",
            },
            timeout=10,
        )
        response.raise_for_status()
        return {"success": True, "simulated": False, "detail": response.text}
    except Exception as exc:
        return {"success": False, "simulated": False, "detail": f"MSG91 request failed: {exc}"}


def create_envelope_docusign(signer_name, signer_email, order_id):
    """Create a real DocuSign envelope when DocuSign credentials are
    configured. Falls back to a simulated envelope link otherwise."""
    if not is_docusign_configured():
        return {
            "success": False,
            "simulated": True,
            "detail": "DocuSign credentials not configured — simulated e-sign link.",
            "link": None,
        }
    try:
        response = requests.post(
            f"{DOCUSIGN_BASE_URL}/v2.1/accounts/{DOCUSIGN_ACCOUNT_ID}/envelopes",
            headers={
                "Authorization": f"Bearer {DOCUSIGN_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "emailSubject": f"Aurantis delivery confirmation — order #{order_id}",
                "status": "sent",
                "recipients": {
                    "signers": [{"email": signer_email, "name": signer_name, "recipientId": "1"}]
                },
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return {"success": True, "simulated": False, "detail": "Envelope created", "link": data.get("uri")}
    except Exception as exc:
        return {"success": False, "simulated": False, "detail": f"DocuSign request failed: {exc}", "link": None}
