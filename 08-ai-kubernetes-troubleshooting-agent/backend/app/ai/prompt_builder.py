import json

SYSTEM_PROMPT = """You are a Senior Kubernetes SRE. Diagnose only from supplied evidence. Correlate pod state, logs, events, deployments, and networking; do not invent facts. Give practical Kubernetes actions. Return only valid JSON with exactly: root_cause, explanation, suggested_fix, kubectl_commands, prevention_recommendation, confidence, confidence_reasoning. confidence is an integer 0-100; kubectl_commands is an array. Commands are suggestions only and were not run."""

class PromptBuilder:
    def build(self, investigation: dict) -> list[dict[str, str]]:
        sections = [("POD STATUS", "pods"), ("LOGS", "logs"), ("EVENTS", "events"), ("DEPLOYMENT HEALTH", "deployments"), ("NETWORKING FINDINGS", "network")]
        evidence = "\n\n".join(f"{title}:\n{json.dumps(investigation.get(key, {}), indent=2)}" for title, key in sections)
        return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": f"Investigate this Kubernetes evidence:\n\n{evidence}"}]
