from app.kubernetes.deployment_inspector import DeploymentInspector
from app.kubernetes.events_analyzer import EventsAnalyzer
from app.kubernetes.kubectl_executor import KubectlExecutor
from app.kubernetes.logs_collector import LogsCollector
from app.kubernetes.network_inspector import NetworkInspector
from app.kubernetes.pod_inspector import PodInspector


class InvestigationService:
    """Collects evidence in a fixed, read-only sequence."""

    def __init__(self, executor: KubectlExecutor | None = None, context: str | None = None):
        executor = executor or KubectlExecutor(context=context)
        self.pods = PodInspector(executor)
        self.logs = LogsCollector(executor)
        self.events = EventsAnalyzer(executor)
        self.deployments = DeploymentInspector(executor)
        self.network = NetworkInspector(executor)

    def steps(self):
        evidence = {}
        yield {"stage": "checking_pods"}
        evidence["pods"] = self.pods.inspect()
        if evidence["pods"].get("error"):
            evidence.update({"logs": {}, "events": {}, "deployments": {}, "network": {}})
            yield {"stage": "evidence_collected", "investigation": evidence}
            return
        yield {"stage": "reading_logs"}
        evidence["logs"] = self.logs.collect(evidence["pods"].get("problematic_pods", []))
        yield {"stage": "analyzing_events"}
        evidence["events"] = self.events.analyze()
        yield {"stage": "inspecting_deployments"}
        evidence["deployments"] = self.deployments.inspect()
        yield {"stage": "checking_networking"}
        evidence["network"] = self.network.inspect()
        yield {"stage": "evidence_collected", "investigation": evidence}

    def investigate(self) -> dict:
        evidence = {}
        for update in self.steps():
            if "investigation" in update:
                evidence = update["investigation"]
        return evidence
