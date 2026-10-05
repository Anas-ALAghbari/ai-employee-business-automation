"""
Agent Operations REST Router.
"""

from typing import Any

from fastapi import APIRouter, Depends

from src.agent.brain import AIEmployeeEngine
from src.api.deps import get_agent_engine
from src.api.schemas import (
    DailyDigestResponse,
    DailyDigestTriggerRequest,
    EmailProcessRequest,
    ProcessEmailResponse,
)
from src.core.models import EmailMessage

router = APIRouter(prefix="/api/v1/agent", tags=["AI Employee Operations"])


@router.post("/process-email", response_model=ProcessEmailResponse)
def process_single_email(
    payload: EmailProcessRequest,
    engine: AIEmployeeEngine = Depends(get_agent_engine),
) -> ProcessEmailResponse:
    """Process an individual customer or lead email message through the agent."""
    msg = EmailMessage(
        sender=payload.sender,
        recipient=payload.recipient,
        subject=payload.subject,
        body=payload.body,
    )
    decision = engine.process_incoming_email(msg)

    return ProcessEmailResponse(
        intent=decision.intent,
        risk_level=decision.risk_level,
        requires_approval=decision.requires_approval,
        drafted_response=decision.drafted_response,
        reasoning=decision.reasoning,
        approval_id=decision.approval_request.id if decision.approval_request else None,
    )


@router.post("/batch-inbox-sync")
def sync_unread_inbox(
    limit: int = 10,
    engine: AIEmployeeEngine = Depends(get_agent_engine),
) -> dict[str, Any]:
    """Poll unread messages from configured mailbox and process autonomously."""
    unread = engine.email_service.fetch_unread_messages(limit=limit)
    processed_count = 0
    results = []

    for msg in unread:
        decision = engine.process_incoming_email(msg)
        results.append({
            "message_id": msg.id,
            "sender": msg.sender,
            "subject": msg.subject,
            "intent": decision.intent.value,
            "requires_approval": decision.requires_approval,
        })
        processed_count += 1

    return {
        "status": "success",
        "processed_count": processed_count,
        "items": results,
    }


@router.post("/daily-digest", response_model=DailyDigestResponse)
def trigger_daily_digest(
    payload: DailyDigestTriggerRequest | None = None,
    engine: AIEmployeeEngine = Depends(get_agent_engine),
) -> DailyDigestResponse:
    """Synthesize operations into the Executive Daily Digest and publish to CRM."""
    req_payload = payload or DailyDigestTriggerRequest()
    digest = engine.generate_daily_digest(date_str=req_payload.date)
    return DailyDigestResponse(
        date=digest.date,
        total_emails_processed=digest.total_emails_processed,
        tasks_created=digest.tasks_created,
        approvals_pending=digest.approvals_pending,
        autonomous_actions_count=digest.autonomous_actions_count,
        executive_summary=digest.executive_summary,
        key_highlights=digest.key_highlights,
    )


@router.get("/stats")
def get_operational_stats(
    engine: AIEmployeeEngine = Depends(get_agent_engine),
) -> dict[str, Any]:
    """Retrieve live metrics on messages processed and autonomous execution rates."""
    return {
        "processed_emails_count": engine.processed_emails_count,
        "tasks_created_count": engine.tasks_created_count,
        "autonomous_actions_count": engine.autonomous_actions_count,
        "approvals_triggered_count": engine.approvals_triggered_count,
    }
