"""
Tests for CoreHub client.
"""

import pytest
from unittest.mock import AsyncMock, patch
import httpx

from agents.devagent.tools.corehub_client import CoreHubClient


@pytest.fixture
def client():
    """Create CoreHub client."""
    return CoreHubClient("http://localhost:8000")


@pytest.mark.asyncio
async def test_is_system_paused_true(client):
    """Test system pause check when paused."""
    with patch.object(client.client, 'get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"system_paused": True}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = await client.is_system_paused()
        
        assert result is True
        mock_get.assert_called_once_with("http://localhost:8000/admin/pause")


@pytest.mark.asyncio
async def test_is_system_paused_false(client):
    """Test system pause check when not paused."""
    with patch.object(client.client, 'get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"system_paused": False}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = await client.is_system_paused()
        
        assert result is False


@pytest.mark.asyncio
async def test_is_system_paused_error(client):
    """Test system pause check with error."""
    with patch.object(client.client, 'get') as mock_get:
        mock_get.side_effect = Exception("Connection error")
        
        result = await client.is_system_paused()
        
        assert result is False


@pytest.mark.asyncio
async def test_get_next_task_success(client):
    """Test successful task retrieval."""
    task_data = {
        "id": "T-101",
        "title": "Test task",
        "type": "dev",
        "status": "todo"
    }
    
    with patch.object(client.client, 'post') as mock_post:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"task": task_data}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = await client.get_next_task("devagent")
        
        assert result == task_data
        mock_post.assert_called_once_with(
            "http://localhost:8000/tasks/next",
            json={"agent": "devagent"}
        )


@pytest.mark.asyncio
async def test_get_next_task_no_tasks(client):
    """Test task retrieval when no tasks available."""
    with patch.object(client.client, 'post') as mock_post:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"task": None}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = await client.get_next_task("devagent")
        
        assert result is None


@pytest.mark.asyncio
async def test_get_next_task_error(client):
    """Test task retrieval with error."""
    with patch.object(client.client, 'post') as mock_post:
        mock_post.side_effect = Exception("API error")
        
        result = await client.get_next_task("devagent")
        
        assert result is None


@pytest.mark.asyncio
async def test_get_task_success(client):
    """Test successful specific task retrieval."""
    task_data = {
        "id": "T-101",
        "title": "Test task",
        "type": "dev"
    }
    
    with patch.object(client.client, 'get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"task": task_data}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = await client.get_task("T-101")
        
        assert result == task_data
        mock_get.assert_called_once_with("http://localhost:8000/tasks/T-101")


@pytest.mark.asyncio
async def test_get_task_not_found(client):
    """Test task retrieval when task not found."""
    with patch.object(client.client, 'get') as mock_get:
        mock_response = AsyncMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not found", request=None, response=mock_response
        )
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = await client.get_task("T-999")
        
        assert result is None


@pytest.mark.asyncio
async def test_update_task_status_success(client):
    """Test successful task status update."""
    with patch.object(client.client, 'put') as mock_put:
        mock_response = AsyncMock()
        mock_response.raise_for_status.return_value = None
        mock_put.return_value = mock_response
        
        result = await client.update_task_status("T-101", "done")
        
        assert result is True
        mock_put.assert_called_once_with(
            "http://localhost:8000/tasks/T-101/status",
            json={"status": "done"}
        )


@pytest.mark.asyncio
async def test_update_task_status_error(client):
    """Test task status update with error."""
    with patch.object(client.client, 'put') as mock_put:
        mock_put.side_effect = Exception("API error")
        
        result = await client.update_task_status("T-101", "done")
        
        assert result is False


@pytest.mark.asyncio
async def test_log_event_success(client):
    """Test successful event logging."""
    with patch.object(client.client, 'post') as mock_post:
        mock_response = AsyncMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = await client.log_event("devagent", "task_start", {"task_id": "T-101"})
        
        assert result is True
        mock_post.assert_called_once_with(
            "http://localhost:8000/events/log",
            json={
                "agent": "devagent",
                "type": "task_start",
                "payload": {"task_id": "T-101"}
            }
        )


@pytest.mark.asyncio
async def test_log_event_error(client):
    """Test event logging with error."""
    with patch.object(client.client, 'post') as mock_post:
        mock_post.side_effect = Exception("API error")
        
        result = await client.log_event("devagent", "task_start", {})
        
        assert result is False


@pytest.mark.asyncio
async def test_get_daily_report_success(client):
    """Test successful daily report retrieval."""
    report_data = {
        "date": "2025-10-22",
        "metrics": {"completed_tasks": 5},
        "content": "# Daily Report"
    }
    
    with patch.object(client.client, 'get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = report_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = await client.get_daily_report("2025-10-22")
        
        assert result == report_data
        mock_get.assert_called_once_with("http://localhost:8000/report/daily?report_date=2025-10-22")


@pytest.mark.asyncio
async def test_get_daily_report_default_date(client):
    """Test daily report retrieval with default date."""
    with patch.object(client.client, 'get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"date": "2025-10-22"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = await client.get_daily_report()
        
        assert result is not None
        mock_get.assert_called_once_with("http://localhost:8000/report/daily")


@pytest.mark.asyncio
async def test_health_check_success(client):
    """Test successful health check."""
    with patch.object(client.client, 'get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"status": "ok"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = await client.health_check()
        
        assert result is True
        mock_get.assert_called_once_with("http://localhost:8000/health")


@pytest.mark.asyncio
async def test_health_check_failure(client):
    """Test health check failure."""
    with patch.object(client.client, 'get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"status": "error"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = await client.health_check()
        
        assert result is False


@pytest.mark.asyncio
async def test_health_check_error(client):
    """Test health check with error."""
    with patch.object(client.client, 'get') as mock_get:
        mock_get.side_effect = Exception("Connection error")
        
        result = await client.health_check()
        
        assert result is False


@pytest.mark.asyncio
async def test_context_manager(client):
    """Test async context manager."""
    with patch.object(client, 'close') as mock_close:
        async with client as ctx:
            assert ctx is client
        
        mock_close.assert_called_once()
