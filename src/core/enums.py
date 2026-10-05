"""
Domain Enums for Enterprise AI Employee.
"""

from enum import StrEnum


class IntentType(StrEnum):
    """Categorized intent of an incoming customer request."""
    INQUIRY = "general_inquiry"
    SUPPORT_TICKET = "support_ticket"
    SALES_LEAD = "sales_lead"
    BILLING_DISPUTE = "billing_dispute"
    SECURITY_ANOMALY = "security_anomaly"
    FEEDBACK = "customer_feedback"
    UNKNOWN = "unknown"


class RiskLevel(StrEnum):
    """Risk tiers that govern whether autonomous execution is permitted."""
    LOW = "low"          # Autonomous execution safe
    MEDIUM = "medium"    # Logged, autonomous with safeguards
    HIGH = "high"        # Strict Human-in-the-Loop required
    CRITICAL = "critical"# Execution blocked, security alert triggered


class TaskPriority(StrEnum):
    """Priority level for CRM and workflow tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(StrEnum):
    """Execution status of tasks."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    WAITING_APPROVAL = "waiting_approval"
    REJECTED = "rejected"
    FAILED = "failed"


class ApprovalStatus(StrEnum):
    """Human-in-the-Loop approval state."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
