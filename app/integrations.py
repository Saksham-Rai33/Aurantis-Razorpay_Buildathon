import os

from dotenv import load_dotenv

load_dotenv()

PLACEHOLDER = "placeholder"


def _get_config(name, default=""):
    return os.environ.get(name, default)


TWILIO_ACCOUNT_SID = _get_config("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = _get_config("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = _get_config("TWILIO_PHONE_NUMBER")
CUSTOMER_PHONE = _get_config("CUSTOMER_PHONE")

DOCUSIGN_API_KEY = _get_config("DOCUSIGN_API_KEY")


def is_twilio_configured():
    return bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER and CUSTOMER_PHONE)


def is_docusign_configured():
    return bool(DOCUSIGN_API_KEY) and DOCUSIGN_API_KEY.lower() != PLACEHOLDER


def send_sms_twilio(message):
    """Send a real SMS via Twilio to CUSTOMER_PHONE when credentials are
    configured. Falls back to a clearly-labeled simulated result otherwise,
    so the app never fires a request with missing/fake credentials."""
    if not is_twilio_configured():
        return {
            "success": False,
            "simulated": True,
            "detail": "Twilio credentials not configured — simulated send.",
        }
    try:
        from twilio.rest import Client

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        msg = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=CUSTOMER_PHONE,
        )
        return {"success": True, "simulated": False, "detail": f"Twilio SID {msg.sid}"}
    except Exception as exc:
        return {"success": False, "simulated": False, "detail": f"Twilio request failed: {exc}"}
