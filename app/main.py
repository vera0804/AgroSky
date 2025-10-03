from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from dotenv import load_dotenv
import os

# Routers
from app.routes.auth import router as auth_router
from app.routes.contact import router as contact_router
from app.routes.health import router as health_router
from app.routes.diag import router as diag_router  # /api/diag/*

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

app = FastAPI(title="AgroSky API + Front")

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://www.agroskycr.com,https://agroskycr.com"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Directorios ===
BACKEND_ROOT = Path(__file__).resolve().parent.parent   
FRONT_DIR = BACKEND_ROOT / "public"                     

# Montar /assets
if (FRONT_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=FRONT_DIR / "assets"), name="assets")

# Ruta raíz -> index.html
@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(FRONT_DIR / "index.html")

# ==== Diag directo en main (temporal) ====
import urllib.request, socket
from fastapi import HTTPException

@app.get("/api/diag/outbound-ip")
def diag_outbound_ip():
    try:
        with urllib.request.urlopen("https://ifconfig.me/ip", timeout=5) as r:
            ip = r.read().decode().strip()
        return {"ip": ip}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"no-ip: {e}")

@app.get("/api/diag/db-socket")
def diag_db_socket():
    host = os.getenv("DB_HOST", "195.35.61.61")
    port = int(os.getenv("DB_PORT", "3306"))
    try:
        s = socket.create_connection((host, port), 5)
        peer = s.getpeername()
        s.close()
        return {"ok": True, "peer": peer}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"tcp-fail: {e}")

from pymysql.err import OperationalError
from app.services.db import get_conn

@app.get("/api/diag/db-sql")
def diag_db_sql():
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
# =========================================

# --- Fallback SPA (AL FINAL) ---
# No capturar rutas del API ni docs/openapi
EXCLUDE_PREFIXES = ("api/", "docs", "openapi.json", "redoc")

# Fallback para otros archivos del front
@app.get("/{path:path}", include_in_schema=False)
def spa_fallback(path: str):
    # Si la ruta es de API o docs, dejar que FastAPI responda 404
    if path.startswith(EXCLUDE_PREFIXES):
        # devolver 404 explícito para que no sirva index.html por error
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not Found")

    candidate = FRONT_DIR / path
    if candidate.exists() and candidate.is_file():
        return FileResponse(candidate)

    # SPA: devuelve index.html para manejar rutas del front (e.g., /servicios)
    return FileResponse(FRONT_DIR / "index.html")

from app.routes import auth
# API
app.include_router(health_router)
app.include_router(auth.router)
app.include_router(contact_router, prefix="/api")
app.include_router(diag_router)

