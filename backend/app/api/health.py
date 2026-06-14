from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {
        "status": "running",
        "project": "Life OS AI",
        "message": "Backend foundation is ready"
    }
