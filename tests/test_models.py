"""
Unit tests for domain models and data integrity.
"""

from src.core.enums import ApprovalStatus, RiskLevel, TaskPriority, TaskStatus
from src.core.models import (
    ApprovalRequest,
    CRMContact,
    CRMTask,
    EmailMessage,
)


def test_email_message_model():
    msg = EmailMessage(
        sender="client@corp.com",
        recipient="support@company.com",
        subject="Service Inquiry",
        body="How do I get started?",
    )
    assert msg.id is not None
    assert msg.is_read is False
    assert msg.sender == "client@corp.com"


def test_crm_contact_model():
    contact = CRMContact(
        email="lead@startup.io",
        name="Alex Smith",
        company="Startup IO",
        stage="Qualified",
    )
    assert contact.email == "lead@startup.io"
    assert contact.stage == "Qualified"


def test_crm_task_model():
    task = CRMTask(
        title="Review Architecture",
        description="Verify scalability of agent adapters",
        priority=TaskPriority.HIGH,
    )
    assert task.status == TaskStatus.PENDING
    assert task.priority == TaskPriority.HIGH
    assert task.id.startswith("TASK-")


def test_approval_request_model():
    appr = ApprovalRequest(
        action_type="send_custom_quote",
        title="Enterprise Proposal Review",
        description="500 seats proposal",
        proposed_payload={"recipient": "boss@client.com"},
        risk_level=RiskLevel.HIGH,
    )
    assert appr.id.startswith("APPR-")
    assert appr.status == ApprovalStatus.PENDING
