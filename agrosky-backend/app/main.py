from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
import os

from app.routes.contact import router as contact_router
from app.routes.health import router as health_router


app = FastAPI(title="AgroSky API + Front")

# CORS (si todo corre en el mismo dominio puedes dejarlo así)
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
# Subimos 2 niveles para llegar a .../AgroSky
REPO_ROOT = Path(__file__).resolve().parents[2]

# Montar /assets (carpeta existe en la raíz del repo)
app.mount("/assets", StaticFiles(directory=REPO_ROOT / "assets"), name="assets")

# Ruta / -> index.html
@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(REPO_ROOT / "index.html")

# (Opcional) Fallback para servir otros archivos estáticos directos
@app.get("/{path:path}", include_in_schema=False)
def spa_fallback(path: str):
    candidate = REPO_ROOT / path
    if candidate.exists() and candidate.is_file():
        return FileResponse(candidate)
    return FileResponse(REPO_ROOT / "index.html")

# ====== API ======
app.include_router(health_router)                   # /healthz, /ping
app.include_router(contact_router, prefix="/api")   # /api/contact

