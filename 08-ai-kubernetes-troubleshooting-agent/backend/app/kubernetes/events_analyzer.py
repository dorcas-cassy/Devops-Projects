from app.kubernetes.kubectl_executor import KubectlExecutor

EVENT_REASONS = {"FailedScheduling", "BackOff", "FailedMount", "FailedPull", "ErrImagePull", "Unhealthy"}

class EventsAnalyzer:
    def __init__(self, executor: KubectlExecutor): self.executor = executor
    def analyze(self) -> dict:
        payload, result = self.executor.get_json(["get", "events", "-A"])
        if not result.success: return {"findings": [], "error": result.stderr}
        findings = []
        for event in payload.get("items", []):
            reason, message = event.get("reason", ""), event.get("message", "")
            if reason in EVENT_REASONS or "dns" in message.lower():
                findings.append({"namespace": event.get("metadata", {}).get("namespace", "default"), "reason": reason, "message": message, "object": event.get("involvedObject", {}).get("name", ""), "type": event.get("type", "")})
        return {"findings": findings}
