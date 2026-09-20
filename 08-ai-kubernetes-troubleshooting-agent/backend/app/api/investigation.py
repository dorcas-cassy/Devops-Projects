import hmac
import json

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger
from pydantic import BaseModel

from app.ai.root_cause_analyzer import RootCauseAnalyzer
from app.core.config import settings
from app.kubernetes.kubectl_executor import KubectlExecutor
from app.services.investigation_service import InvestigationService

router = APIRouter()


class InvestigationRequest(BaseModel):
    context: str | None = None


def require_internal_token(x_internal_token: str | None = Header(default=None)) -> None:
    if not settings.backend_internal_token or not x_internal_token or not hmac.compare_digest(
        x_internal_token, settings.backend_internal_token
    ):
        raise HTTPException(401, "Authentication required.")


def _selected_context(request: InvestigationRequest | None) -> str:
    executor = KubectlExecutor()
    contexts, result = executor.list_contexts()
    if not result.success or not contexts:
        raise HTTPException(503, "No Kubernetes contexts found. Mount a kubeconfig and check kubectl access.")
    selected = request.context if request else None
    selected = selected or executor.current_context()
    if selected not in contexts:
        raise HTTPException(400, "Select a context from the available Kubernetes clusters.")
    return selected


def _cluster_error(stderr: str) -> str:
    value = stderr.lower()
    if "forbidden" in value or "permission" in value:
        return "Kubernetes denied access. Check the selected account's read permissions."
    if "unauthorized" in value or "credentials" in value or "auth" in value:
        return "Kubernetes authentication failed. Refresh your cluster credentials."
    if any(term in value for term in ("connection refused", "timeout", "timed out", "deadline exceeded", "awaiting headers", "unable to connect")):
        return "Unable to reach the Kubernetes cluster. Check its connection and kubeconfig."
    return "Unable to inspect the Kubernetes cluster. Check kubeconfig and kubectl access."


def _diagnose(context: str, investigation: dict) -> dict:
    failures = [
        investigation[key].get("error", "")
        for key in ("pods", "events", "deployments", "network")
        if investigation[key].get("error")
    ]
    if failures:
        raise HTTPException(503, _cluster_error("; ".join(failures)))

    no_issues = (
        investigation["pods"].get("healthy")
        and investigation["deployments"].get("healthy")
        and not investigation["events"].get("findings")
        and not investigation["network"].get("findings")
    )
    if no_issues:
        return {"status": "healthy", "context": context, "investigation": investigation, "diagnosis": None}

    try:
        diagnosis = RootCauseAnalyzer().analyze(investigation).api_payload()
        return {"status": "success", "context": context, "investigation": investigation, "diagnosis": diagnosis}
    except Exception as exc:
        logger.warning("Diagnosis generation unavailable: {}", type(exc).__name__)
        return {
            "status": "partial_success",
            "context": context,
            "investigation": investigation,
            "diagnosis": {"available": False, "error": "Evidence was collected, but AI diagnosis is unavailable. Check OpenRouter configuration."},
        }


@router.get("/clusters", dependencies=[Depends(require_internal_token)])
def clusters() -> dict:
    executor = KubectlExecutor()
    contexts, result = executor.list_contexts()
    if not result.success or not contexts:
        raise HTTPException(503, "No Kubernetes contexts found. Mount a kubeconfig and check kubectl access.")
    return {"contexts": contexts, "current_context": executor.current_context()}


@router.post("/investigate", dependencies=[Depends(require_internal_token)])
def investigate(request: InvestigationRequest | None = None) -> dict:
    context = _selected_context(request)
    investigation = InvestigationService(context=context).investigate()
    return _diagnose(context, investigation)


@router.post("/investigate/stream", dependencies=[Depends(require_internal_token)])
def investigate_stream(request: InvestigationRequest | None = None) -> StreamingResponse:
    context = _selected_context(request)

    def events():
        try:
            evidence = {}
            for update in InvestigationService(context=context).steps():
                if "investigation" in update:
                    evidence = update["investigation"]
                    break
                yield json.dumps(update) + "\n"
            yield json.dumps({"stage": "ai_reasoning"}) + "\n"
            result = _diagnose(context, evidence)
            yield json.dumps({"stage": "complete", "result": result}) + "\n"
        except HTTPException as exc:
            yield json.dumps({"stage": "error", "error": exc.detail}) + "\n"
        except Exception as exc:
            logger.exception("Investigation stream failed: {}", type(exc).__name__)
            yield json.dumps({"stage": "error", "error": "Investigation failed. Check backend logs and cluster access."}) + "\n"

    return StreamingResponse(events(), media_type="application/x-ndjson")
