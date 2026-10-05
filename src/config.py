"""
Application Configuration Module.
Loads environment variables and provides strongly-typed settings across the application.
"""

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

# Load .env file if it exists
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    """Enterprise AI Employee Settings."""

    def __init__(self) -> None:
        self.app_name: str = "AI Employee & Business Automation"
        self.app_env: str = os.getenv("APP_ENV", "development")
        self.app_debug: bool = os.getenv("APP_DEBUG", "true").lower() in ("true", "1", "yes")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.host: str = os.getenv("HOST", "0.0.0.0")

        # Security & Autonomy Guardrails
        self.max_refund_limit: float = float(os.getenv("MAX_AUTONOMOUS_REFUND_AMOUNT", "50.00"))
        self.max_discount_limit: float = float(os.getenv("MAX_AUTONOMOUS_DISCOUNT_PERCENT", "10.0"))
        self.prompt_injection_strict: bool = (
            os.getenv("PROMPT_INJECTION_STRICT_MODE", "true").lower() in ("true", "1", "yes")
        )
        self.require_approval_for_quotes: bool = (
            os.getenv("REQUIRE_HUMAN_APPROVAL_FOR_QUOTES", "true").lower() in ("true", "1", "yes")
        )

        # AI Provider Settings
        self.ai_provider: Literal["mock", "gemini", "openai"] = os.getenv(
            "AI_PROVIDER", "mock"
        ).lower()  # type: ignore
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.ai_model_name: str = os.getenv("AI_MODEL_NAME", "gemini-2.0-flash")

        # Adapters Configuration
        self.email_adapter_mode: Literal["mock", "gmail"] = os.getenv(
            "EMAIL_ADAPTER_MODE", "mock"
        ).lower()  # type: ignore
        self.sender_email: str = os.getenv("SENDER_EMAIL", "ai-employee@company.com")

        self.crm_adapter_mode: Literal["mock", "notion"] = os.getenv(
            "CRM_ADAPTER_MODE", "mock"
        ).lower()  # type: ignore
        self.notion_api_key: str = os.getenv("NOTION_API_KEY", "")
        self.notion_customers_db_id: str = os.getenv("NOTION_CUSTOMERS_DB_ID", "")
        self.notion_tasks_db_id: str = os.getenv("NOTION_TASKS_DB_ID", "")
        self.notion_digests_db_id: str = os.getenv("NOTION_DIGESTS_DB_ID", "")

        self.redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")


# Global Singleton Settings Instance
settings = Settings()
