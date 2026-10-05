"""
Human-in-the-Loop (HITL) Approvals REST Router.
Allows human managers to review, sign off on, or reject high-risk agent recommendations.
"""


from fastapi import APIRouter, Depends, HTTPException, status

from src.agent.brain import AIEmployeeEngine
from src.api.deps import get_agent_engine
from src.api.schemas import ApprovalActionRequest, ApprovalItemResponse

router = APIRouter(prefix="/api/v1/approvals", tags=["Human-in-the-Loop Approvals"])


@router.get("", response_model=list[ApprovalItemResponse])
def list_pending_approvals(
    engine: AIEmployeeEngine = Depends(get_agent_engine),
) -> list[ApprovalItemResponse]:
    """Retrieve all actions currently paused waiting for human supervisor sign-off."""
    pending_items = engine.memory_service.list_pending_approvals()
    return [
        ApprovalItemResponse(
            id=item.id,
            action_type=item.action_type,
            title=item.title,
            description=item.description,
            proposed_payload=item.proposed_payload,
            risk_level=item.risk_level,
            status=item.status,
        )
        for item in pending_items
    ]


@router.post("/{approval_id}/action")
def execute_human_approval_decision(
    approval_id: str,
    payload: ApprovalActionRequest,
    engine: AIEmployeeEngine = Depends(get_agent_engine),
):
    """Submit human review decision (Approve or Reject)."""
    req = engine.memory_service.get_approval_request(approval_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approval request {approval_id} not found.",
        )

    success = engine.memory_service.update_approval_status(
        request_id=approval_id,
        approved=payload.approved,
        reviewer=payload.reviewer_name,
        comment=payload.comment or "",
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update approval status.",
        )

    # If approved, dispatch the originally proposed action!
    if payload.approved:
        if req.action_type == "send_custom_quote":
            recipient = req.proposed_payload.get("recipient", "")
            subject = req.proposed_payload.get("subject", "")
            body = req.proposed_payload.get("draft_body", "")
            engine.email_service.send_email(recipient, subject, body)

    return {
        "status": "success",
        "approval_id": approval_id,
        "decision": "APPROVED" if payload.approved else "REJECTED",
        "reviewer": payload.reviewer_name,
        "dispatched": payload.approved,
    }
