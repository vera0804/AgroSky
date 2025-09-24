from fastapi import APIRouter
router = APIRouter(tags=["health"])

@router.get("/healthz")
def healthz():
    return {"ok": True}

@router.get("/ping")
def ping():
    return {"message": "pong"}
