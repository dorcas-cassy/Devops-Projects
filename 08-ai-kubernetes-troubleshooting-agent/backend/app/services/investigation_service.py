from app.kubernetes.deployment_inspector import DeploymentInspector
from app.kubernetes.events_analyzer import EventsAnalyzer
from app.kubernetes.kubectl_executor import KubectlExecutor
from app.kubernetes.logs_collector import LogsCollector
from app.kubernetes.network_inspector import NetworkInspector
from app.kubernetes.pod_inspector import PodInspector

class InvestigationService:
    """Collects evidence only; it makes no root-cause or remediation decision."""
    def __init__(self, executor: KubectlExecutor | None = None):
        executor = executor or KubectlExecutor()
        self.pods, self.logs = PodInspector(executor), LogsCollector(executor)
        self.events, self.deployments, self.network = EventsAnalyzer(executor), DeploymentInspector(executor), NetworkInspector(executor)
    def investigate(self) -> dict:
        pods = self.pods.inspect()
        return {"pods": pods, "logs": self.logs.collect(pods.get("problematic_pods", [])), "events": self.events.analyze(), "deployments": self.deployments.inspect(), "network": self.network.inspect()}
