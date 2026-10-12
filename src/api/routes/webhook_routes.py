"""
Omnichannel Webhook Router (WhatsApp Business, External Webhooks).
Supports Meta Cloud API verification and real-time customer message ingestion.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse

from src.agent.brain import AIEmployeeEngine
from src.api.deps import get_agent_engine
from src.config import settings
from src.core.models import EmailMessage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/webhooks", tags=["Omnichannel Webhooks"])


@router.get("/whatsapp", response_class=PlainTextResponse)
def verify_whatsapp_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """
    Meta Cloud API Webhook handshake verification.
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        logger.info("WhatsApp webhook verified successfully.")
        return hub_challenge or "VERIFIED"

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Verification token mismatch.",
    )


@router.post("/whatsapp")
def process_incoming_whatsapp_message(
    payload: dict[str, Any],
    engine: AIEmployeeEngine = Depends(get_agent_engine),
):
    """
    Process incoming WhatsApp message payload, normalize, and process through the AI Employee.
    """
    logger.info("Received WhatsApp webhook event: %s", payload)

    # Extract sender and text from standard Meta Cloud API format or generic payload
    sender = "whatsapp_user"
    body = ""

    # Parse standard Meta Cloud API structure if present
    try:
        entries = payload.get("entry", [])
        if entries:
            changes = entries[0].get("changes", [])
            if changes:
                value = changes[0].get("value", {})
                messages = value.get("messages", [])
                if messages:
                    sender = messages[0].get("from", "whatsapp_user")
                    msg_body = messages[0].get("text", {}).get("body", "")
                    if msg_body:
                        body = msg_body
    except Exception as err:
        logger.warning("Custom WhatsApp format detected: %s", err)

    # Fallback to simple payload structure for testing / custom webhooks
    if not body:
        sender = payload.get("sender") or payload.get("from") or "whatsapp_user"
        body = payload.get("body") or payload.get("message") or payload.get("text") or "Hello"

    # Normalize into EmailMessage structure
    normalized_msg = EmailMessage(
        sender=f"{sender}@whatsapp.net",
        recipient="support@company.com",
        subject="Incoming WhatsApp Communication",
        body=body,
    )

    decision = engine.process_incoming_email(normalized_msg)

    return {
        "status": "processed",
        "channel": "whatsapp",
        "sender": sender,
        "intent": decision.intent.value,
        "requires_approval": decision.requires_approval,
        "reply": decision.drafted_response,
    }
