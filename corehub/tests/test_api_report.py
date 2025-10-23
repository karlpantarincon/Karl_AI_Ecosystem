"""
Tests for report generation endpoints.
"""

import os
import tempfile
from datetime import date, datetime
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from corehub.api.main import app
from corehub.db.database import get_db
from corehub.db.models import Base, Task, Run, Event

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


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    with TestingSessionLocal() as db:
        # Create sample tasks
        tasks = [
            Task(
                id="T-101",
                title="Test task 1",
                type="dev",
                prio=1,
                status="done",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            Task(
                id="T-102",
                title="Test task 2",
                type="ops",
                prio=2,
                status="done",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        # Create sample runs
        runs = [
            Run(
                agent="devagent",
                task_id="T-101",
                status="completed",
                cost_usd=0.25,
                duration_sec=120.0,
                created_at=datetime.utcnow()
            ),
            Run(
                agent="devagent",
                task_id="T-102",
                status="completed",
                cost_usd=0.15,
                duration_sec=90.0,
                created_at=datetime.utcnow()
            )
        ]
        
        # Create sample events
        events = [
            Event(
                agent="devagent",
                type="task_start",
                payload={"task_id": "T-101"},
                created_at=datetime.utcnow()
            ),
            Event(
                agent="system",
                type="health_check",
                payload={"status": "healthy"},
                created_at=datetime.utcnow()
            )
        ]
        
        for task in tasks:
            db.add(task)
        for run in runs:
            db.add(run)
        for event in events:
            db.add(event)
        
        db.commit()


def test_get_daily_report_default_date(client, sample_data):
    """Test daily report generation with default date."""
    response = client.get("/report/daily")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "date" in data
    assert "metrics" in data
    assert "content" in data
    assert "report_path" in data
    
    # Check metrics
    metrics = data["metrics"]
    assert "completed_tasks" in metrics
    assert "total_runs" in metrics
    assert "successful_runs" in metrics
    assert "success_rate" in metrics
    assert "total_cost" in metrics
    assert "total_duration" in metrics
    assert "total_events" in metrics


def test_get_daily_report_specific_date(client, sample_data):
    """Test daily report generation with specific date."""
    test_date = "2025-10-22"
    response = client.get(f"/report/daily?report_date={test_date}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["date"] == test_date
    assert "content" in data
    assert "metrics" in data


def test_get_daily_report_invalid_date(client):
    """Test daily report with invalid date format."""
    response = client.get("/report/daily?report_date=invalid-date")
    
    assert response.status_code == 400
    data = response.json()
    assert "Invalid date format" in data["detail"]


def test_get_daily_report_file_success(client, sample_data):
    """Test getting daily report file."""
    # First generate a report
    response = client.get("/report/daily")
    assert response.status_code == 200
    
    # Get the report file
    report_date = response.json()["date"]
    response = client.get(f"/report/daily/{report_date}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "date" in data
    assert "content" in data
    assert "file_path" in data
    assert "Resumen Diario" in data["content"]


def test_get_daily_report_file_not_found(client):
    """Test getting non-existent daily report file."""
    response = client.get("/report/daily/2025-01-01")
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]


def test_get_daily_report_file_invalid_date(client):
    """Test getting daily report file with invalid date."""
    response = client.get("/report/daily/invalid-date")
    
    assert response.status_code == 400
    data = response.json()
    assert "Invalid date format" in data["detail"]


def test_daily_report_content_structure(client, sample_data):
    """Test that daily report content has expected structure."""
    response = client.get("/report/daily")
    
    assert response.status_code == 200
    data = response.json()
    content = data["content"]
    
    # Check that content contains expected sections
    assert "# Resumen Diario" in content
    assert "## Tareas Completadas" in content
    assert "## Métricas del Día" in content
    assert "## Eventos del Día" in content
    assert "## Próximas Acciones" in content
    assert "*Reporte generado automáticamente por CoreHub*" in content


def test_daily_report_metrics_calculation(client, sample_data):
    """Test that daily report metrics are calculated correctly."""
    response = client.get("/report/daily")
    
    assert response.status_code == 200
    data = response.json()
    metrics = data["metrics"]
    
    # Verify metrics are numeric
    assert isinstance(metrics["completed_tasks"], int)
    assert isinstance(metrics["total_runs"], int)
    assert isinstance(metrics["successful_runs"], int)
    assert isinstance(metrics["success_rate"], (int, float))
    assert isinstance(metrics["total_cost"], (int, float))
    assert isinstance(metrics["total_duration"], (int, float))
    assert isinstance(metrics["total_events"], int)
    
    # Verify success rate is between 0 and 100
    assert 0 <= metrics["success_rate"] <= 100
