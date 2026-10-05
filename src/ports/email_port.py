"""
Abstract Port for Email Services (Gmail, SendGrid, SMTP).
"""

from abc import ABC, abstractmethod

from src.core.models import EmailMessage


class AbstractEmailService(ABC):
    """Port interface defining standard email capabilities."""

    @abstractmethod
    def fetch_unread_messages(self, limit: int = 10) -> list[EmailMessage]:
        """Fetch incoming unread emails."""
        pass

    @abstractmethod
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send an email directly to a recipient."""
        pass

    @abstractmethod
    def create_draft(self, to_email: str, subject: str, body: str) -> str:
        """Create a draft email for human review. Returns draft ID."""
        pass

    @abstractmethod
    def mark_as_read(self, email_id: str) -> bool:
        """Mark processed email as read."""
        pass
