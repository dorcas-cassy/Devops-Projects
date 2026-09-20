# Observability and Incident-Response Lab

Docker Compose lab with a deliberately small metrics API, Prometheus scraping, and Grafana provisioning. The API exposes request count and error count; use `/error` to simulate a failed request safely.

```sh
docker compose up --build
# API: http://localhost:8000/health
# Metrics: http://localhost:8000/metrics
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000  (admin / admin)
```

Generate evidence:

```sh
curl http://localhost:8000/health
curl -i http://localhost:8000/error
curl http://localhost:8000/metrics
```

Capture Grafana, Prometheus target health, and the incident timeline after you run the lab.
