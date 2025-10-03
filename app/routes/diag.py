# app/routes/diag.py
from fastapi import APIRouter, HTTPException
import os, socket

# Para pedir la IP pública sin instalar librerías extra
import urllib.request

from pymysql.err import OperationalError
from app.services.db import get_conn  # tu helper actual

router = APIRouter(prefix="/api/diag", tags=["diag"])

@router.get("/outbound-ip")
def outbound_ip():
    """Devuelve la IP pública de salida del contenedor en Render."""
    try:
        with urllib.request.urlopen("https://ifconfig.me/ip", timeout=5) as r:
            ip = r.read().decode().strip()
        return {"ip": ip}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"no-ip: {e}")

@router.get("/db-socket")
def db_socket():
    """Prueba de socket TCP contra tu MySQL (sin credenciales)."""
    host = os.getenv("DB_HOST", "195.35.61.61")
    port = int(os.getenv("DB_PORT", "3306"))
    try:
        s = socket.create_connection((host, port), 5)
        peer = s.getpeername()
        s.close()
        return {"ok": True, "peer": peer}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"tcp-fail: {e}")

@router.get("/db-sql")
def db_sql():
    """SELECT 1 contra la BD (requiere que /db-socket ya pase)."""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                one = cur.fetchone()
        return {"ok": True, "select1": one}
    except OperationalError as e:
        raise HTTPException(status_code=503, detail=f"db-unreachable: {repr(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"db-error: {repr(e)}")
