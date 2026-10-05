"""
Abstract Port for Knowledge Base and Audit Memory Services.
"""

from abc import ABC, abstractmethod
from typing import Any

from src.core.models import AgentAction, ApprovalRequest


class AbstractMemoryService(ABC):
    """Port interface defining standard Vector / Audit memory operations."""

    @abstractmethod
    def search_policies(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """Search corporate knowledge base, SOPs, and policies."""
        pass

    @abstractmethod
    def record_audit(self, action: AgentAction) -> None:
        """Store step trace in immutable audit log."""
        pass

    @abstractmethod
    def save_approval_request(self, request: ApprovalRequest) -> None:
        """Store a pending Human-in-the-Loop review request."""
        pass

    @abstractmethod
    def get_approval_request(self, request_id: str) -> ApprovalRequest | None:
        """Fetch pending approval by ID."""
        pass

    @abstractmethod
    def list_pending_approvals(self) -> list[ApprovalRequest]:
        """List all pending reviews waiting for human manager."""
        pass

    @abstractmethod
    def update_approval_status(self, request_id: str, approved: bool, reviewer: str, comment: str) -> bool:
        """Mark approval request as approved or rejected."""
        pass
