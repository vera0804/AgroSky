import os, smtplib
from email.message import EmailMessage

def send_email_html(subject: str, html: str, reply_to: str | None = None):
    # Cargar variables cada vez que se envía un correo
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")
    SMTP_FROM = os.getenv("SMTP_FROM")
    SMTP_TO   = os.getenv("SMTP_TO", "agroskycr@gmail.com")

    if not all([SMTP_USER, SMTP_PASS, SMTP_FROM, SMTP_TO]):
        raise RuntimeError("Faltan variables SMTP (SMTP_USER/PASS/FROM/TO)")

    # Construcción del mensaje
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = SMTP_TO
    if reply_to:
        msg["Reply-To"] = reply_to

    msg.set_content("Tu cliente no soporta HTML.")
    msg.add_alternative(html, subtype="html")

    # Conexión y envío
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)

