#!/usr/bin/env python3
"""Create a short-lived, minimal kubeconfig for a local Docker investigation."""

import json
import os
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit, urlunsplit


def capture(command: list[str]) -> str:
    try:
        return subprocess.run(
            command, check=True, capture_output=True, text=True, timeout=30
        ).stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        raise RuntimeError(f"{command[0]} failed; check your local GKE login and current context") from None


def main() -> None:
    config = json.loads(capture(["kubectl", "config", "view", "--raw", "-o", "json"]))
    if not config.get("contexts") or not config.get("users"):
        raise RuntimeError("no Kubernetes contexts found in the host kubeconfig")
    # Replace macOS GKE auth helpers while preserving every local context.
    gke_users = [
        item for item in config["users"]
        if "gke-gcloud-auth-plugin" in item.get("user", {}).get("exec", {}).get("command", "")
    ]
    if gke_users:
        token = capture(["gcloud", "auth", "print-access-token"])
        if not token:
            raise RuntimeError("gcloud returned an empty access token")
        for item in gke_users:
            item["user"] = {"token": token}
    for item in config.get("clusters", []):
        cluster = item.get("cluster", {})
        server = urlsplit(cluster.get("server", ""))
        if server.hostname in {"127.0.0.1", "localhost"} and server.port:
            cluster["server"] = urlunsplit(server._replace(netloc=f"host.docker.internal:{server.port}"))
            cluster["tls-server-name"] = server.hostname
    fd, path = tempfile.mkstemp(prefix="ai-k8s-agent-", suffix=".kubeconfig")
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(config, stream)
            stream.write("\n")
    except Exception:
        os.unlink(path)
        raise
    print(path)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"Could not create Docker kubeconfig: {exc}", file=sys.stderr)
        raise SystemExit(1)
