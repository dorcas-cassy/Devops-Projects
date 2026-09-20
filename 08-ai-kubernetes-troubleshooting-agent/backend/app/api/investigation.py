from fastapi import APIRouter
from app.services.investigation_service import InvestigationService

router = APIRouter()

@router.post("/investigate")
def investigate() -> dict:
    return {"status": "success", "investigation": InvestigationService().investigate()}
