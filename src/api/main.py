"""
FastAPI Enterprise Application Entrypoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.agent_routes import router as agent_router
from src.api.routes.approval_routes import router as approval_router
from src.config import settings

app = FastAPI(
    title="🧑💼 AI Employee & Business Automation API",
    description=(
        "Production-grade Enterprise AI Employee for autonomous mailbox processing, "
        "CRM & Notion synchronization, Human-in-the-Loop decision gating, and daily digests.\n\n"
        "Architected by **Anas AL-Aghbari**."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Cross-Origin Request Security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(agent_router)
app.include_router(approval_router)


@app.get("/health", tags=["System Health"])
def health_check():
    """Liveness probe ensuring the AI Employee service is operating normally."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "environment": settings.app_env,
        "email_mode": settings.email_adapter_mode,
        "crm_mode": settings.crm_adapter_mode,
    }
