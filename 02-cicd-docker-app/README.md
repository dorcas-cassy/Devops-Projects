# CI/CD Docker Application

Node.js API with automated test, image build, container scan, and GitHub Container Registry publishing.

```sh
npm test
docker build -t portfolio-api:local .
docker run --rm -p 8080:8080 portfolio-api:local
curl http://localhost:8080/health
```

Capture: passing Actions workflow, Trivy scan, and `/health` response.
