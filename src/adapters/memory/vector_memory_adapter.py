"""
Knowledge Base & Memory Adapter.
Stores corporate SOPs, FAQs, execution audit trails, and Human-in-the-Loop approval requests.
"""

from datetime import UTC, datetime
from typing import Any

from src.core.enums import ApprovalStatus
from src.core.models import AgentAction, ApprovalRequest
from src.ports.memory_port import AbstractMemoryService


class KnowledgeMemoryAdapter(AbstractMemoryService):
    """Knowledge base and operational memory store for the AI Employee."""

    def __init__(self) -> None:
        self.audit_log: list[AgentAction] = []
        self.approvals: dict[str, ApprovalRequest] = {}
        self.knowledge_documents: list[dict[str, str]] = []
        self._seed_corporate_knowledge()

    def _seed_corporate_knowledge(self) -> None:
        """Seed enterprise operating guidelines and FAQs."""
        self.knowledge_documents.extend([
            {
                "topic": "business_hours",
                "title": "Business Support Operating Hours",
                "content": (
                    "Our customer support desk operates Monday through Friday, 8:00 AM to 6:00 PM EST. "
                    "For enterprise tier accounts with custom SLAs, 24/7 on-call coverage is provided."
                ),
            },
            {
                "topic": "pricing_and_plans",
                "title": "Standard Pricing and Seat Tiers",
                "content": (
                    "Starter: $29/seat/mo (up to 10 users). "
                    "Growth: $79/seat/mo (up to 50 users). "
                    "Enterprise: Custom pricing for 100+ users. Requires a formal proposal by Account Executive."
                ),
            },
            {
                "topic": "refund_policy",
                "title": "Refund and Billing Policy",
                "content": (
                    "Full refund within first 14 days of subscription. "
                    "Partial refunds up to $50 can be handled autonomously. "
                    "Refunds above $50 or contract cancellations require Financial Director approval."
                ),
            },
            {
                "topic": "sla_policy",
                "title": "Service Level Agreement (SLA)",
                "content": (
                    "Enterprise accounts receive a 99.9% uptime SLA with 1-hour critical response time guarantee."
                ),
            },
        ])

    def search_policies(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """
        Keyword and semantic relevance matching across corporate knowledge docs.
        """
        query_tokens = query.lower().split()
        scored_docs = []

        for doc in self.knowledge_documents:
            text = (doc["title"] + " " + doc["content"]).lower()
            score = sum(1 for token in query_tokens if token in text)
            if score > 0:
                scored_docs.append((score, doc))

        # Sort by match score descending
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        results = [doc for _, doc in scored_docs[:top_k]]

        # Fallback to general policies if no direct keyword match
        if not results:
            results = self.knowledge_documents[:top_k]

        return results

    def record_audit(self, action: AgentAction) -> None:
        self.audit_log.append(action)

    def save_approval_request(self, request: ApprovalRequest) -> None:
        self.approvals[request.id] = request

    def get_approval_request(self, request_id: str) -> ApprovalRequest | None:
        return self.approvals.get(request_id)

    def list_pending_approvals(self) -> list[ApprovalRequest]:
        return [req for req in self.approvals.values() if req.status == ApprovalStatus.PENDING]

    def update_approval_status(
        self, request_id: str, approved: bool, reviewer: str, comment: str
    ) -> bool:
        req = self.approvals.get(request_id)
        if not req:
            return False

        req.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        req.reviewed_by = reviewer
        req.review_comment = comment
        req.reviewed_at = datetime.now(UTC)
        return True
