import os, requests

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

        # solo agrega reply_to si es válido
        if reply_to and "@" in reply_to:
            payload["reply_to"] = reply_to

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
            raise RuntimeError(f"Resend error {resp.status_code}: {resp.text}")
        return True
