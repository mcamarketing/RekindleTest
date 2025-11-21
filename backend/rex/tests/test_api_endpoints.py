"""
Unit tests for Rex API endpoints

Tests all FastAPI routes with mocked database and Redis dependencies.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import uuid

from backend.rex.app import app
from backend.rex.api_models import MissionTypeEnum, MissionStateEnum


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def mock_supabase():
    """Mock Supabase client"""
    mock = Mock()

    # Mock table() method to return a chainable query builder
    mock_table = Mock()
    mock_table.insert = Mock(return_value=mock_table)
    mock_table.select = Mock(return_value=mock_table)
    mock_table.update = Mock(return_value=mock_table)
    mock_table.eq = Mock(return_value=mock_table)
    mock_table.gte = Mock(return_value=mock_table)
    mock_table.is_ = Mock(return_value=mock_table)
    mock_table.or_ = Mock(return_value=mock_table)
    mock_table.order = Mock(return_value=mock_table)
    mock_table.limit = Mock(return_value=mock_table)
    mock_table.single = Mock(return_value=mock_table)
    mock_table.rpc = Mock(return_value=mock_table)
    mock_table.execute = Mock()

    mock.table = Mock(return_value=mock_table)
    mock.rpc = Mock(return_value=mock_table)

    return mock


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    mock = AsyncMock()
    mock.ping = AsyncMock(return_value=True)
    mock.publish = AsyncMock(return_value=1)
    return mock


@pytest.fixture
def sample_mission_id():
    """Sample UUID for missions"""
    return str(uuid.uuid4())


@pytest.fixture
def sample_user_id():
    """Sample UUID for users"""
    return str(uuid.uuid4())


# ============================================================================
# HEALTH CHECK TESTS
# ============================================================================

def test_root_endpoint(client):
    """Test root endpoint returns service info"""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "REX Orchestration API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "operational"


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_ping(client):
    """Test ping endpoint"""
    response = client.get("/ping")

    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}


# ============================================================================
# REX COMMAND TESTS
# ============================================================================

@patch("backend.rex.api_endpoints.get_supabase_client")
def test_create_mission_success(mock_get_db, client, sample_mission_id, sample_user_id, mock_supabase):
    """Test successful mission creation"""
    mock_get_db.return_value = mock_supabase

    # Mock database insert response
    mock_supabase.table().execute.return_value.data = [{
        "id": sample_mission_id,
        "user_id": sample_user_id,
        "type": "lead_reactivation",
        "state": "queued",
        "priority": 75,
        "created_at": datetime.utcnow().isoformat(),
    }]

    request_data = {
        "user_id": sample_user_id,
        "type": "lead_reactivation",
        "priority": 75,
        "campaign_id": "campaign_123",
        "lead_ids": ["lead_1", "lead_2"],
    }

    response = client.post("/rex/command", json=request_data)

    assert response.status_code == 201
    data = response.json()
    assert data["mission_id"] == sample_mission_id
    assert data["state"] == "queued"
    assert "estimated_completion_time" in data
    assert "message" in data


@patch("backend.rex.api_endpoints.get_supabase_client")
def test_create_mission_validation_error(mock_get_db, client):
    """Test mission creation with invalid data"""
    mock_get_db.return_value = Mock()

    # Missing required field: user_id
    request_data = {
        "type": "lead_reactivation",
    }

    response = client.post("/rex/command", json=request_data)

    assert response.status_code == 422  # Validation error


@patch("backend.rex.api_endpoints.get_supabase_client")
def test_get_mission_status(mock_get_db, client, sample_mission_id, mock_supabase):
    """Test fetching mission status"""
    mock_get_db.return_value = mock_supabase

    # Mock database select response
    mock_supabase.table().execute.return_value.data = [{
        "id": sample_mission_id,
        "state": "executing",
        "created_at": datetime.utcnow().isoformat(),
        "assigned_at": datetime.utcnow().isoformat(),
        "started_at": datetime.utcnow().isoformat(),
        "assigned_crew": "ReviverCrew",
    }]

    response = client.get(f"/rex/command/{sample_mission_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["mission_id"] == sample_mission_id
    assert data["state"] == "executing"
    assert data["progress"] == 0.3  # executing state = 30% progress


@patch("backend.rex.api_endpoints.get_supabase_client")
def test_get_mission_status_not_found(mock_get_db, client, mock_supabase):
    """Test fetching non-existent mission"""
    mock_get_db.return_value = mock_supabase

    # Mock empty response
    mock_supabase.table().execute.return_value.data = []

    response = client.get("/rex/command/nonexistent-id")

    assert response.status_code == 404


@patch("backend.rex.api_endpoints.get_supabase_client")
def test_cancel_mission(mock_get_db, client, sample_mission_id, mock_supabase):
    """Test mission cancellation"""
    mock_get_db.return_value = mock_supabase

    # Mock mission fetch
    mock_supabase.table().select().eq().execute.return_value.data = [{
        "id": sample_mission_id,
        "state": "executing",
    }]

    # Mock update
    mock_supabase.table().update().eq().execute.return_value.data = [{
        "id": sample_mission_id,
        "state": "failed",
    }]

    request_data = {
        "mission_id": sample_mission_id,
        "reason": "User requested cancellation",
    }

    response = client.post(f"/rex/command/{sample_mission_id}/cancel", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["mission_id"] == sample_mission_id
    assert data["cancelled"] is True
    assert data["state"] == "failed"


# ============================================================================
# AGENT WEBHOOK TESTS
# ============================================================================

@patch("backend.rex.api_endpoints.get_redis_client")
@patch("backend.rex.api_endpoints.get_supabase_client")
def test_agent_mission_update(mock_get_db, mock_get_redis, client, sample_mission_id, mock_supabase, mock_redis):
    """Test agent mission update webhook"""
    mock_get_db.return_value = mock_supabase
    mock_get_redis.return_value = mock_redis

    # Mock database insert
    mock_supabase.table().execute.return_value.data = [{}]

    request_data = {
        "mission_id": sample_mission_id,
        "agent_name": "ReviverAgent",
        "event_type": "mission_progress",
        "progress": 0.45,
        "data": {
            "leads_processed": 45,
            "leads_qualified": 12,
        },
    }

    response = client.post("/agents/mission", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["acknowledged"] is True
    assert data["message"] == "Update received successfully"


@patch("backend.rex.api_endpoints.get_supabase_client")
def test_agent_mission_update_invalid_event(mock_get_db, client, sample_mission_id):
    """Test agent update with invalid event type"""
    mock_get_db.return_value = Mock()

    request_data = {
        "mission_id": sample_mission_id,
        "agent_name": "ReviverAgent",
        "event_type": "invalid_event_type",
    }

    response = client.post("/agents/mission", json=request_data)

    assert response.status_code == 422  # Validation error


@patch("backend.rex.api_endpoints.get_supabase_client")
def test_get_agent_status(mock_get_db, client, mock_supabase):
    """Test agent status endpoint"""
    mock_get_db.return_value = mock_supabase

    # Mock RPC call
    mock_supabase.rpc().execute.return_value.data = [
        {
            "agent_name": "ReviverAgent",
            "total_missions": 156,
            "success_rate": 0.94,
            "avg_duration_ms": 45000,
        }
    ]

    response = client.get("/agents/status")

    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert "timestamp" in data


# ============================================================================
# DOMAIN MANAGEMENT TESTS
# ============================================================================

@patch("backend.rex.api_endpoints.get_supabase_client")
def test_allocate_domain(mock_get_db, client, sample_user_id, mock_supabase):
    """Test domain allocation"""
    mock_get_db.return_value = mock_supabase

    domain_id = str(uuid.uuid4())

    # Mock domain query
    mock_supabase.table().execute.return_value.data = [{
        "id": domain_id,
        "domain": "mail.example.com",
        "warmup_state": "warm",
        "reputation_score": 0.92,
        "daily_send_limit": 300,
        "emails_sent_today": 87,
    }]

    request_data = {
        "user_id": sample_user_id,
        "campaign_id": "campaign_123",
        "min_reputation_score": 0.7,
    }

    response = client.post("/domain/assign", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["domain"] == "mail.example.com"
    assert data["domain_id"] == domain_id
    assert data["reputation_score"] == 0.92
    assert data["available_capacity"] == 213


@patch("backend.rex.api_endpoints.get_supabase_client")
def test_allocate_domain_none_available(mock_get_db, client, sample_user_id, mock_supabase):
    """Test domain allocation when no domains available"""
    mock_get_db.return_value = mock_supabase

    # Mock empty response
    mock_supabase.table().execute.return_value.data = []

    request_data = {
        "user_id": sample_user_id,
        "campaign_id": "campaign_123",
    }

    response = client.post("/domain/assign", json=request_data)

    assert response.status_code == 404


@patch("backend.rex.api_endpoints.get_supabase_client")
def test_start_domain_warmup(mock_get_db, client, mock_supabase):
    """Test starting domain warmup"""
    mock_get_db.return_value = mock_supabase

    # Mock RPC call
    mock_supabase.rpc().execute.return_value.data = True

    # Mock domain fetch
    mock_supabase.table().execute.return_value.data = {
        "domain": "new.example.com",
        "warmup_state": "warming",
        "warmup_day": 1,
        "warmup_target_per_day": 5,
        "warmup_schedule": [{"day": 1, "target_emails": 5}],
    }

    request_data = {
        "domain": "new.example.com",
        "user_id": str(uuid.uuid4()),
    }

    response = client.post("/domain/warmup", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["domain"] == "new.example.com"
    assert data["warmup_state"] == "warming"
    assert data["warmup_day"] == 1


@patch("backend.rex.api_endpoints.get_supabase_client")
def test_check_domain_health(mock_get_db, client, mock_supabase):
    """Test domain health check"""
    mock_get_db.return_value = mock_supabase

    # Mock RPC call
    mock_supabase.rpc().execute.return_value.data = [{
        "health_status": "good",
        "reputation_score": 0.85,
        "deliverability_score": 0.91,
        "should_rotate": False,
    }]

    # Mock domain fetch
    mock_supabase.table().execute.return_value.data = {
        "domain": "mail.example.com",
        "bounce_rate": 0.03,
        "spam_complaint_rate": 0.0005,
    }

    response = client.get("/domain/health/mail.example.com")

    assert response.status_code == 200
    data = response.json()
    assert data["domain"] == "mail.example.com"
    assert data["health_status"] == "good"
    assert data["should_rotate"] is False


# ============================================================================
# INBOX MANAGEMENT TESTS
# ============================================================================

@patch("backend.rex.api_endpoints.get_supabase_client")
def test_allocate_inbox(mock_get_db, client, sample_user_id, mock_supabase):
    """Test inbox allocation"""
    mock_get_db.return_value = mock_supabase

    inbox_id = str(uuid.uuid4())

    # Mock RPC call
    mock_supabase.rpc().execute.return_value.data = inbox_id

    # Mock inbox fetch
    mock_supabase.table().execute.return_value.data = {
        "id": inbox_id,
        "email_address": "sales@example.com",
        "provider": "sendgrid",
        "status": "active",
        "daily_send_limit": 500,
        "emails_sent_today": 120,
    }

    request_data = {
        "user_id": sample_user_id,
        "campaign_id": "campaign_123",
    }

    response = client.post("/inbox/allocate", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["inbox_id"] == inbox_id
    assert data["email_address"] == "sales@example.com"
    assert data["available_capacity"] == 380


@patch("backend.rex.api_endpoints.get_supabase_client")
def test_upgrade_inbox_tier(mock_get_db, client, mock_supabase):
    """Test inbox tier upgrade"""
    mock_get_db.return_value = mock_supabase

    inbox_id = str(uuid.uuid4())

    # Mock RPC calls
    mock_supabase.rpc().execute.return_value.data = [
        {
            "daily_send_limit": 2000,
            "price_per_month": 99.99,
            "features": {"warmup": True, "analytics": True},
        }
    ]

    request_data = {
        "inbox_id": inbox_id,
        "new_tier": "pro",
        "stripe_subscription_id": "sub_123",
    }

    response = client.post("/inbox/upgrade", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["inbox_id"] == inbox_id
    assert data["new_tier"] == "pro"
    assert data["daily_send_limit"] == 2000
    assert data["price_per_month"] == 99.99


# ============================================================================
# WEBHOOK TESTS
# ============================================================================

@patch("backend.rex.api_endpoints.get_supabase_client")
def test_llm_callback(mock_get_db, client, sample_mission_id, mock_supabase):
    """Test LLM callback webhook"""
    mock_get_db.return_value = mock_supabase

    # Mock insert
    mock_supabase.table().execute.return_value.data = [{}]

    request_data = {
        "correlation_id": str(uuid.uuid4()),
        "mission_id": sample_mission_id,
        "agent_name": "ReviverAgent",
        "prompt_hash": "abc123def456",
        "response": {"generated_text": "Hello, this is a personalized message."},
        "model": "gpt-4",
        "tokens_used": 250,
        "cost_usd": 0.005,
        "duration_ms": 1200,
    }

    response = client.post("/webhook/llm", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["acknowledged"] is True
    assert data["logged"] is True


# ============================================================================
# BULK OPERATIONS TESTS
# ============================================================================

@patch("backend.rex.api_endpoints.get_supabase_client")
def test_bulk_create_missions(mock_get_db, client, sample_user_id, mock_supabase):
    """Test bulk mission creation"""
    mock_get_db.return_value = mock_supabase

    # Mock successful inserts
    mock_supabase.table().execute.return_value.data = [
        {"id": str(uuid.uuid4())} for _ in range(3)
    ]

    request_data = {
        "missions": [
            {
                "user_id": sample_user_id,
                "type": "lead_reactivation",
                "priority": 50,
            },
            {
                "user_id": sample_user_id,
                "type": "campaign_execution",
                "priority": 75,
            },
            {
                "user_id": sample_user_id,
                "type": "icp_extraction",
                "priority": 60,
            },
        ]
    }

    response = client.post("/rex/command/bulk", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["created_count"] >= 0
    assert "mission_ids" in data
