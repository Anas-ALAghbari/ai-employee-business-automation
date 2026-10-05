"""
Mock CRM Adapter for testing, offline demos, and unit test suites.
"""


from src.core.models import CRMContact, CRMTask, DailyDigestReport
from src.ports.crm_port import AbstractCRMService


class MockCRMAdapter(AbstractCRMService):
    """In-memory Notion/CRM database simulator."""

    def __init__(self) -> None:
        self.contacts: dict[str, CRMContact] = {}
        self.tasks: dict[str, CRMTask] = {}
        self.digests: list[DailyDigestReport] = []

    def upsert_contact(self, contact: CRMContact) -> bool:
        if contact.email in self.contacts:
            existing = self.contacts[contact.email]
            existing.notes.extend(contact.notes)
            existing.last_contacted = contact.last_contacted
            if contact.name:
                existing.name = contact.name
            if contact.company:
                existing.company = contact.company
        else:
            self.contacts[contact.email] = contact
        return True

    def get_contact_by_email(self, email: str) -> CRMContact | None:
        return self.contacts.get(email)

    def create_task(self, task: CRMTask) -> str:
        self.tasks[task.id] = task
        return task.id

    def list_open_tasks(self, limit: int = 50) -> list[CRMTask]:
        return list(self.tasks.values())[:limit]

    def save_daily_digest(self, digest: DailyDigestReport) -> str:
        self.digests.append(digest)
        return digest.id
