"""
Tests for dashboard API endpoints.

Tests the new dashboard endpoints optimized for React/v0.dev integration.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from corehub.api.main import app
from corehub.db.database import get_db
from corehub.db.models import Task, Run, Event
from corehub.api.schemas import TaskStatus, TaskType, TaskPriority

client = TestClient(app)


@pytest.fixture
def db_session():
    """Get database session for testing."""
    return next(get_db())


@pytest.fixture
def sample_tasks(db_session: Session):
    """Create sample tasks for testing."""
    tasks = [
        Task(
            id="T-001",
            title="Test Task 1",
            type="dev",
            prio=1,
            status="todo"
        ),
        Task(
            id="T-002", 
            title="Test Task 2",
            type="ops",
            prio=2,
            status="in_progress"
        ),
        Task(
            id="T-003",
            title="Test Task 3", 
            type="test",
            prio=3,
            status="done"
        )
    ]
    
    for task in tasks:
        db_session.add(task)
    db_session.commit()
    
    yield tasks
    
    # Cleanup
    for task in tasks:
        db_session.delete(task)
    db_session.commit()


@pytest.fixture
def sample_runs(db_session: Session):
    """Create sample runs for testing."""
    runs = [
        Run(
            agent="devagent",
            task_id="T-001",
            status="completed"
        ),
        Run(
            agent="devagent", 
            task_id="T-002",
            status="running"
        )
    ]
    
    for run in runs:
        db_session.add(run)
    db_session.commit()
    
    yield runs
    
    # Cleanup
    for run in runs:
        db_session.delete(run)
    db_session.commit()


@pytest.fixture
def sample_events(db_session: Session):
    """Create sample events for testing."""
    events = [
        Event(
            agent="devagent",
            type="info",
            description="Test event 1"
        ),
        Event(
            agent="devagent",
            type="error", 
            description="Test event 2"
        )
    ]
    
    for event in events:
        db_session.add(event)
    db_session.commit()
    
    yield events
    
    # Cleanup
    for event in events:
        db_session.delete(event)
    db_session.commit()


class TestDashboardOverview:
    """Test dashboard overview endpoint."""
    
    def test_get_dashboard_overview(self, sample_tasks, sample_runs, sample_events):
        """Test getting dashboard overview."""
        response = client.get("/dashboard/overview")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "system_status" in data
        assert "tasks" in data
        assert "performance" in data
        assert "activity" in data
        
        # Check task statistics
        assert data["tasks"]["total"] >= 3
        assert data["tasks"]["completed"] >= 1
        assert data["tasks"]["in_progress"] >= 1
        assert data["tasks"]["todo"] >= 1
        
        # Check system status
        assert data["system_status"]["status"] == "healthy"
        
        # Check activity info
        assert data["activity"]["active_agents"] >= 0


class TestDashboardTasks:
    """Test dashboard tasks endpoint."""
    
    def test_get_dashboard_tasks(self, sample_tasks):
        """Test getting dashboard tasks."""
        response = client.get("/dashboard/tasks")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "tasks" in data
        assert "pagination" in data
        
        # Check tasks structure
        assert len(data["tasks"]) >= 3
        task = data["tasks"][0]
        assert "id" in task
        assert "title" in task
        assert "type" in task
        assert "priority" in task
        assert "status" in task
        assert "created_at" in task
    
    def test_get_dashboard_tasks_with_filters(self, sample_tasks):
        """Test getting dashboard tasks with filters."""
        # Filter by status
        response = client.get("/dashboard/tasks?status=done")
        assert response.status_code == 200
        data = response.json()
        
        # All returned tasks should be done
        for task in data["tasks"]:
            assert task["status"] == "done"
        
        # Filter by priority
        response = client.get("/dashboard/tasks?priority=1")
        assert response.status_code == 200
        data = response.json()
        
        # All returned tasks should have priority 1
        for task in data["tasks"]:
            assert task["priority"] == 1
    
    def test_get_dashboard_tasks_pagination(self, sample_tasks):
        """Test dashboard tasks pagination."""
        response = client.get("/dashboard/tasks?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["tasks"]) <= 2
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["offset"] == 0
        assert "has_more" in data["pagination"]


class TestDashboardMetrics:
    """Test dashboard metrics endpoint."""
    
    def test_get_dashboard_metrics(self, sample_tasks, sample_runs):
        """Test getting dashboard metrics."""
        response = client.get("/dashboard/metrics")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "daily_completions" in data
        assert "agent_performance" in data
        assert "system_metrics" in data
        assert "generated_at" in data
        
        # Check daily completions structure
        assert isinstance(data["daily_completions"], list)
        if data["daily_completions"]:
            completion = data["daily_completions"][0]
            assert "date" in completion
            assert "completed" in completion
        
        # Check system metrics structure
        metrics = data["system_metrics"]
        assert "avg_response_time" in metrics
        assert "error_rate" in metrics
        assert "throughput" in metrics
        assert "uptime" in metrics


class TestDashboardLogs:
    """Test dashboard logs endpoint."""
    
    def test_get_dashboard_logs(self, sample_events):
        """Test getting dashboard logs."""
        response = client.get("/dashboard/logs")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "logs" in data
        assert "total" in data
        assert "filters" in data
        
        # Check logs structure
        assert len(data["logs"]) >= 0
        if data["logs"]:
            log = data["logs"][0]
            assert "id" in log
            assert "timestamp" in log
            assert "level" in log
            assert "agent" in log
            assert "message" in log
            assert "data" in log
    
    def test_get_dashboard_logs_with_filters(self, sample_events):
        """Test getting dashboard logs with filters."""
        # Filter by level
        response = client.get("/dashboard/logs?level=error")
        assert response.status_code == 200
        data = response.json()
        
        # All returned logs should be error level
        for log in data["logs"]:
            assert log["level"] == "error"
        
        # Filter by agent
        response = client.get("/dashboard/logs?agent=devagent")
        assert response.status_code == 200
        data = response.json()
        
        # All returned logs should be from devagent
        for log in data["logs"]:
            assert log["agent"] == "devagent"


class TestTaskStatusUpdate:
    """Test task status update endpoint."""
    
    def test_update_task_status(self, sample_tasks):
        """Test updating task status."""
        task_id = "T-001"
        new_status = "in_progress"
        
        response = client.post(
            f"/dashboard/tasks/{task_id}/status",
            params={"status": new_status}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert data["success"] is True
        assert "message" in data
        assert "task" in data
        
        # Check task structure
        task = data["task"]
        assert task["id"] == task_id
        assert task["status"] == new_status
    
    def test_update_task_status_invalid_task(self, sample_tasks):
        """Test updating status of non-existent task."""
        response = client.post(
            "/dashboard/tasks/NONEXISTENT/status",
            params={"status": "done"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Task not found" in data["detail"]
    
    def test_update_task_status_invalid_status(self, sample_tasks):
        """Test updating task with invalid status."""
        task_id = "T-001"
        
        response = client.post(
            f"/dashboard/tasks/{task_id}/status",
            params={"status": "invalid_status"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid status" in data["detail"]


class TestAgentsStatus:
    """Test agents status endpoint."""
    
    def test_get_agents_status(self, sample_runs):
        """Test getting agents status."""
        response = client.get("/dashboard/agents")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "agents" in data
        assert "total_agents" in data
        assert "active_agents" in data
        assert "last_updated" in data
        
        # Check agents structure
        assert len(data["agents"]) >= 0
        if data["agents"]:
            agent = data["agents"][0]
            assert "name" in agent
            assert "status" in agent
            assert "total_runs" in agent
            assert "success_rate" in agent


class TestAgentControl:
    """Test agent control endpoint."""
    
    def test_control_agent(self, sample_runs):
        """Test controlling an agent."""
        agent_name = "devagent"
        action = "start"
        
        response = client.post(
            f"/dashboard/agents/{agent_name}/control",
            params={"action": action}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert data["success"] is True
        assert data["agent"] == agent_name
        assert data["action"] == action
        assert "timestamp" in data
    
    def test_control_agent_invalid_action(self, sample_runs):
        """Test controlling an agent with invalid action."""
        agent_name = "devagent"
        action = "invalid_action"
        
        response = client.post(
            f"/dashboard/agents/{agent_name}/control",
            params={"action": action}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid action" in data["detail"]


class TestDashboardHealth:
    """Test dashboard health endpoint."""
    
    def test_get_dashboard_health(self):
        """Test getting dashboard health."""
        response = client.get("/dashboard/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "components" in data
        
        # Check components structure
        components = data["components"]
        assert "api" in components
        assert "database" in components
        assert "cache" in components
        assert "notifications" in components


class TestDashboardErrorHandling:
    """Test dashboard error handling."""
    
    def test_dashboard_overview_error_handling(self):
        """Test dashboard overview error handling."""
        # This test would require mocking database errors
        # For now, just test that the endpoint exists
        response = client.get("/dashboard/overview")
        assert response.status_code in [200, 500]  # Either success or server error
    
    def test_dashboard_tasks_invalid_parameters(self):
        """Test dashboard tasks with invalid parameters."""
        # Test with negative limit
        response = client.get("/dashboard/tasks?limit=-1")
        # Should either handle gracefully or return error
        assert response.status_code in [200, 400, 422]
        
        # Test with negative offset
        response = client.get("/dashboard/tasks?offset=-1")
        # Should either handle gracefully or return error
        assert response.status_code in [200, 400, 422]


class TestDashboardIntegration:
    """Test dashboard integration scenarios."""
    
    def test_full_dashboard_workflow(self, sample_tasks, sample_runs, sample_events):
        """Test complete dashboard workflow."""
        # 1. Get overview
        overview_response = client.get("/dashboard/overview")
        assert overview_response.status_code == 200
        
        # 2. Get tasks
        tasks_response = client.get("/dashboard/tasks")
        assert tasks_response.status_code == 200
        
        # 3. Get metrics
        metrics_response = client.get("/dashboard/metrics")
        assert metrics_response.status_code == 200
        
        # 4. Get logs
        logs_response = client.get("/dashboard/logs")
        assert logs_response.status_code == 200
        
        # 5. Get agents
        agents_response = client.get("/dashboard/agents")
        assert agents_response.status_code == 200
        
        # 6. Update task status
        if tasks_response.json()["tasks"]:
            task_id = tasks_response.json()["tasks"][0]["id"]
            update_response = client.post(
                f"/dashboard/tasks/{task_id}/status",
                params={"status": "in_progress"}
            )
            assert update_response.status_code == 200
        
        # 7. Check health
        health_response = client.get("/dashboard/health")
        assert health_response.status_code == 200
        
        # All responses should have consistent structure
        all_responses = [
            overview_response, tasks_response, metrics_response,
            logs_response, agents_response, health_response
        ]
        
        for response in all_responses:
            data = response.json()
            assert isinstance(data, dict)
            # Should not have any obvious errors
            assert "error" not in data or data.get("success", True)
