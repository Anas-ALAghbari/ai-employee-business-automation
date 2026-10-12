"""
Abstract Port for Mobile Alerts & Manager Notifications (Telegram, Slack, Push).
"""

from abc import ABC, abstractmethod

from src.core.models import ApprovalRequest, DailyDigestReport


class AbstractNotificationService(ABC):
    """Port interface defining notification alerts to human supervisors."""

    @abstractmethod
    def send_approval_alert(self, request: ApprovalRequest) -> bool:
        """Send an urgent mobile notification when an action requires human review."""
        pass

    @abstractmethod
    def send_daily_digest_alert(self, digest: DailyDigestReport) -> bool:
        """Send daily operational summary to executive phone/channel."""
        pass

    @abstractmethod
    def send_security_alert(self, details: str) -> bool:
        """Send immediate security alert if prompt injection or breach detected."""
        pass
