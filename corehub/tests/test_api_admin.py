"""
Tests for admin endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from corehub.api.main import app
from corehub.db.database import get_db
from corehub.db.models import Base

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_admin.db"
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


def test_get_system_status(client):
    """Test getting system status."""
    response = client.get("/admin/status")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "timestamp" in data
    assert "database" in data


def test_pause_system(client):
    """Test pausing the system."""
    response = client.post("/admin/pause")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "paused"
    assert "message" in data


def test_resume_system(client):
    """Test resuming the system."""
    response = client.post("/admin/resume")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "active"
    assert "message" in data


def test_get_system_metrics(client):
    """Test getting system metrics."""
    response = client.get("/admin/metrics")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "tasks" in data
    assert "runs" in data
    assert "events" in data
    assert "timestamp" in data


def test_get_system_logs(client):
    """Test getting system logs."""
    response = client.get("/admin/logs")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "logs" in data
    assert "total" in data
    assert "timestamp" in data


def test_get_system_logs_with_limit(client):
    """Test getting system logs with limit."""
    response = client.get("/admin/logs?limit=10")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "logs" in data
    assert "total" in data
    assert len(data["logs"]) <= 10


def test_get_system_logs_with_level(client):
    """Test getting system logs with level filter."""
    response = client.get("/admin/logs?level=ERROR")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "logs" in data
    assert "total" in data


def test_clear_system_logs(client):
    """Test clearing system logs."""
    response = client.delete("/admin/logs")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "message" in data


def test_get_database_info(client):
    """Test getting database information."""
    response = client.get("/admin/database")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "connected" in data
    assert "url" in data
    assert "version" in data


def test_health_check_detailed(client):
    """Test detailed health check."""
    response = client.get("/admin/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "database" in data
    assert "scheduler" in data
    assert "timestamp" in data


def test_restart_scheduler(client):
    """Test restarting the scheduler."""
    response = client.post("/admin/scheduler/restart")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "message" in data


def test_stop_scheduler(client):
    """Test stopping the scheduler."""
    response = client.post("/admin/scheduler/stop")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "message" in data


def test_start_scheduler(client):
    """Test starting the scheduler."""
    response = client.post("/admin/scheduler/start")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "message" in data


def test_get_scheduler_status(client):
    """Test getting scheduler status."""
    response = client.get("/admin/scheduler/status")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "running" in data
    assert "jobs" in data
    assert "timestamp" in data