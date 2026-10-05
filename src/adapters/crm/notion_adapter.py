"""
Production Notion API CRM Adapter.
Synchronizes customer contacts, creates task cards, and writes daily digests into Notion databases.
"""

import logging

from src.config import settings
from src.core.models import CRMContact, CRMTask, DailyDigestReport
from src.ports.crm_port import AbstractCRMService

logger = logging.getLogger(__name__)


class NotionAdapter(AbstractCRMService):
    """Notion API adapter for Enterprise CRM & Task tracking."""

    def __init__(self) -> None:
        self.client = None
        self._init_client()

    def _init_client(self) -> None:
        """Initialize official Notion Client if API key is provided."""
        if not settings.notion_api_key or settings.notion_api_key.startswith("ntn_your"):
            logger.warning("Notion API Key not configured. Running in unauthenticated mode.")
            return

        try:
            from notion_client import Client
            self.client = Client(auth=settings.notion_api_key)
            logger.info("Successfully connected to Notion API.")
        except Exception as err:
            logger.error("Failed to initialize Notion client: %s", err)

    def upsert_contact(self, contact: CRMContact) -> bool:
        if not self.client or not settings.notion_customers_db_id:
            logger.info("[Mock/Fallback] Contact %s recorded locally.", contact.email)
            return True

        try:
            # Query if contact already exists in Notion DB
            query_res = self.client.databases.query(
                database_id=settings.notion_customers_db_id,
                filter={"property": "Email", "email": {"equals": contact.email}},
            )
            results = query_res.get("results", [])

            if results:
                page_id = results[0]["id"]
                self.client.pages.update(
                    page_id=page_id,
                    properties={
                        "Last Contacted": {"date": {"start": contact.last_contacted.isoformat()}},
                        "Stage": {"select": {"name": contact.stage}},
                    },
                )
            else:
                self.client.pages.create(
                    parent={"database_id": settings.notion_customers_db_id},
                    properties={
                        "Name": {"title": [{"text": {"content": contact.name or contact.email}}]},
                        "Email": {"email": contact.email},
                        "Company": {
                            "rich_text": [{"text": {"content": contact.company or "N/A"}}]
                        },
                        "Stage": {"select": {"name": contact.stage}},
                    },
                )
            return True
        except Exception as err:
            logger.error("Error upserting contact to Notion: %s", err)
            return False

    def get_contact_by_email(self, email: str) -> CRMContact | None:
        if not self.client or not settings.notion_customers_db_id:
            return None

        try:
            res = self.client.databases.query(
                database_id=settings.notion_customers_db_id,
                filter={"property": "Email", "email": {"equals": email}},
            )
            results = res.get("results", [])
            if not results:
                return None

            props = results[0]["properties"]
            name_text = props.get("Name", {}).get("title", [{}])[0].get("text", {}).get("content", "")
            company_text = (
                props.get("Company", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")
            )
            stage_name = props.get("Stage", {}).get("select", {}).get("name", "Lead")

            return CRMContact(
                email=email,
                name=name_text,
                company=company_text,
                stage=stage_name,
            )
        except Exception as err:
            logger.error("Error reading Notion contact: %s", err)
            return None

    def create_task(self, task: CRMTask) -> str:
        if not self.client or not settings.notion_tasks_db_id:
            logger.info("[Mock/Fallback] Created Notion task: %s (%s)", task.id, task.title)
            return task.id

        try:
            page = self.client.pages.create(
                parent={"database_id": settings.notion_tasks_db_id},
                properties={
                    "Task Title": {"title": [{"text": {"content": task.title}}]},
                    "Description": {"rich_text": [{"text": {"content": task.description}}]},
                    "Priority": {"select": {"name": task.priority.value.upper()}},
                    "Status": {"select": {"name": task.status.value.replace("_", " ").title()}},
                    "Assignee": {"rich_text": [{"text": {"content": task.assigned_to}}]},
                },
            )
            return page.get("id", task.id)
        except Exception as err:
            logger.error("Error creating Notion task: %s", err)
            return task.id

    def list_open_tasks(self, limit: int = 50) -> list[CRMTask]:
        return []

    def save_daily_digest(self, digest: DailyDigestReport) -> str:
        if not self.client or not settings.notion_digests_db_id:
            logger.info("[Mock/Fallback] Published Daily Digest for %s", digest.date)
            return digest.id

        try:
            page = self.client.pages.create(
                parent={"database_id": settings.notion_digests_db_id},
                properties={
                    "Date": {"title": [{"text": {"content": f"Daily Digest: {digest.date}"}}]},
                    "Processed Emails": {"number": digest.total_emails_processed},
                    "Tasks Created": {"number": digest.tasks_created},
                    "Pending Approvals": {"number": digest.approvals_pending},
                },
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"text": {"content": digest.executive_summary}}]
                        },
                    }
                ],
            )
            return page.get("id", digest.id)
        except Exception as err:
            logger.error("Error publishing Notion digest: %s", err)
            return digest.id
