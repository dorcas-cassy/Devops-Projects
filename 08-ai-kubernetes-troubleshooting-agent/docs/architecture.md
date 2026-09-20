# Foundation architecture

The frontend calls the FastAPI backend only when a user requests an investigation. The investigation, AI, and external-provider layers are placeholders in this foundation and intentionally perform no Kubernetes or LLM operation.
