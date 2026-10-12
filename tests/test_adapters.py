"""
Unit tests for Email and CRM Adapters.
"""

from src.adapters.crm.mock_crm_adapter import MockCRMAdapter
from src.adapters.email.mock_email_adapter import MockEmailAdapter
from src.core.models import CRMContact, CRMTask


def test_mock_email_adapter_operations():
    adapter = MockEmailAdapter()
    unread = adapter.fetch_unread_messages(limit=5)
    assert len(unread) > 0

    first_id = unread[0].id
    adapter.mark_as_read(first_id)

    remaining_unread = adapter.fetch_unread_messages()
    assert all(m.id != first_id for m in remaining_unread)

    # Test send email
    assert adapter.send_email("test@domain.com", "Test Subject", "Test Body") is True
    assert len(adapter.sent_emails) == 1

    # Test create draft
    draft_id = adapter.create_draft("test@domain.com", "Draft Subject", "Draft Body")
    assert draft_id.startswith("DRAFT-")
    assert draft_id in adapter.drafts


def test_mock_crm_adapter_operations():
    crm = MockCRMAdapter()
    contact = CRMContact(
        email="anas@ai-portfolio.com",
        name="Anas AL-Aghbari",
        company="AI Vanguard",
        stage="Customer",
    )
    assert crm.upsert_contact(contact) is True

    fetched = crm.get_contact_by_email("anas@ai-portfolio.com")
    assert fetched is not None
    assert fetched.name == "Anas AL-Aghbari"

    # Test task creation
    task = CRMTask(title="Integration Check", description="Verify Notion webhook")
    task_id = crm.create_task(task)
    assert task_id.startswith("TASK-")

    open_tasks = crm.list_open_tasks()
    assert len(open_tasks) == 1


def test_telegram_notification_adapter():
    from src.adapters.notifications.telegram_adapter import TelegramNotificationAdapter
    from src.core.enums import RiskLevel
    from src.core.models import ApprovalRequest, DailyDigestReport

    notifier = TelegramNotificationAdapter()

    # Test approval alert
    appr = ApprovalRequest(
        action_type="send_quote",
        title="Enterprise 500 Seats",
        description="Requires sign off",
        proposed_payload={"to": "test@corp.com"},
        risk_level=RiskLevel.HIGH,
    )
    assert notifier.send_approval_alert(appr) is True
    assert len(notifier.sent_notifications) == 1

    # Test daily digest alert
    digest = DailyDigestReport(
        date="2026-10-12",
        total_emails_processed=10,
        autonomous_actions_count=8,
        tasks_created=2,
    )
    assert notifier.send_daily_digest_alert(digest) is True
    assert len(notifier.sent_notifications) == 2

    # Test security alert
    assert notifier.send_security_alert("Prompt Injection Quarantined") is True
    assert len(notifier.sent_notifications) == 3
