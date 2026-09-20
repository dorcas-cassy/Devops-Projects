# Simulated elevated-error incident

1. Confirm `/health` returns 200 and Prometheus target is `UP`.
2. Generate one or more safe failures with `/error`; never use this endpoint outside the local Compose lab.
3. Inspect `portfolio_errors_total` and correlate with API logs.
4. Record start time, blast radius, mitigation, and verification.
5. Close when health is normal and no further error growth is observed.
