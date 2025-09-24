from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import os

from app.routes.contact import router as contact_router
from app.routes.health import router as health_router

app = FastAPI(title="AgroSky API + Front")

# CORS (si todo corre en el mismo dominio, puedes relajar esto)
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

# ====== Servir FRONTEND desde la raíz del repo ======
# main.py está en .../agrosky-backend/app/main.py
REPO_ROOT = Path(__file__).resolve().parents[3]  # sube 3 niveles hasta la raíz del repo

# Monta assets/ y (si lo necesitas) forms/ como estáticos
app.mount("/assets", StaticFiles(directory=REPO_ROOT / "assets"), name="assets")

# Ruta / -> index.html
@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(REPO_ROOT / "index.html")

# (opcional) fallback para otras rutas de front
@app.get("/{path:path}", include_in_schema=False)
def spa_fallback(path: str):
    # si piden /algo y no es API ni estático, sirve index.html
    candidate = REPO_ROOT / path
    if candidate.exists() and candidate.is_file():
        return FileResponse(candidate)
    return FileResponse(REPO_ROOT / "index.html")

# ====== API ======
app.include_router(health_router)              # /healthz /ping
app.include_router(contact_router, prefix="/api")  # /api/contact

