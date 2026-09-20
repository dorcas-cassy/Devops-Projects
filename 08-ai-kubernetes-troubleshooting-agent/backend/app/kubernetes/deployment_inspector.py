from app.kubernetes.kubectl_executor import KubectlExecutor

class DeploymentInspector:
    def __init__(self, executor: KubectlExecutor): self.executor = executor
    def inspect(self) -> dict:
        payload, result = self.executor.get_json(["get", "deployments", "-A"])
        if not result.success: return {"healthy": False, "unhealthy_deployments": [], "error": result.stderr}
        unhealthy = []
        for item in payload.get("items", []):
            spec, status = item.get("spec", {}), item.get("status", {})
            desired, available = spec.get("replicas", 1), status.get("availableReplicas", 0)
            unavailable = status.get("unavailableReplicas", 0)
            conditions = status.get("conditions", [])
            failed_conditions = [c.get("reason", c.get("type", "")) for c in conditions if c.get("status") == "False"]
            if available < desired or unavailable or failed_conditions:
                unhealthy.append({"name": item["metadata"]["name"], "namespace": item["metadata"].get("namespace", "default"), "desired_replicas": desired, "available_replicas": available, "unavailable_replicas": unavailable, "failed_conditions": failed_conditions})
        return {"healthy": not unhealthy, "unhealthy_deployments": unhealthy}
