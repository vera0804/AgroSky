# app/routes/auth.py
from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse
from app.services.auth_service import login_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    res = login_user(username, password)
    if not res["ok"]:
        return RedirectResponse(url="/login.html?error=1", status_code=303)

    rol = res["rol"]
    if rol == "Administrador":
        return RedirectResponse(url="/dashboard_admin.html", status_code=303)
    elif rol == "Piloto":
        return RedirectResponse(url="/dashboard_piloto.html", status_code=303)
    else:  # 'Levantamientos'
        return RedirectResponse(url="/dashboard_levantamiento.html", status_code=303)
