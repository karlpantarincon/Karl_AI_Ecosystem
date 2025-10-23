"""
Tests for task management endpoints.
"""

import json
import os
import tempfile
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from corehub.api.main import app
from corehub.db.database import get_db
from corehub.db.models import Base, Task

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
def mock_kanban():
    """Mock kanban configuration."""
    return {
        "v": 1,
        "sprint": "2025-10-23",
        "goals": ["Test goals"],
        "tasks": [
            {
                "id": "T-101",
                "title": "Test task 1",
                "prio": 1,
                "type": "dev",
                "status": "todo",
                "acceptance": ["test criteria"]
            },
            {
                "id": "T-102",
                "title": "Test task 2",
                "prio": 2,
                "type": "ops",
                "status": "todo",
                "acceptance": ["test criteria 2"]
            }
        ]
    }


def test_get_next_task_success(client, mock_kanban):
    """Test successful task retrieval."""
    with patch('corehub.api.routes.tasks.load_kanban', return_value=mock_kanban):
        response = client.post("/tasks/next", json={"agent": "devagent"})
        
        assert response.status_code == 200
        data = response.json()
        
        assert "task" in data
        assert data["task"]["id"] == "T-101"  # Highest priority
        assert data["agent"] == "devagent"
        assert data["task"]["status"] == "in_progress"  # Should be updated


def test_get_next_task_no_agent(client):
    """Test task retrieval without agent."""
    response = client.post("/tasks/next", json={})
    
    assert response.status_code == 400
    data = response.json()
    assert "Agent name is required" in data["detail"]


def test_get_next_task_no_tasks(client):
    """Test task retrieval when no tasks available."""
    empty_kanban = {
        "v": 1,
        "sprint": "2025-10-23",
        "goals": ["Test goals"],
        "tasks": []
    }
    
    with patch('corehub.api.routes.tasks.load_kanban', return_value=empty_kanban):
        response = client.post("/tasks/next", json={"agent": "devagent"})
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["task"] is None
        assert data["message"] == "No tasks available"


def test_list_tasks_all(client, mock_kanban):
    """Test listing all tasks."""
    with patch('corehub.api.routes.tasks.load_kanban', return_value=mock_kanban):
        response = client.get("/tasks/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "tasks" in data
        assert len(data["tasks"]) == 2
        assert data["total"] == 2


def test_list_tasks_filtered(client, mock_kanban):
    """Test listing tasks with status filter."""
    with patch('corehub.api.routes.tasks.load_kanban', return_value=mock_kanban):
        response = client.get("/tasks/?status=todo")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "tasks" in data
        assert len(data["tasks"]) == 2
        assert all(task["status"] == "todo" for task in data["tasks"])


def test_get_specific_task(client, mock_kanban):
    """Test getting specific task by ID."""
    with patch('corehub.api.routes.tasks.load_kanban', return_value=mock_kanban):
        response = client.get("/tasks/T-101")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "task" in data
        assert data["task"]["id"] == "T-101"
        assert data["task"]["title"] == "Test task 1"


def test_get_specific_task_not_found(client, mock_kanban):
    """Test getting non-existent task."""
    with patch('corehub.api.routes.tasks.load_kanban', return_value=mock_kanban):
        response = client.get("/tasks/T-999")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]


def test_update_task_status(client, mock_kanban):
    """Test updating task status."""
    with patch('corehub.api.routes.tasks.load_kanban', return_value=mock_kanban):
        response = client.put("/tasks/T-101/status", json={"status": "done"})
        
        assert response.status_code == 200
        data = response.json()
        
        assert "task" in data
        assert data["task"]["status"] == "done"
        assert "updated" in data["message"]


def test_update_task_status_invalid(client, mock_kanban):
    """Test updating task status with invalid status."""
    with patch('corehub.api.routes.tasks.load_kanban', return_value=mock_kanban):
        response = client.put("/tasks/T-101/status", json={"status": "invalid"})
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid status" in data["detail"]


def test_update_task_status_missing_status(client, mock_kanban):
    """Test updating task status without status field."""
    with patch('corehub.api.routes.tasks.load_kanban', return_value=mock_kanban):
        response = client.put("/tasks/T-101/status", json={})
        
        assert response.status_code == 400
        data = response.json()
        assert "Status is required" in data["detail"]
