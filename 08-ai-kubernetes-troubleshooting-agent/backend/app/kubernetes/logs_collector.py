from app.kubernetes.kubectl_executor import KubectlExecutor

KEYWORDS = ("exception", "error", "failed", "connection refused", "connection timed out", "env", "startup", "missing", "not set")

class LogsCollector:
    def __init__(self, executor: KubectlExecutor): self.executor = executor

    def collect(self, problematic_pods: list[dict]) -> dict:
        findings = []
        for pod in problematic_pods[:10]:
            command = ["logs", "-n", pod["namespace"], pod["name"], "--all-containers", "--tail=100"]
            result = self.executor.run(command)
            if not result.stdout:
                previous = self.executor.run([*command, "--previous"])
                if previous.stdout:
                    result = previous
                elif result.success:
                    result = self.executor.run(command)
            lines = [line for line in result.stdout.splitlines() if any(word in line.lower() for word in KEYWORDS)]
            findings.append({"pod": pod["name"], "namespace": pod["namespace"], "success": result.success, "relevant_lines": lines[-20:], "error": result.stderr if not result.success else ""})
        return {"collected_for": len(findings), "findings": findings}
