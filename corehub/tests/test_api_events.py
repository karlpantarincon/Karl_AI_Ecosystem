"""
Tests for event logging endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from corehub.api.main import app
from corehub.db.database import get_db
from corehub.db.models import Base, Event

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    """Create test client."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def test_log_event_success(client):
    """Test successful event logging."""
    event_data = {
        "agent": "devagent",
        "type": "task_start",
        "payload": {"task_id": "T-101", "duration": 120}
    }
    
    response = client.post("/events/log", json=event_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "id" in data
    assert "created_at" in data
    assert data["message"] == "Event logged successfully"


def test_log_event_minimal(client):
    """Test event logging with minimal data."""
    event_data = {
        "type": "system_start"
    }
    
    response = client.post("/events/log", json=event_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "id" in data
    assert "created_at" in data


def test_log_event_missing_type(client):
    """Test event logging without required type field."""
    event_data = {
        "agent": "devagent",
        "payload": {"data": "test"}
    }
    
    response = client.post("/events/log", json=event_data)
    
    assert response.status_code == 400
    data = response.json()
    assert "Event type is required" in data["detail"]


def test_list_events_all(client):
    """Test listing all events."""
    # First, create some test events
    events = [
        {"agent": "devagent", "type": "task_start", "payload": {"task_id": "T-101"}},
        {"agent": "system", "type": "health_check", "payload": {"status": "healthy"}},
        {"agent": "devagent", "type": "task_complete", "payload": {"task_id": "T-101"}}
    ]
    
    for event in events:
        client.post("/events/log", json=event)
    
    response = client.get("/events/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "events" in data
    assert "total" in data
    assert len(data["events"]) >= 3


def test_list_events_with_filters(client):
    """Test listing events with filters."""
    # Create test events
    events = [
        {"agent": "devagent", "type": "task_start", "payload": {"task_id": "T-101"}},
        {"agent": "system", "type": "health_check", "payload": {"status": "healthy"}},
        {"agent": "devagent", "type": "task_complete", "payload": {"task_id": "T-101"}}
    ]
    
    for event in events:
        client.post("/events/log", json=event)
    
    # Filter by agent
    response = client.get("/events/?agent=devagent")
    assert response.status_code == 200
    data = response.json()
    assert all(event["agent"] == "devagent" for event in data["events"])
    
    # Filter by type
    response = client.get("/events/?event_type=health_check")
    assert response.status_code == 200
    data = response.json()
    assert all(event["type"] == "health_check" for event in data["events"])


def test_list_events_pagination(client):
    """Test event listing with pagination."""
    # Create multiple events
    for i in range(5):
        client.post("/events/log", json={
            "agent": "test",
            "type": f"test_event_{i}",
            "payload": {"index": i}
        })
    
    # Test pagination
    response = client.get("/events/?limit=3&offset=0")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["events"]) <= 3
    assert data["limit"] == 3
    assert data["offset"] == 0


def test_get_specific_event(client):
    """Test getting specific event by ID."""
    # Create an event
    event_data = {
        "agent": "devagent",
        "type": "test_event",
        "payload": {"test": "data"}
    }
    
    create_response = client.post("/events/log", json=event_data)
    event_id = create_response.json()["id"]
    
    # Get the specific event
    response = client.get(f"/events/{event_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == event_id
    assert data["agent"] == "devagent"
    assert data["type"] == "test_event"
    assert data["payload"]["test"] == "data"


def test_get_specific_event_not_found(client):
    """Test getting non-existent event."""
    response = client.get("/events/99999")
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]
