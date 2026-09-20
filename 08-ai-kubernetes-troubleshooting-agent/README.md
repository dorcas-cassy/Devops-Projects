# AI Kubernetes Troubleshooting Agent

Foundation for an on-demand Kubernetes troubleshooting application. The current version provides a FastAPI health service and a Next.js starter UI only. Kubernetes investigation, AI reasoning, OpenRouter, InsForge, authentication, and realtime behavior are deliberately not implemented yet.

## Run with Docker

```sh
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
docker compose up --build
```

Open [http://localhost:3000](http://localhost:3000) and [http://localhost:8000/health](http://localhost:8000/health).

## Structure

```text
backend/    FastAPI application and future integration boundaries
frontend/   Next.js UI
docs/       Design notes
prompts/    Future AI prompts
```

Never commit real API keys, kubeconfig files, or `.env` files.
