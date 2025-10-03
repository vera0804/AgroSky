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




