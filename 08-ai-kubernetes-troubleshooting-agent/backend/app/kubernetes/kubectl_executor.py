"""Small, read-only wrapper around the kubectl CLI."""
import json
import os
import subprocess
from dataclasses import asdict, dataclass

from loguru import logger


@dataclass
class KubectlResult:
    command: list[str]
    success: bool
    stdout: str = ""
    stderr: str = ""
    return_code: int | None = None

    def as_dict(self) -> dict:
        return asdict(self)


class KubectlExecutor:
    """Executes a fixed list of read-only kubectl arguments without a shell."""

    def run(self, arguments: list[str]) -> KubectlResult:
        command = ["kubectl", *arguments]
        env = os.environ.copy()
        if kubeconfig := os.getenv("KUBECONFIG_PATH"):
            env["KUBECONFIG"] = kubeconfig
        logger.info("Running kubectl command: {}", " ".join(command))
        try:
            completed = subprocess.run(
                command, capture_output=True, text=True, timeout=30, check=False, env=env
            )
        except FileNotFoundError:
            return KubectlResult(command, False, stderr="kubectl executable was not found")
        except subprocess.TimeoutExpired:
            return KubectlResult(command, False, stderr="kubectl command timed out")
        result = KubectlResult(command, completed.returncode == 0, completed.stdout, completed.stderr, completed.returncode)
        if not result.success:
            logger.warning("kubectl failed ({}): {}", completed.returncode, completed.stderr.strip())
        return result

    def get_json(self, arguments: list[str]) -> tuple[dict, KubectlResult]:
        result = self.run([*arguments, "-o", "json"])
        if not result.success:
            return {}, result
        try:
            return json.loads(result.stdout), result
        except json.JSONDecodeError:
            logger.warning("kubectl returned invalid JSON for {}", result.command)
            result.success = False
            result.stderr = "kubectl returned invalid JSON"
            return {}, result
