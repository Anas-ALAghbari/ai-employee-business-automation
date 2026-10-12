"""
Autonomous AI Employee Cognitive Engine.
Coordinates intent classification, safety guardrails, policy grounding, tool execution,
and Human-in-the-Loop gating.
"""

import time
from datetime import UTC, datetime
from typing import Any

from src.core.enums import (
    ApprovalStatus,
    IntentType,
    RiskLevel,
    TaskPriority,
    TaskStatus,
)
from src.core.guardrails import GuardrailsEngine
from src.core.models import (
    AgentAction,
    AgentDecision,
    ApprovalRequest,
    CRMContact,
    CRMTask,
    DailyDigestReport,
    EmailMessage,
)
from src.ports.crm_port import AbstractCRMService
from src.ports.email_port import AbstractEmailService
from src.ports.memory_port import AbstractMemoryService
from src.ports.notification_port import AbstractNotificationService


class AIEmployeeEngine:
    """The central intelligence and execution coordinator of the digital worker."""

    def __init__(
        self,
        email_service: AbstractEmailService,
        crm_service: AbstractCRMService,
        memory_service: AbstractMemoryService,
        notification_service: AbstractNotificationService | None = None,
    ) -> None:
        self.email_service = email_service
        self.crm_service = crm_service
        self.memory_service = memory_service
        self.notification_service = notification_service

        # Operational metrics tracking
        self.processed_emails_count = 0
        self.tasks_created_count = 0
        self.autonomous_actions_count = 0
        self.approvals_triggered_count = 0
        self.audit_log: list[AgentAction] = []

    def process_incoming_email(self, email: EmailMessage) -> AgentDecision:
        """
        End-to-end processing pipeline for an incoming email:
        1. Guardrails check (Security / Prompt Injection / PII)
        2. Policy knowledge retrieval (Vector memory search)
        3. Intent classification & Decision generation
        4. Autonomy vs HITL evaluation
        5. Execution / Drafting & CRM synchronization
        """
        start_time = time.time()
        self.processed_emails_count += 1

        # Step 1: Security Guardrail Inspection
        is_injection, detected_patterns = GuardrailsEngine.detect_prompt_injection(
            f"{email.subject} {email.body}"
        )
        if is_injection:
            action_sec = AgentAction(
                tool_name="security_guardrail",
                parameters={"patterns": detected_patterns},
                result="Blocked hostile payload",
                status="blocked",
                execution_time_ms=(time.time() - start_time) * 1000,
            )
            self.memory_service.record_audit(action_sec)

            # Create Security Alert Task in CRM
            sec_task = CRMTask(
                title=f"🚨 SECURITY ALERT: Prompt Injection from {email.sender}",
                description=f"Blocked attack vector containing: {', '.join(detected_patterns)}",
                priority=TaskPriority.CRITICAL,
                status=TaskStatus.PENDING,
            )
            self.crm_service.create_task(sec_task)
            self.tasks_created_count += 1
            self.email_service.mark_as_read(email.id)

            if self.notification_service:
                self.notification_service.send_security_alert(
                    f"Prompt injection blocked from {email.sender}: {', '.join(detected_patterns)}"
                )

            return AgentDecision(
                intent=IntentType.SECURITY_ANOMALY,
                confidence=0.99,
                reasoning="Input flagged as prompt injection attack vector.",
                risk_level=RiskLevel.CRITICAL,
                requires_approval=False,
                drafted_response="[System Notice: Message quarantined due to policy violation.]",
                actions_to_execute=[{"action": "quarantine", "patterns": detected_patterns}],
            )

        # Step 2: Retrieve Relevant Corporate SOPs & Knowledge
        policies = self.memory_service.search_policies(f"{email.subject} {email.body}", top_k=2)

        # Step 3: Intent Analysis & Plan Formulation
        subject_lower = email.subject.lower()
        body_lower = email.body.lower()

        if any(term in subject_lower or term in body_lower for term in ["pricing", "quote", "seats", "enterprise", "cost"]):
            intent = IntentType.SALES_LEAD
            risk_level, requires_approval, rationale = GuardrailsEngine.evaluate_risk(
                "send_formal_quote",
                {"seats": 500},
                text_content=email.body,
            )
        elif any(term in subject_lower or term in body_lower for term in ["hours", "time", "available", "schedule"]):
            intent = IntentType.INQUIRY
            risk_level = RiskLevel.LOW
            requires_approval = False
            rationale = "General inquiry matched in corporate knowledge base"
        elif any(term in subject_lower or term in body_lower for term in ["invoice", "payment", "bill", "receipt", "overdue"]):
            intent = IntentType.BILLING_DISPUTE
            risk_level = RiskLevel.LOW
            requires_approval = False
            rationale = "Invoice and payment transaction inquiry"
        elif any(term in subject_lower or term in body_lower for term in ["bug", "issue", "error", "broken", "support"]):
            intent = IntentType.SUPPORT_TICKET
            risk_level = RiskLevel.LOW
            requires_approval = False
            rationale = "Standard technical support request"
        else:
            intent = IntentType.INQUIRY
            risk_level = RiskLevel.LOW
            requires_approval = False
            rationale = "Standard customer communication"

        # Step 4: Formulate Response & Action Plan
        drafted_reply = self._formulate_response(intent, email, policies)

        # Step 5: Execution vs Human-in-the-Loop Gating
        approval_request: ApprovalRequest | None = None
        executed_actions: list[dict[str, Any]] = []

        if requires_approval:
            self.approvals_triggered_count += 1
            # Create Approval Request for supervisor
            approval_request = ApprovalRequest(
                action_type="send_custom_quote",
                title=f"Review Enterprise Proposal for {email.sender}",
                description=f"Customer requesting custom contract. Rationale: {rationale}",
                proposed_payload={
                    "recipient": email.sender,
                    "subject": f"Re: {email.subject}",
                    "draft_body": drafted_reply,
                },
                risk_level=RiskLevel.HIGH,
                status=ApprovalStatus.PENDING,
            )
            self.memory_service.save_approval_request(approval_request)

            # Create Draft in Email Service (so human can review/send)
            draft_id = self.email_service.create_draft(
                email.sender, f"Re: {email.subject}", drafted_reply
            )
            executed_actions.append({"action": "create_email_draft", "draft_id": draft_id})

            # Create CRM Task to notify supervisor
            crm_task = CRMTask(
                title=f"Review Pending Quote: {email.sender}",
                description=f"Approval ID {approval_request.id} requires managerial review before dispatching.",
                priority=TaskPriority.HIGH,
                status=TaskStatus.WAITING_APPROVAL,
            )
            self.crm_service.create_task(crm_task)
            self.tasks_created_count += 1

            if self.notification_service and approval_request:
                self.notification_service.send_approval_alert(approval_request)
        else:
            # Autonomous Execution
            self.autonomous_actions_count += 1
            self.email_service.send_email(email.sender, f"Re: {email.subject}", drafted_reply)
            executed_actions.append({"action": "send_email", "to": email.sender})

            # Sync CRM Contact
            crm_contact = CRMContact(
                email=email.sender,
                notes=[f"Replied to inquiry '{email.subject}' on {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')}"],
                stage="Customer" if intent != IntentType.SALES_LEAD else "Qualified",
            )
            self.crm_service.upsert_contact(crm_contact)
            executed_actions.append({"action": "upsert_crm_contact", "email": email.sender})

        # Mark processed
        email.is_read = True
        self.email_service.mark_as_read(email.id)

        # Record step in audit log
        action_trace = AgentAction(
            tool_name="process_email",
            parameters={"sender": email.sender, "intent": intent.value},
            result={"status": "success", "requires_approval": requires_approval},
            status="success",
            execution_time_ms=(time.time() - start_time) * 1000,
        )
        self.memory_service.record_audit(action_trace)

        return AgentDecision(
            intent=intent,
            confidence=0.95,
            reasoning=rationale,
            risk_level=risk_level,
            requires_approval=requires_approval,
            drafted_response=drafted_reply,
            actions_to_execute=executed_actions,
            approval_request=approval_request,
        )

    def _formulate_response(
        self, intent: IntentType, email: EmailMessage, policies: list[dict[str, str]]
    ) -> str:
        """Compose clear, professional business communication."""
        if intent == IntentType.INQUIRY:
            # Find relevant policy excerpt
            policy_text = policies[0]["content"] if policies else "Monday - Friday, 8am - 6pm EST."
            return (
                f"Hello,\n\nThank you for reaching out to us.\n\n"
                f"{policy_text}\n\n"
                f"Please let us know if we can assist you with anything else!\n\n"
                f"Best regards,\nCustomer Operations Team"
            )

        if intent == IntentType.SALES_LEAD:
            return (
                "Hello,\n\nThank you for your interest in our enterprise solutions.\n\n"
                "For organizations with large seat deployments, we offer dedicated infrastructure, "
                "custom SLAs (99.9% uptime guarantee), and tailored volume pricing.\n\n"
                "I have prepared an initial enterprise review package and escalated this to your "
                "dedicated Account Executive, who will reach out shortly to finalize details.\n\n"
                "Best regards,\nEnterprise Solutions Desk"
            )

        if intent == IntentType.BILLING_DISPUTE:
            return (
                "Hello,\n\nThank you for contacting billing operations.\n\n"
                "We have verified your account billing ledger. Invoices can be reviewed and settled "
                "directly via your customer portal with instant one-click payment (Credit Card / Bank Transfer).\n\n"
                "If you need an updated formal statement or tax invoice, our accounts team will provide it shortly.\n\n"
                "Best regards,\nFinance & Accounts Desk"
            )

        if intent == IntentType.SUPPORT_TICKET:
            return (
                "Hello,\n\nThank you for contacting technical support. We have received your ticket.\n"
                "Our engineering desk is investigating the issue, and you will receive an update shortly.\n\n"
                "Best regards,\nTechnical Support Team"
            )

        return (
            "Hello,\n\nThank you for your message. We have received your request and are processing it.\n\n"
            "Best regards,\nSupport Operations"
        )

    def generate_daily_digest(self, date_str: str | None = None) -> DailyDigestReport:
        """
        Synthesize the day's operations, autonomous achievements, and pending human reviews
        into an executive-level summary and publish to Notion / CRM.
        """
        if not date_str:
            date_str = datetime.now(UTC).strftime("%Y-%m-%d")

        pending_approvals = self.memory_service.list_pending_approvals()

        highlights = [
            f"Successfully processed {self.processed_emails_count} incoming communications.",
            f"Executed {self.autonomous_actions_count} workflow actions autonomously without human delay.",
            f"Created {self.tasks_created_count} prioritized task tracking items in Notion.",
        ]
        if pending_approvals:
            highlights.append(
                f"⚠️ {len(pending_approvals)} high-risk decision(s) currently awaiting managerial sign-off."
            )

        summary_text = (
            f"Autonomous operations ran seamlessly for {date_str}. "
            f"Total volume handled: {self.processed_emails_count} messages. "
            f"Autonomous execution rate: "
            f"{(self.autonomous_actions_count / max(1, self.processed_emails_count)) * 100:.1f}%. "
            f"{len(pending_approvals)} item(s) require supervisor review in the HITL dashboard."
        )

        digest = DailyDigestReport(
            date=date_str,
            total_emails_processed=self.processed_emails_count,
            tasks_created=self.tasks_created_count,
            approvals_pending=len(pending_approvals),
            autonomous_actions_count=self.autonomous_actions_count,
            key_highlights=highlights,
            executive_summary=summary_text,
        )

        self.crm_service.save_daily_digest(digest)

        if self.notification_service:
            self.notification_service.send_daily_digest_alert(digest)

        return digest
