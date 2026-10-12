# 🧑💼 AI Employee / Business Automation

[![LinkedIn Profile](https://img.shields.io/badge/LinkedIn-Anas%20AL--Aghbari-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/anas-al-aghbari-71070440a/)
[![Notion Connected](https://img.shields.io/badge/Notion-Workspace%20Connected-000000?style=for-the-badge&logo=notion&logoColor=white)](https://www.notion.so)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Tests Passing](https://img.shields.io/badge/Tests-20%2F20%20Passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org/)
[![License: Commercial](https://img.shields.io/badge/License-Commercial-blue?style=for-the-badge)](#-commercial-license--ownership)

**🧑💼 AI Employee / Business Automation** is an enterprise-grade autonomous digital worker designed and engineered by **Anas AL-Aghbari** as part of the **AI Systems & Autonomous Agents Portfolio**.

> **Slogan**: *"Autonomous Digital Worker for Enterprise Workflow Automation"*  
> **Portfolio Track**: `Phase 2 - Enterprise Automation`  
> **Notion Roadmap Track**: `المرحلة 2 | 6. AI Employee / Business Automation`

---

## 📖 Overview & Purpose

Modern enterprises are weighed down by repetitive operational tasks: triaging support tickets, managing customer email inquiries, synchronizing CRM records, and drafting daily status reports.

**AI Employee** acts as an always-on digital team member that:
1. **Monitors & Triages Email**: Ingests incoming emails via Google Workspace or Webhooks, extracts customer intent, redacts sensitive PII, and formulates compliant responses.
2. **Synchronizes Notion CRM**: Automatically registers customer profiles, logs interaction histories, and generates prioritized task cards.
3. **Enforces Human-in-the-Loop (HITL)**: Intelligently identifies high-risk actions (custom quotes, contracts, large refunds) and pauses execution for managerial sign-off.
4. **Shields with Prompt Guardrails**: Defends corporate systems against prompt injection and jailbreak exploits in customer inputs.
5. **Generates Daily Operational Digests**: Automatically summarizes business transactions, autonomous resolution rates, and outstanding items every evening.

---

## 🏗️ System Architecture (Clean / Hexagonal)

```text
                     +---------------------------------------------+
                     |    Incoming Events (Gmail API / Webhooks)   |
                     +---------------------------------------------+
                                            │
                                            ▼
                     +---------------------------------------------+
                     |         AI Employee Cognitive Engine        |
                     |  - Prompt Injection & PII Guardrails        |
                     |  - Multi-Tier Risk Evaluation (LOW/HIGH)    |
                     |  - Corporate Knowledge & SOP Grounding      |
                     +---------------------------------------------+
                                     /             \
                                    ▼               ▼
        +-----------------------------------+     +-----------------------------------+
        |  Memory & Policies Port           |     |  Email & CRM Adapter Ports        |
        |  - Vector Knowledge Store         |     |  - Gmail / Mock Email Service     |
        |  - Audit Log & Traceability       |     |  - Notion CRM / Task Synchronizer |
        +-----------------------------------+     +-----------------------------------+
                                            │
                                            ▼
                     +---------------------------------------------+
                     |   FastAPI Portal & Human Approval Dashboard |
                     |   (/api/v1/approvals & /api/v1/agent)       |
                     +---------------------------------------------+
```

---

## 🛠️ Technology Stack

* **Language**: Python 3.11+ / 3.14
* **Web Framework & REST API**: FastAPI, Uvicorn, Starlette
* **Data Validation & Typing**: Pydantic V2, Pydantic Settings
* **CRM & Workspace**: Notion API (`notion-client`)
* **Email Infrastructure**: Google Workspace Gmail API (`google-api-python-client`)
* **Background Scheduling**: Schedule, Redis
* **Quality & CI/CD**: Pytest, Pytest-Asyncio, Ruff, Docker Compose, GitHub Actions

---

## 🚀 Quickstart & Interactive Simulation

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/Anas-ALAghbari/ai-employee-business-automation.git
cd ai-employee-business-automation

python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run Interactive Simulation Demo

Run the end-to-end multi-scenario simulation runner to see the AI Employee handle FAQs, pause high-risk quotes for human approval, block prompt injections, and generate an executive daily digest:

```bash
python scripts/run_demo.py
```

### 3. Run Automated Tests

Execute the full automated test suite (19 test cases covering models, guardrails, agent brain, adapters, and API endpoints):

```bash
python -m pytest -v
```

### 4. Launch FastAPI REST Server

```bash
uvicorn src.api.main:app --reload --port 8000
```
Visit `http://localhost:8000/docs` to interact with the live Swagger OpenAPI documentation.

### 5. Launch with Docker Compose

```bash
docker-compose up --build
```

---

## 📁 Repository Structure

```text
ai-employee-business-automation/
├── .github/workflows/ci.yml       # Automated GitHub Actions CI pipeline
├── docs/
│   ├── ARCHITECTURE.md            # In-depth architectural specification
│   ├── WORKFLOWS.md               # Visual workflow flowcharts and state diagrams
│   └── API_SPEC.md                # Comprehensive OpenAPI REST documentation
├── src/
│   ├── config.py                  # Strongly typed environment configuration
│   ├── core/                      # Zero-dependency domain models & guardrails
│   │   ├── enums.py               # Intent, RiskLevel, Priority, Status enums
│   │   ├── models.py              # Pydantic entities (Email, Task, Approval)
│   │   └── guardrails.py          # Security engine (Prompt injection & PII filter)
│   ├── agent/
│   │   ├── brain.py               # AI Employee Cognitive Engine
│   │   └── prompts.py             # Enterprise system prompts
│   ├── ports/                     # Abstract interfaces (Email, CRM, Memory)
│   ├── adapters/                  # Swappable vendor adapters (Gmail, Notion, Mock)
│   ├── api/                       # FastAPI application & REST route controllers
│   └── workers/                   # Background polling and daily digest scheduler
├── tests/                         # Full automated unit & integration test suite
├── scripts/
│   └── run_demo.py                # Colorized interactive simulation runner
├── docker-compose.yml             # Multi-container orchestration (API + Worker + Redis)
├── Dockerfile                     # Production container specification
├── pyproject.toml                 # Build system, pytest, and ruff linter configuration
└── requirements.txt               # Dependency manifest
```

---

## 👨‍💻 Developer & Portfolio Credits

* **Developer & AI Architect**: **[Anas AL-Aghbari](https://www.linkedin.com/in/anas-al-aghbari-71070440a/)** 🚀
* **LinkedIn Profile**: [anas-al-aghbari-71070440a](https://www.linkedin.com/in/anas-al-aghbari-71070440a/)
* **Portfolio Track**: AI Systems, RAG, MCP & Multi-Agent Swarms

---

## 🔒 Commercial License & Ownership

Copyright © 2026 **[Anas AL-Aghbari](https://www.linkedin.com/in/anas-al-aghbari-71070440a/)**. All Rights Reserved.  
Proprietary & Commercial Software License.
