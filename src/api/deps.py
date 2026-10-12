"""
API Dependencies and Services Singleton Container.
"""

from src.adapters.crm.mock_crm_adapter import MockCRMAdapter
from src.adapters.crm.notion_adapter import NotionAdapter
from src.adapters.email.gmail_adapter import GmailAdapter
from src.adapters.email.mock_email_adapter import MockEmailAdapter
from src.adapters.memory.vector_memory_adapter import KnowledgeMemoryAdapter
from src.adapters.notifications.telegram_adapter import TelegramNotificationAdapter
from src.agent.brain import AIEmployeeEngine
from src.config import settings

# Initialize Adapters based on Configuration
if settings.email_adapter_mode == "gmail":
    email_service = GmailAdapter()
else:
    email_service = MockEmailAdapter()

if settings.crm_adapter_mode == "notion":
    crm_service = NotionAdapter()
else:
    crm_service = MockCRMAdapter()

memory_service = KnowledgeMemoryAdapter()
notification_service = TelegramNotificationAdapter()

# Central Engine Instance
engine = AIEmployeeEngine(
    email_service=email_service,
    crm_service=crm_service,
    memory_service=memory_service,
    notification_service=notification_service,
)


def get_agent_engine() -> AIEmployeeEngine:
    """Dependency provider for FastAPI route handlers."""
    return engine
