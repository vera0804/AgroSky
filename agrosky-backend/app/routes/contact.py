from fastapi import APIRouter, Form, HTTPException
from jinja2 import Template
from pathlib import Path
from app.services.emailer import send_email_html

router = APIRouter(tags=["contact"])

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "contact_email.html"
TEMPLATE = Template(TEMPLATE_PATH.read_text(encoding="utf-8"))

@router.post("/contact")
async def contact(
    name: str = Form(...),
    email: str | None = Form(None),
    phone: str = Form(...),
    message: str = Form(...),
):
    if len(name.strip()) < 2:
        raise HTTPException(400, "Nombre inválido")
    if len(phone.strip()) < 6:
        raise HTTPException(400, "Teléfono inválido")

    html = TEMPLATE.render(
        name=name.strip(),
        email=(email or "").strip() or "—",
        phone=phone.strip(),
        message=message.strip()
    )

    try:
        send_email_html(subject=f"Contacto AgroSky: {name} - {phone}", html=html, reply_to=email)
    except Exception as e:
        raise HTTPException(500, f"No se pudo enviar el correo: {e}")

    return {"ok": True, "message": "Mensaje enviado"}
