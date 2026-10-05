"""
API Integration tests using FastAPI TestClient.
"""

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "email_mode" in data


def test_process_single_email_api():
    payload = {
        "sender": "visitor@acme.org",
        "recipient": "support@company.com",
        "subject": "Question regarding support availability hours",
        "body": "Can someone help me know when your phone support operates?",
    }
    response = client.post("/api/v1/agent/process-email", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "general_inquiry"
    assert data["risk_level"] == "low"
    assert data["requires_approval"] is False
    assert data["drafted_response"] is not None


def test_batch_inbox_sync_api():
    response = client.post("/api/v1/agent/batch-inbox-sync?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "processed_count" in data


def test_daily_digest_api():
    response = client.post("/api/v1/agent/daily-digest", json={"date": "2026-10-05"})
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == "2026-10-05"
    assert "executive_summary" in data


def test_approvals_api():
    # 1. Trigger high-risk request to generate approval
    payload = {
        "sender": "corp@bigclient.com",
        "subject": "Enterprise Quote 1000 seats",
        "body": "Please provide pricing and quote for 1000 enterprise seats.",
    }
    proc_res = client.post("/api/v1/agent/process-email", json=payload)
    assert proc_res.status_code == 200
    approval_id = proc_res.json().get("approval_id")
    assert approval_id is not None

    # 2. List pending approvals
    list_res = client.get("/api/v1/approvals")
    assert list_res.status_code == 200
    items = list_res.json()
    assert any(i["id"] == approval_id for i in items)

    # 3. Approve via HITL endpoint
    action_payload = {
        "reviewer_name": "Anas AL-Aghbari",
        "approved": True,
        "comment": "Approved enterprise proposal.",
    }
    act_res = client.post(f"/api/v1/approvals/{approval_id}/action", json=action_payload)
    assert act_res.status_code == 200
    assert act_res.json()["decision"] == "APPROVED"
