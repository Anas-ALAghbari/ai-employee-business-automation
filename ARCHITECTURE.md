# 🏗️ Architecture & Technical Specification: 🧑💼 AI Employee / Business Automation

Developer & AI Architect: **[Anas AL-Aghbari](https://www.linkedin.com/in/anas-al-aghbari-71070440a/)**  
LinkedIn: [anas-al-aghbari-71070440a](https://www.linkedin.com/in/anas-al-aghbari-71070440a/)  
Track: `Phase 2 - Enterprise Automation` | Repository: [ai-employee-business-automation](https://github.com/Anas-ALAghbari/ai-employee-business-automation)

---

## 🎯 Architectural Philosophy

This project adheres to **Hexagonal Architecture (Ports and Adapters)** and **Clean Architecture** principles. Domain logic remains completely framework-agnostic, while communication with external enterprise services (Gmail, Notion, Vector DBs, Redis) is mediated strictly through abstract ports.

```
+-----------------------------------------------------------------------------------+
|                                  API LAYER                                        |
|                     FastAPI REST & Webhooks (/api/v1/)                            |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                          CORE AGENT COGNITIVE ENGINE                              |
|                          (src/agent/brain.py)                                     |
|  - Threat Protection & Prompt Injection Defense (src/core/guardrails.py)          |
|  - Multi-Tier Risk Evaluation (Autonomous vs Human Gating)                        |
|  - Grounded Knowledge Retrieval & Intent Reasoning                                |
+-----------------------------------------------------------------------------------+
             │                                   │                           │
             ▼                                   ▼                           ▼
      [ Email Port ]                       [ CRM Port ]               [ Memory Port ]
   AbstractEmailService                AbstractCRMService         AbstractMemoryService
             │                                   │                           │
      ┌──────┴──────┐                     ┌──────┴──────┐             ┌──────┴──────┐
      ▼             ▼                     ▼             ▼             ▼             ▼
   Gmail API    Mock Adapter           Notion API    Mock Adapter  Vector Store   Audit Log
```

---

## 📦 Module Breakdown

* `src/core/`: Zero-dependency business domain entities (`models.py`), enums (`enums.py`), and safety rules (`guardrails.py`).
* `src/agent/`: Cognitive intelligence engine (`brain.py`) and enterprise prompts (`prompts.py`).
* `src/ports/`: Abstract interfaces establishing contracts for external services (`email_port.py`, `crm_port.py`, `memory_port.py`).
* `src/adapters/`: Vendor implementations for Gmail (`gmail_adapter.py`), Notion CRM (`notion_adapter.py`), and mock fixtures for isolated testing.
* `src/api/`: Production FastAPI application with endpoints for processing communications, human approvals, and daily digests.
* `src/workers/`: Periodic background scheduler (`scheduler.py`) handling inbox polling and digest publication.
* `tests/`: Complete automated test suite covering models, guardrails, agent engine, adapters, and REST endpoints.
* `scripts/`: Interactive demo simulator (`run_demo.py`).

---

## 🔒 Enterprise Security & Safety Guardrails

1. **Adversarial Input Defense**: Real-time regex pattern scanning intercepts prompt injections, jailbreak attempts, and system prompt extraction attacks before the LLM processes them.
2. **PII Masking**: Redaction of payment card data and sensitive identifiers before payload persistence.
3. **Human-in-the-Loop Gating**: Actions involving high financial commitments (quotes, contracts, refunds > $50) are automatically paused in draft mode until authorized by a human supervisor.
4. **Audit Trail**: Every action is stamped with millisecond execution latency and logged for SOC2 compliance.

> For detailed workflow diagrams and sequence charts, refer to [docs/WORKFLOWS.md](file:///c:/Users/Anas-ALaghbari/.gemini/antigravity/scratch/ai-employee-business-automation/docs/WORKFLOWS.md) and [docs/ARCHITECTURE.md](file:///c:/Users/Anas-ALaghbari/.gemini/antigravity/scratch/ai-employee-business-automation/docs/ARCHITECTURE.md).
