import os, requests
from email.message import EmailMessage  # lo puedes dejar si también tienes SMTP opcional

EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "resend").lower()

if EMAIL_PROVIDER == "resend":
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")
    EMAIL_FROM     = os.getenv("EMAIL_FROM")             # e.g. "AgroSky <onboarding@resend.dev>"
    EMAIL_TO       = os.getenv("EMAIL_TO", "agroskycr@gmail.com")

    def send_email_html(subject: str, html: str, reply_to: str | None = None):
        if not all([RESEND_API_KEY, EMAIL_FROM, EMAIL_TO]):
            raise RuntimeError("Faltan variables (RESEND_API_KEY/EMAIL_FROM/EMAIL_TO)")

        payload = {
            "from": EMAIL_FROM,
            "to": [EMAIL_TO],
            "subject": subject,
            "html": html
        }
        if reply_to:
            payload["reply_to"] = reply_to   # puede ser string o lista

        resp = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=15
        )
        if resp.status_code >= 400:
            # ← muestra el mensaje específico de Resend (te dirá si es “from domain not verified”, etc.)
            raise RuntimeError(f"Resend error {resp.status_code}: {resp.text}")
        return True
