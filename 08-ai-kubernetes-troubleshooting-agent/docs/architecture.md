# Architecture

The Next.js frontend calls the FastAPI backend when a user requests an investigation. The backend runs a fixed set of read-only `kubectl` inspections, organizes the returned evidence, and passes it to the OpenRouter reasoning layer for a diagnosis. The application does not execute suggested fixes.

Docker Compose starts the backend and frontend together. The backend image includes a pinned, checksum-verified `kubectl` client. Kubernetes credentials are optional and can be mounted read-only with `docker-compose.kubeconfig.yml`; kubeconfigs that depend on external authentication plugins also need those plugins in the container. OpenRouter settings are read from `backend/.env` at runtime. The browser-facing API URL is embedded in the frontend at build time.
