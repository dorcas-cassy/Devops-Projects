from app.kubernetes.kubectl_executor import KubectlExecutor

UNHEALTHY_WAITING = {"CrashLoopBackOff", "ImagePullBackOff", "ErrImagePull", "ContainerCreating"}
UNHEALTHY_PHASES = {"Pending", "Failed", "Unknown"}


class PodInspector:
    def __init__(self, executor: KubectlExecutor): self.executor = executor

    def inspect(self) -> dict:
        payload, result = self.executor.get_json(["get", "pods", "-A"])
        if not result.success:
            return {"healthy": False, "problematic_pods": [], "error": result.stderr, "command": result.command}
        problematic = []
        for pod in payload.get("items", []):
            reasons = self._reasons(pod)
            if reasons:
                problematic.append({"name": pod["metadata"]["name"], "namespace": pod["metadata"].get("namespace", "default"), "status": reasons[0], "reasons": reasons})
        return {"healthy": not problematic, "total_pods": len(payload.get("items", [])), "problematic_pods": problematic}

    @staticmethod
    def _reasons(pod: dict) -> list[str]:
        reasons = []
        phase = pod.get("status", {}).get("phase", "")
        if phase in UNHEALTHY_PHASES: reasons.append(phase)
        for status in pod.get("status", {}).get("containerStatuses", []):
            waiting = status.get("state", {}).get("waiting", {}).get("reason")
            terminated = status.get("state", {}).get("terminated", {}).get("reason")
            last_terminated = status.get("lastState", {}).get("terminated", {}).get("reason")
            for reason in (waiting, terminated, last_terminated):
                if reason in UNHEALTHY_WAITING or reason in {"Error", "OOMKilled"}:
                    reasons.append(reason)
        return list(dict.fromkeys(reasons))
