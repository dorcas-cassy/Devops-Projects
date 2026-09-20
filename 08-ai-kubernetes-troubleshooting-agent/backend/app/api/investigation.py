from fastapi import APIRouter
from loguru import logger
from app.ai.root_cause_analyzer import RootCauseAnalyzer
from app.services.investigation_service import InvestigationService

router = APIRouter()

@router.post("/investigate")
def investigate() -> dict:
    investigation = InvestigationService().investigate()
    try:
        diagnosis = RootCauseAnalyzer().analyze(investigation).api_payload()
        return {"status": "success", "investigation": investigation, "diagnosis": diagnosis}
    except Exception as exc:
        logger.warning("Diagnosis generation unavailable: {}", type(exc).__name__)
        return {"status": "partial_success", "investigation": investigation, "diagnosis": {"available": False, "error": "Diagnosis generation is unavailable. Check OpenRouter configuration and evidence collection."}}
