# 🏗️ Enterprise Architecture & Technical Specification

**Developer & AI Architect**: **[Anas AL-Aghbari](https://www.linkedin.com/in/anas-al-aghbari-71070440a/)**  
**Portfolio Track**: `Phase 2 - Enterprise Automation`  
**Repository**: [ai-employee-business-automation](https://github.com/Anas-ALAghbari/ai-employee-business-automation)

---

## 1. Architectural Philosophy: Clean & Hexagonal Architecture

The system is structured according to **Hexagonal Architecture (Ports and Adapters)** to guarantee strict decoupling of business domain logic from external vendors (Notion, Google Workspace, LLM APIs).

```
 +-------------------------------------------------------------------------+
 |                                  API                                    |
 |           FastAPI Endpoints (REST, Webhooks, HITL Portal)               |
 +-------------------------------------------------------------------------+
                                      │
                                      ▼
 +-------------------------------------------------------------------------+
 |                          APPLICATION CORE                               |
 |     AI Employee Cognitive Engine (src/agent/brain.py)                   |
 |     - Security Guardrails & Prompt Injection Detection                  |
 |     - Multi-tier Risk Assessment (Autonomy vs Human Gating)             |
 |     - ReAct Reasoning & Decision Formulation                            |
 +-------------------------------------------------------------------------+
             │                                │                     │
             ▼                                ▼                     ▼
     [ Email Port ]                    [ CRM Port ]          [ Memory Port ]
     AbstractEmailService              AbstractCRMService    AbstractMemoryService
             │                                │                     │
      ┌──────┴──────┐                  ┌──────┴──────┐       ┌──────┴──────┐
      ▼             ▼                  ▼             ▼       ▼             ▼
  GmailAPI     MockEmail           NotionAPI     MockCRM   Qdrant/Vector  AuditLog
```

### Dependency Rule
* Inner domain layers (`src/core/`) have **zero dependencies** on external frameworks or databases.
* Ports (`src/ports/`) define abstract interfaces.
* Adapters (`src/adapters/`) implement the ports and can be swapped seamlessly between live production vendors (Gmail, Notion) and isolated testing environments (Mock adapters).

---

## 2. Autonomy Tiers & Risk Gating (Human-in-the-Loop)

To prevent uncontrolled AI actions in enterprise environments, actions are categorized into 4 risk tiers:

| Risk Tier | Autonomous Execution | Example Actions | Safety Mechanism |
| :--- | :---: | :--- | :--- |
| **LOW** | ✅ Allowed | Answering FAQs, business hours inquiries, logging contacts, creating draft notes. | Executed immediately; logged in audit trail. |
| **MEDIUM** | ✅ Allowed with Alert | Creating support tickets, updating lead statuses, non-binding trial assistance. | Executed immediately; notification sent to team. |
| **HIGH** | ⏸️ Paused (HITL) | Custom commercial quotes, issuing contracts, refunds exceeding threshold ($50). | Paused; draft created; approval card registered in Notion / HITL dashboard. |
| **CRITICAL** | 🛑 Blocked | Prompt injection payloads, credential harvesting, bulk record deletions. | Quarantined; blocked; critical incident alert dispatched to security team. |

---

## 3. Data & Entity Models

* **`EmailMessage`**: Normalized email entity containing sender, recipient, subject, sanitized body, and timestamp.
* **`CRMContact`**: Customer or lead identity containing historical contact logs, deal stage, and company affiliation.
* **`CRMTask`**: Prioritized work item created in Notion or CRM with status, urgency, and assignee.
* **`ApprovalRequest`**: A paused action requiring human manager sign-off before dispatch.
* **`DailyDigestReport`**: End-of-day operational summary summarizing volume, autonomous execution rates, and pending items.

---

## 4. Observability & Auditability

* Every decision step emits an `AgentAction` trace with millisecond execution latency and status.
* Audit records are stored in memory and can be exported for enterprise compliance reviews (SOC2 / ISO 27001).
