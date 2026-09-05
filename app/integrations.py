import os

from dotenv import load_dotenv

load_dotenv()

PLACEHOLDER = "placeholder"


def _get_config(name, default=""):
    return os.environ.get(name, default)


TWILIO_ACCOUNT_SID = _get_config("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = _get_config("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = _get_config("TWILIO_PHONE_NUMBER")
TWILIO_VERIFY_SERVICE_SID = _get_config("TWILIO_VERIFY_SERVICE_SID")
CUSTOMER_PHONE = _get_config("CUSTOMER_PHONE")

DOCUSIGN_INTEGRATION_KEY = _get_config("DOCUSIGN_INTEGRATION_KEY")
DOCUSIGN_USER_ID = _get_config("DOCUSIGN_USER_ID")
DOCUSIGN_ACCOUNT_ID = _get_config("DOCUSIGN_ACCOUNT_ID")
DOCUSIGN_PRIVATE_KEY_PATH = _get_config("DOCUSIGN_PRIVATE_KEY_PATH")
# hosted environments can't ship a local .pem file — allow the raw PEM text
# itself to be passed as a secret instead of a path
DOCUSIGN_PRIVATE_KEY = _get_config("DOCUSIGN_PRIVATE_KEY")
DOCUSIGN_AUTH_SERVER = _get_config("DOCUSIGN_AUTH_SERVER", "account-d.docusign.com")


def _read_docusign_private_key():
    if DOCUSIGN_PRIVATE_KEY:
        return DOCUSIGN_PRIVATE_KEY.encode("utf-8")
    with open(DOCUSIGN_PRIVATE_KEY_PATH, "rb") as key_file:
        return key_file.read()


def is_twilio_configured():
    return bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER and CUSTOMER_PHONE)


def is_verify_configured():
    return bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_VERIFY_SERVICE_SID and CUSTOMER_PHONE)


def is_docusign_configured():
    has_key = DOCUSIGN_PRIVATE_KEY or (DOCUSIGN_PRIVATE_KEY_PATH and os.path.exists(DOCUSIGN_PRIVATE_KEY_PATH))
    return bool(DOCUSIGN_INTEGRATION_KEY and DOCUSIGN_USER_ID and DOCUSIGN_ACCOUNT_ID and has_key)


def _get_docusign_api_client():
    """Authenticate via JWT grant and return an ApiClient whose host is set
    to the correct account base URI (sandbox base URIs vary by account)."""
    from docusign_esign import ApiClient

    private_key_bytes = _read_docusign_private_key()

    api_client = ApiClient()
    api_client.set_base_path(f"https://{DOCUSIGN_AUTH_SERVER}")
    token_response = api_client.request_jwt_user_token(
        client_id=DOCUSIGN_INTEGRATION_KEY,
        user_id=DOCUSIGN_USER_ID,
        oauth_host_name=DOCUSIGN_AUTH_SERVER,
        private_key_bytes=private_key_bytes,
        expires_in=3600,
        scopes=("signature", "impersonation"),
    )
    access_token = token_response.access_token

    user_info = api_client.get_user_info(access_token)
    account = next(a for a in user_info.accounts if a.account_id == DOCUSIGN_ACCOUNT_ID)

    api_client.host = f"{account.base_uri}/restapi"
    api_client.set_default_header("Authorization", f"Bearer {access_token}")
    return api_client


def create_envelope_docusign(signer_name, signer_email, order_id):
    """Create and send a real DocuSign envelope for delivery confirmation.
    DocuSign emails the signing link directly to signer_email. Falls back to
    a clearly-labeled simulated result when not configured or no valid
    recipient email is available."""
    if not is_docusign_configured():
        return {
            "success": False,
            "simulated": True,
            "detail": "DocuSign not configured — simulated e-sign.",
            "envelope_id": None,
        }
    if not signer_email or "@" not in signer_email:
        return {
            "success": False,
            "simulated": True,
            "detail": "No customer email on file — simulated e-sign.",
            "envelope_id": None,
        }
    try:
        import base64

        from docusign_esign import Document, EnvelopeDefinition, EnvelopesApi, Recipients, SignHere, Signer, Tabs

        doc_text = (
            "AURANTIS — DELIVERY CONFIRMATION\n\n"
            f"Order #{order_id}\n"
            f"Signer: {signer_name}\n\n"
            "By signing below, you confirm receipt of this delivery.\n\n"
            "Signature: /sig1/\n"
        )
        document = Document(
            document_base64=base64.b64encode(doc_text.encode("utf-8")).decode("ascii"),
            name="Delivery Confirmation",
            file_extension="txt",
            document_id="1",
        )
        sign_here = SignHere(anchor_string="/sig1/", anchor_units="pixels", anchor_x_offset="10", anchor_y_offset="-10")
        signer = Signer(
            email=signer_email,
            name=signer_name,
            recipient_id="1",
            routing_order="1",
            tabs=Tabs(sign_here_tabs=[sign_here]),
        )
        envelope_definition = EnvelopeDefinition(
            email_subject=f"Aurantis — please sign delivery confirmation for order #{order_id}",
            documents=[document],
            recipients=Recipients(signers=[signer]),
            status="sent",
        )

        api_client = _get_docusign_api_client()
        envelopes_api = EnvelopesApi(api_client)
        results = envelopes_api.create_envelope(DOCUSIGN_ACCOUNT_ID, envelope_definition=envelope_definition)

        return {
            "success": True,
            "simulated": False,
            "detail": f"Envelope {results.envelope_id} sent to {signer_email}",
            "envelope_id": results.envelope_id,
        }
    except Exception as exc:
        return {"success": False, "simulated": False, "detail": f"DocuSign request failed: {exc}", "envelope_id": None}


def start_otp_verification():
    """Ask Twilio Verify to generate and send a real OTP via SMS to
    CUSTOMER_PHONE. Twilio holds the code — we never see it, by design.
    Falls back to a clearly-labeled simulated result when not configured."""
    if not is_verify_configured():
        return {
            "success": False,
            "simulated": True,
            "detail": "Twilio Verify not configured — simulated OTP.",
        }
    try:
        from twilio.rest import Client

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        verification = client.verify.v2.services(TWILIO_VERIFY_SERVICE_SID).verifications.create(
            to=CUSTOMER_PHONE, channel="sms"
        )
        return {
            "success": True,
            "simulated": False,
            "detail": f"Twilio Verify status: {verification.status}",
        }
    except Exception as exc:
        return {"success": False, "simulated": False, "detail": f"Twilio Verify request failed: {exc}"}


def check_otp_verification(code):
    """Ask Twilio Verify whether `code` matches what it sent to
    CUSTOMER_PHONE. Returns success True only on an "approved" check."""
    if not is_verify_configured():
        return {"success": False, "simulated": True, "detail": "Twilio Verify not configured."}
    try:
        from twilio.rest import Client

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        check = client.verify.v2.services(TWILIO_VERIFY_SERVICE_SID).verification_checks.create(
            to=CUSTOMER_PHONE, code=code
        )
        return {
            "success": check.status == "approved",
            "simulated": False,
            "detail": f"Twilio Verify check status: {check.status}",
        }
    except Exception as exc:
        return {"success": False, "simulated": False, "detail": f"Twilio Verify check failed: {exc}"}


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
