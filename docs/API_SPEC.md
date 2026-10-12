# 🔌 REST API Specification & Endpoint Documentation

The AI Employee exposes a RESTful API built on **FastAPI**. Interactive Swagger UI documentation is accessible at `http://localhost:8000/docs`.

---

## 1. Web Portals & UI Views

* **`GET /`**
  - **Description**: Serves the executive commercial landing page featuring the interactive ROI Calculator.
  - **Response**: HTML5 web application.

* **`GET /dashboard`**
  - **Description**: Serves the live Executive Command Center dashboard with real-time test drive simulator, HITL approval queue, and synced Notion CRM records.
  - **Response**: HTML5 interactive application.

* **`GET /health`**
  - **Description**: Verifies API liveness and active adapter operational modes.
  - **Response (200 OK)**:
    ```json
    {
      "status": "healthy",
      "app_name": "AI Employee & Business Automation",
      "environment": "development",
      "email_mode": "mock",
      "crm_mode": "mock"
    }
    ```

---

## 2. Agent Operations (`/api/v1/agent`)

* **`POST /api/v1/agent/process-email`**
  - **Description**: Submits an email for automated evaluation, guardrails inspection, and execution.
  - **Request Body**:
    ```json
    {
      "sender": "sarah.connor@clientcorp.com",
      "recipient": "support@company.com",
      "subject": "Request for Custom Enterprise Pricing (500 Seats)",
      "body": "Please provide formal quotation and SLA terms."
    }
    ```
  - **Response (200 OK)**:
    ```json
    {
      "intent": "sales_lead",
      "risk_level": "high",
      "requires_approval": true,
      "drafted_response": "Hello, thank you for your interest...",
      "reasoning": "Commercial policy requires supervisor approval before issuing binding quotes",
      "approval_id": "APPR-97C14A"
    }
    ```

* **`POST /api/v1/agent/batch-inbox-sync?limit=10`**
  - **Description**: Triggers a synchronization cycle fetching unread emails from the connected inbox.

* **`POST /api/v1/agent/daily-digest`**
  - **Description**: Compiles and publishes the daily operational digest to Notion and triggers mobile Telegram notification.

* **`GET /api/v1/agent/stats`**
  - **Description**: Returns live counters for processed communications, created tasks, and autonomous resolution rates.

* **`GET /api/v1/agent/contacts`**
  - **Description**: Returns all synchronized CRM contacts stored in Notion/CRM.

* **`GET /api/v1/agent/tasks`**
  - **Description**: Returns all tracked operational and security tasks stored in Notion/CRM.

* **`GET /api/v1/agent/policies`**
  - **Description**: Returns active corporate SOPs and policy knowledge documents.

---

## 3. Human-in-the-Loop Approvals (`/api/v1/approvals`)

* **`GET /api/v1/approvals`**
  - **Description**: Retrieves all actions currently paused waiting for supervisor review.

* **`POST /api/v1/approvals/{approval_id}/action`**
  - **Description**: Submits an approval or rejection decision.
  - **Request Body**:
    ```json
    {
      "reviewer_name": "Anas AL-Aghbari",
      "approved": true,
      "comment": "Approved with enterprise standard terms."
    }
    ```

---

## 4. Omnichannel WhatsApp Webhooks (`/api/v1/webhooks`)

* **`GET /api/v1/webhooks/whatsapp`**
  - **Description**: Meta Cloud API handshake verification endpoint (`hub.mode`, `hub.challenge`, `hub.verify_token`).

* **`POST /api/v1/webhooks/whatsapp`**
  - **Description**: Ingests incoming WhatsApp customer messages in real-time and executes autonomous resolution.
  - **Request Body**:
    ```json
    {
      "sender": "+1234567890",
      "body": "Hi, what are your business support hours?"
    }
    ```
