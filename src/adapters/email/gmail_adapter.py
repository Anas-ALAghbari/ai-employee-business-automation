"""
Production Gmail API Adapter.
Handles OAuth2 credentials, unread fetching, drafting, and sending via Google Workspace API.
"""

import base64
import logging
from email.mime.text import MIMEText
from pathlib import Path

from src.config import settings
from src.core.models import EmailMessage
from src.ports.email_port import AbstractEmailService

logger = logging.getLogger(__name__)


class GmailAdapter(AbstractEmailService):
    """Google Workspace / Gmail API adapter for live enterprise mailbox automation."""

    def __init__(self) -> None:
        self.service = None
        self._init_service()

    def _init_service(self) -> None:
        """Initialize Gmail API service using credentials if present."""
        token_path = Path("secrets/token.json")
        creds_path = Path("secrets/credentials.json")

        if not token_path.exists() and not creds_path.exists():
            logger.warning(
                "Gmail credentials not found in secrets/. Running in uninitialized state."
            )
            return

        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            creds = Credentials.from_authorized_user_file(str(token_path))
            self.service = build("gmail", "v1", credentials=creds)
            logger.info("Successfully authenticated with Gmail API.")
        except Exception as err:
            logger.error("Failed to authenticate with Gmail API: %s", err)

    def fetch_unread_messages(self, limit: int = 10) -> list[EmailMessage]:
        if not self.service:
            logger.warning("Gmail service inactive. Returning empty unread list.")
            return []

        try:
            results = (
                self.service.users()
                .messages()
                .list(userId="me", q="is:unread", maxResults=limit)
                .execute()
            )
            messages = results.get("messages", [])
            unread_emails = []

            for msg_meta in messages:
                msg_data = (
                    self.service.users()
                    .messages()
                    .get(userId="me", id=msg_meta["id"], format="full")
                    .execute()
                )
                headers = {h["name"].lower(): h["value"] for h in msg_data["payload"]["headers"]}
                sender = headers.get("from", "unknown@sender.com")
                subject = headers.get("subject", "(No Subject)")
                snippet = msg_data.get("snippet", "")

                unread_emails.append(
                    EmailMessage(
                        id=msg_meta["id"],
                        sender=sender,
                        recipient=settings.sender_email,
                        subject=subject,
                        body=snippet,
                    )
                )
            return unread_emails
        except Exception as err:
            logger.error("Error fetching Gmail unread: %s", err)
            return []

    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        if not self.service:
            logger.warning("Gmail service inactive. Email to %s not sent.", to_email)
            return False

        try:
            message = MIMEText(body)
            message["to"] = to_email
            message["from"] = settings.sender_email
            message["subject"] = subject
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            self.service.users().messages().send(userId="me", body={"raw": raw}).execute()
            return True
        except Exception as err:
            logger.error("Error sending Gmail: %s", err)
            return False

    def create_draft(self, to_email: str, subject: str, body: str) -> str:
        if not self.service:
            logger.warning("Gmail service inactive. Draft for %s not created.", to_email)
            return "DRAFT-LOCAL-MOCK"

        try:
            message = MIMEText(body)
            message["to"] = to_email
            message["from"] = settings.sender_email
            message["subject"] = subject
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            draft = (
                self.service.users()
                .drafts()
                .create(userId="me", body={"message": {"raw": raw}})
                .execute()
            )
            return draft.get("id", "UNKNOWN_DRAFT")
        except Exception as err:
            logger.error("Error creating Gmail draft: %s", err)
            return "ERROR_DRAFT"

    def mark_as_read(self, email_id: str) -> bool:
        if not self.service:
            return False
        try:
            self.service.users().messages().modify(
                userId="me", id=email_id, body={"removeLabelIds": ["UNREAD"]}
            ).execute()
            return True
        except Exception as err:
            logger.error("Error marking Gmail as read: %s", err)
            return False
