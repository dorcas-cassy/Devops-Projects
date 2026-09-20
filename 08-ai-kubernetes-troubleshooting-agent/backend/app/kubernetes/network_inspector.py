from app.kubernetes.kubectl_executor import KubectlExecutor

class NetworkInspector:
    def __init__(self, executor: KubectlExecutor): self.executor = executor
    def inspect(self) -> dict:
        services, service_result = self.executor.get_json(["get", "services", "-A"])
        endpoints, endpoint_result = self.executor.get_json(["get", "endpoints", "-A"])
        pods, pod_result = self.executor.get_json(["get", "pods", "-A"])
        if not all((service_result.success, endpoint_result.success, pod_result.success)):
            return {"findings": [], "error": "; ".join(x.stderr for x in (service_result, endpoint_result, pod_result) if not x.success)}
        endpoint_keys = {(item.get("metadata", {}).get("namespace", "default"), item.get("metadata", {}).get("name")) for item in endpoints.get("items", []) if item.get("subsets")}
        pod_labels = {(pod.get("metadata", {}).get("namespace", "default"), tuple(sorted(pod.get("metadata", {}).get("labels", {}).items()))) for pod in pods.get("items", [])}
        findings = []
        for service in services.get("items", []):
            metadata, spec = service.get("metadata", {}), service.get("spec", {})
            namespace, name, selector = metadata.get("namespace", "default"), metadata.get("name", ""), spec.get("selector", {})
            if selector and not any(ns == namespace and all(item in labels for item in selector.items()) for ns, labels in pod_labels):
                findings.append({"service": name, "namespace": namespace, "issue": "selector_mismatch", "selector": selector})
            if selector and (namespace, name) not in endpoint_keys:
                findings.append({"service": name, "namespace": namespace, "issue": "missing_endpoints"})
        return {"services_checked": len(services.get("items", [])), "findings": findings}
