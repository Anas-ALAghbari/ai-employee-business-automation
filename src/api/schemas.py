"""
API Request and Response Data Transfer Objects (DTOs).
"""

from typing import Any

from pydantic import BaseModel, Field

from src.core.enums import ApprovalStatus, IntentType, RiskLevel


class EmailProcessRequest(BaseModel):
    """Payload to trigger processing of a single email message."""
    sender: str
    recipient: str = "support@company.com"
    subject: str
    body: str


class ProcessEmailResponse(BaseModel):
    """Response returned after AI Employee evaluates the email."""
    intent: IntentType
    risk_level: RiskLevel
    requires_approval: bool
    drafted_response: str | None = None
    reasoning: str
    approval_id: str | None = None


class ApprovalActionRequest(BaseModel):
    """Request payload to approve or reject a pending Human-in-the-Loop request."""
    reviewer_name: str = Field(..., json_schema_extra={"example": "Anas AL-Aghbari"})
    approved: bool
    comment: str | None = Field(None, json_schema_extra={"example": "Approved with 10% volume discount applied."})


class ApprovalItemResponse(BaseModel):
    """Details of a pending approval item."""
    id: str
    action_type: str
    title: str
    description: str
    proposed_payload: dict[str, Any]
    risk_level: RiskLevel
    status: ApprovalStatus


class DailyDigestTriggerRequest(BaseModel):
    """Optional parameters when manually requesting a daily digest."""
    date: str | None = None


class DailyDigestResponse(BaseModel):
    """Structured executive daily digest summary."""
    date: str
    total_emails_processed: int
    tasks_created: int
    approvals_pending: int
    autonomous_actions_count: int
    executive_summary: str
    key_highlights: list[str]
