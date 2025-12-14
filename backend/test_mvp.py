"""
Minimal tests for MVP API
Run: pytest test_mvp.py
"""
import pytest
from fastapi.testclient import TestClient
import json
import io
from mvp_api import app

client = TestClient(app)

def test_upload_validates_limit():
    """Test that upload enforces 50 lead limit"""
    # Create CSV with 51 leads
    csv_content = "name,email\n"
    for i in range(51):
        csv_content += f"Lead {i},lead{i}@example.com\n"

    files = {"file": ("leads.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    response = client.post("/api/mvp/leads/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] == False
    assert "limit exceeded" in data["error"].lower()
    assert data["accepted_count"] == 0

def test_upload_accepts_valid_csv():
    """Test that upload accepts valid CSV under limit"""
    csv_content = "name,email\nJohn Doe,john@example.com\nJane Smith,jane@example.com\n"

    files = {"file": ("leads.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    response = client.post("/api/mvp/leads/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["accepted_count"] == 2
    assert "batch_id" in data

def test_report_returns_correct_counters():
    """Test that report calculates metrics correctly"""
    # First upload leads
    csv_content = "name,email\nTest User,test@example.com\n"
    files = {"file": ("leads.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    upload_res = client.post("/api/mvp/leads/upload", files=files)
    batch_id = upload_res.json()["batch_id"]

    # Get report
    response = client.get(f"/api/mvp/batches/{batch_id}/report")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["report"]["leads_contacted"] == 1
    assert data["report"]["replies_received"] == 0
    assert data["report"]["total_fee_gbp"] == 0.0

def test_revival_start_generates_messages():
    """Test that revival generates opener messages"""
    # Upload first
    csv_content = "name,email\nAlice,alice@example.com\n"
    files = {"file": ("leads.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    upload_res = client.post("/api/mvp/leads/upload", files=files)
    batch_id = upload_res.json()["batch_id"]

    # Start revival
    payload = {
        "batch_id": batch_id,
        "business_type": "generic",
        "sender_name": "Bob",
        "company_name": "TestCo"
    }
    response = client.post("/api/mvp/revival/start", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["messages_generated"] == 1
    assert data["dry_run"] == True
    assert len(data["sample_messages"]) == 1

def test_reply_classification():
    """Test reply classification logic"""
    payload = {
        "lead_email": "test@example.com",
        "message_text": "Yes, I'm interested. Send me pricing info."
    }
    response = client.post("/api/mvp/replies/ingest", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["classification"] == "interested"
    assert data["next_action"] in ["send_qualifier", "send_booking"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
