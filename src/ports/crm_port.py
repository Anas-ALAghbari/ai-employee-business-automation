"""
Abstract Port for CRM and Task Management Services (Notion, HubSpot, Airtable).
"""

from abc import ABC, abstractmethod

from src.core.models import CRMContact, CRMTask, DailyDigestReport


class AbstractCRMService(ABC):
    """Port interface defining standard CRM and Notion operations."""

    @abstractmethod
    def upsert_contact(self, contact: CRMContact) -> bool:
        """Create or update a customer profile."""
        pass

    @abstractmethod
    def get_contact_by_email(self, email: str) -> CRMContact | None:
        """Retrieve customer profile by email."""
        pass

    @abstractmethod
    def create_task(self, task: CRMTask) -> str:
        """Create a new action item or ticket. Returns task ID."""
        pass

    @abstractmethod
    def list_open_tasks(self, limit: int = 50) -> list[CRMTask]:
        """List active pending or in-progress tasks."""
        pass

    @abstractmethod
    def save_daily_digest(self, digest: DailyDigestReport) -> str:
        """Publish the daily operational digest report."""
        pass
