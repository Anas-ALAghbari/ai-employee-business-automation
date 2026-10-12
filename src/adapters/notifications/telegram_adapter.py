"""
Production & Mock Telegram Alert Adapter.
Dispatches mobile push notifications to supervisors for HITL approvals and critical alerts.
"""

import logging
from typing import Any

import httpx

from src.config import settings
from src.core.models import ApprovalRequest, DailyDigestReport
from src.ports.notification_port import AbstractNotificationService

logger = logging.getLogger(__name__)


class TelegramNotificationAdapter(AbstractNotificationService):
    """Telegram Bot alert adapter for manager notifications."""

    def __init__(self) -> None:
        self.bot_token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
        self.sent_notifications: list[dict[str, Any]] = []

    def _send_telegram_message(self, text: str) -> bool:
        """Helper to send a message via Telegram Bot API or mock log."""
        if not self.bot_token or not self.chat_id:
            logger.info("[Telegram Alert Mock] %s", text)
            self.sent_notifications.append({"channel": "mock_telegram", "text": text})
            return True

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown",
        }
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    self.sent_notifications.append({"channel": "live_telegram", "text": text})
                    return True
                logger.error("Failed to send Telegram alert: HTTP %s - %s", res.status_code, res.text)
                return False
        except Exception as err:
            logger.error("Telegram API connection error: %s", err)
            return False

    def send_approval_alert(self, request: ApprovalRequest) -> bool:
        message = (
            f"🚨 *AI EMPLOYEE: APPROVAL REQUIRED*\n\n"
            f"🆔 *ID*: `{request.id}`\n"
            f"📌 *Action*: {request.title}\n"
            f"⚠️ *Risk*: {request.risk_level.value.upper()}\n"
            f"📝 *Description*: {request.description}\n\n"
            f"👉 _Review and approve in the Command Dashboard._"
        )
        return self._send_telegram_message(message)

    def send_daily_digest_alert(self, digest: DailyDigestReport) -> bool:
        message = (
            f"📊 *EXECUTIVE DAILY DIGEST ({digest.date})*\n\n"
            f"📈 *Processed Emails*: {digest.total_emails_processed}\n"
            f"⚡ *Autonomous Resolutions*: {digest.autonomous_actions_count}\n"
            f"📋 *Tasks Created*: {digest.tasks_created}\n"
            f"⏸️ *Pending Approvals*: {digest.approvals_pending}\n\n"
            f"📝 *Summary*:\n{digest.executive_summary}"
        )
        return self._send_telegram_message(message)

    def send_security_alert(self, details: str) -> bool:
        message = (
            f"🛡️ *SECURITY INCIDENT QUARANTINED*\n\n"
            f"Threat intercepted: {details}\n"
            f"Zero unauthorized operations were executed."
        )
        return self._send_telegram_message(message)
