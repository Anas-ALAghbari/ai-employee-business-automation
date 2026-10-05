"""
Enterprise Guardrails & Security Module.
Provides prompt-injection defense, PII masking, and action-risk classification.
"""

import re

from src.config import settings
from src.core.enums import RiskLevel


class GuardrailsEngine:
    """Security and safety engine protecting the AI Employee system."""

    # Known prompt injection signatures
    INJECTION_PATTERNS = [
        r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
        r"(?i)disregard\s+(all\s+)?(previous|prior)\s+rules",
        r"(?i)system\s+prompt\s*(reveal|show|dump|print)",
        r"(?i)you\s+are\s+now\s+in\s+developer\s+mode",
        r"(?i)jailbreak",
        r"(?i)override\s+(all\s+)?safeguards",
        r"(?i)<\|im_start\|>",
        r"(?i)\[system\]",
        r"(?i)act\s+as\s+an\s+unrestricted\s+ai",
    ]

    # Sensitive PII patterns
    CREDIT_CARD_REGEX = r"\b(?:\d{4}[ -]?){3}\d{4}\b"
    EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

    @classmethod
    def detect_prompt_injection(cls, text: str) -> tuple[bool, list[str]]:
        """
        Scans input text for potential prompt injection and adversarial manipulation attempts.
        Returns (is_compromised, list_of_detected_patterns).
        """
        detected: list[str] = []
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, text):
                detected.append(pattern)

        return (len(detected) > 0, detected)

    @classmethod
    def sanitize_input(cls, text: str) -> str:
        """
        Masks highly sensitive data such as credit cards before sending to LLM.
        """
        # Redact Credit Cards
        sanitized = re.sub(cls.CREDIT_CARD_REGEX, "[REDACTED_CARD_NUMBER]", text)
        return sanitized

    @classmethod
    def evaluate_risk(
        cls,
        action_type: str,
        payload: dict[str, any],
        text_content: str = ""
    ) -> tuple[RiskLevel, bool, str]:
        """
        Evaluates the operational risk tier of a planned action.
        Returns (RiskLevel, requires_human_approval, rationale).
        """
        # 1. First check if prompt injection was detected in the context
        is_injection, patterns = cls.detect_prompt_injection(text_content)
        if is_injection:
            return (
                RiskLevel.CRITICAL,
                True,
                f"Blocked potential prompt injection attempt: {patterns}"
            )

        # 2. Financial transactions: Refunds
        if action_type in ("issue_refund", "process_refund"):
            amount = float(payload.get("amount", 0.0))
            if amount > settings.max_refund_limit:
                return (
                    RiskLevel.HIGH,
                    True,
                    f"Refund amount ${amount:.2f} exceeds autonomous threshold of ${settings.max_refund_limit:.2f}"
                )
            return (RiskLevel.LOW, False, "Refund within approved autonomous threshold")

        # 3. Financial transactions: Quotes & Contracts
        if action_type in ("send_formal_quote", "issue_contract", "create_custom_pricing"):
            if settings.require_approval_for_quotes:
                return (
                    RiskLevel.HIGH,
                    True,
                    "Commercial policy requires supervisor approval before issuing binding quotes"
                )

        # 4. Critical CRM operations: Deletions
        if action_type in ("delete_customer", "wipe_database"):
            return (
                RiskLevel.HIGH,
                True,
                "Destructive operations strictly require human approval"
            )

        # Default low-risk actions (standard FAQs, draft emails, creating tasks)
        return (RiskLevel.LOW, False, "Action qualifies for autonomous execution")
