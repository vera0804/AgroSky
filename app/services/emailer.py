# app/services/emailer.py
import os
import smtplib
from email.message import EmailMessage
import requests  # <-- API HTTP

PROVIDER = os.getenv("EMAIL_PROVIDER", "resend").lower()

# SMTP (fallback local)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

# Emails (compartidos)
EMAIL_FROM = os.getenv("EMAIL_FROM")              # p.ej. onboarding@resend.dev (pruebas) o notificaciones@agroskycr.com (ya con dominio verificado)
EMAIL_TO   = os.getenv("EMAIL_TO", "agroskycr@gmail.com")

# Resend
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

def send_email_html(subject: str, html: str, reply_to: str | None = None):
    if PROVIDER == "resend":
        if not all([RESEND_API_KEY, EMAIL_FROM, EMAIL_TO]):
            raise RuntimeError("Faltan RESEND_API_KEY/EMAIL_FROM/EMAIL_TO")

        payload = {
            "from": EMAIL_FROM,
            "to": [EMAIL_TO],
            "subject": subject,
            "html": html,
        }
        if reply_to:
            payload["reply_to"] = reply_to

        r = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=15,
        )
        r.raise_for_status()
        return

    # ---- SMTP fallback (local) ----
    if not all([SMTP_USER, SMTP_PASS, EMAIL_FROM, EMAIL_TO]):
        raise RuntimeError("Faltan variables SMTP o EMAIL_FROM/EMAIL_TO")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content("Tu cliente no soporta HTML.")
    msg.add_alternative(html, subtype="html")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)


