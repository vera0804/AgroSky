# app/services/auth_service.py
import bcrypt
from .db import get_conn

def login_user(usuario: str, password: str):
    # Llama al SP: opción 1 = login (lookup)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL sp_acceso(%s,%s,NULL)", (1, usuario))
            row = cur.fetchone()

    # Soporta ambas versiones del SP:
    if not row:
        return {"ok": False}
    if "found" in row and row["found"] == 0:
        return {"ok": False}

    hashed = row.get("password_hash")
    rol    = row.get("rol")

    if not hashed or not rol:
        return {"ok": False}

    # Verificar con bcrypt (hash debe empezar con $2...)
    try:
        ok = hashed.startswith("$2") and bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        ok = False

    return {"ok": ok, "rol": rol}
