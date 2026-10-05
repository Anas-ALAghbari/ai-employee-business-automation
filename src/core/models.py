"""
Core Domain Models for Enterprise AI Employee.
Built using Pydantic V2 for high performance and strict type validation.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from src.core.enums import (
    ApprovalStatus,
    IntentType,
    RiskLevel,
    TaskPriority,
    TaskStatus,
)


class EmailMessage(BaseModel):
    """Normalized incoming or outgoing email message."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    recipient: str
    subject: str
    body: str
    received_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_read: bool = False
    thread_id: str | None = None


class CRMContact(BaseModel):
    """Customer / Lead profile stored in Notion / CRM."""
    email: str
    name: str | None = None
    company: str | None = None
    stage: str = "Lead"  # Lead, Qualified, Customer, Churned
    notes: list[str] = Field(default_factory=list)
    last_contacted: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CRMTask(BaseModel):
    """Action item recorded in Notion / CRM task manager."""
    id: str = Field(default_factory=lambda: f"TASK-{uuid.uuid4().hex[:6].upper()}")
    title: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: str = "AI Employee"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    due_date: datetime | None = None


class ApprovalRequest(BaseModel):
    """Human-in-the-Loop review request for high-risk actions."""
    id: str = Field(default_factory=lambda: f"APPR-{uuid.uuid4().hex[:6].upper()}")
    action_type: str  # e.g., "send_custom_quote", "issue_refund", "delete_record"
    title: str
    description: str
    proposed_payload: dict[str, Any]
    risk_level: RiskLevel = RiskLevel.HIGH
    status: ApprovalStatus = ApprovalStatus.PENDING
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None
    review_comment: str | None = None


class AgentAction(BaseModel):
    """Atomic step or tool call recorded during agent execution."""
    tool_name: str
    parameters: dict[str, Any]
    result: Any | None = None
    status: str = "success"
    execution_time_ms: float = 0.0


class AgentDecision(BaseModel):
    """Structured decision output produced by the AI Employee planner."""
    intent: IntentType
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    risk_level: RiskLevel
    requires_approval: bool
    drafted_response: str | None = None
    actions_to_execute: list[dict[str, Any]] = Field(default_factory=list)
    approval_request: ApprovalRequest | None = None


class DailyDigestReport(BaseModel):
    """Executive operational summary generated at end of business day."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: str
    total_emails_processed: int = 0
    tasks_created: int = 0
    approvals_pending: int = 0
    autonomous_actions_count: int = 0
    key_highlights: list[str] = Field(default_factory=list)
    executive_summary: str = ""
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
