from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.health import router as health_router
from app.api.investigation import router as investigation_router
from app.core.config import settings

logger.info("Starting {}", settings.service_name)

app = FastAPI(title="AI Kubernetes Troubleshooting Agent", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(investigation_router)
