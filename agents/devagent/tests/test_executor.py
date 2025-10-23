"""
Tests for DevAgent executor.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from agents.devagent.app.executor import DevAgentExecutor
from agents.devagent.tools.corehub_client import CoreHubClient


@pytest.fixture
def mock_client():
    """Mock CoreHub client."""
    client = AsyncMock(spec=CoreHubClient)
    client.is_system_paused.return_value = False
    client.get_next_task.return_value = {
        "id": "T-101",
        "title": "Test task",
        "type": "dev",
        "status": "todo",
        "acceptance": ["test criteria"]
    }
    client.update_task_status.return_value = True
    client.log_event.return_value = True
    return client


@pytest.fixture
def executor(mock_client):
    """Create DevAgent executor with mocked client."""
    return DevAgentExecutor(mock_client)


@pytest.mark.asyncio
async def test_execute_task_success(executor, mock_client):
    """Test successful task execution."""
    with patch.object(executor, '_execute_single_task') as mock_execute:
        mock_execute.return_value = {"status": "completed", "task_id": "T-101"}
        
        result = await executor.execute_task()
        
        assert result is not None
        assert result["status"] == "completed"
        assert result["task_id"] == "T-101"
        
        # Verify client calls
        mock_client.get_next_task.assert_called_once_with("devagent")
        mock_client.log_event.assert_called_once()


@pytest.mark.asyncio
async def test_execute_task_no_tasks(executor, mock_client):
    """Test task execution when no tasks available."""
    mock_client.get_next_task.return_value = None
    
    result = await executor.execute_task()
    
    assert result is None
    mock_client.get_next_task.assert_called_once_with("devagent")


@pytest.mark.asyncio
async def test_execute_task_system_paused(executor, mock_client):
    """Test task execution when system is paused."""
    mock_client.is_system_paused.return_value = True
    
    result = await executor.execute_task()
    
    assert result is None
    mock_client.is_system_paused.assert_called_once()


@pytest.mark.asyncio
async def test_execute_specific_task_success(executor, mock_client):
    """Test successful specific task execution."""
    task_data = {
        "id": "T-102",
        "title": "Specific task",
        "type": "dev",
        "status": "todo"
    }
    mock_client.get_task.return_value = task_data
    
    with patch.object(executor, '_execute_single_task') as mock_execute:
        mock_execute.return_value = {"status": "completed", "task_id": "T-102"}
        
        result = await executor.execute_specific_task("T-102")
        
        assert result is not None
        assert result["status"] == "completed"
        assert result["task_id"] == "T-102"
        
        # Verify client calls
        mock_client.get_task.assert_called_once_with("T-102")
        mock_client.log_event.assert_called_once()


@pytest.mark.asyncio
async def test_execute_specific_task_not_found(executor, mock_client):
    """Test specific task execution when task not found."""
    mock_client.get_task.return_value = None
    
    result = await executor.execute_specific_task("T-999")
    
    assert result is None
    mock_client.get_task.assert_called_once_with("T-999")


@pytest.mark.asyncio
async def test_generate_plan_dev_task(executor):
    """Test plan generation for dev task."""
    task = {
        "id": "T-101",
        "title": "Create new endpoint",
        "type": "dev",
        "acceptance": ["endpoint responds", "tests pass"]
    }
    
    plan = await executor._generate_plan(task)
    
    assert isinstance(plan, list)
    assert len(plan) > 0
    assert "Analyze requirements" in plan[0]
    assert "Implement solution" in plan[1]


@pytest.mark.asyncio
async def test_generate_plan_ops_task(executor):
    """Test plan generation for ops task."""
    task = {
        "id": "T-102",
        "title": "Setup monitoring",
        "type": "ops",
        "acceptance": ["monitoring works", "alerts configured"]
    }
    
    plan = await executor._generate_plan(task)
    
    assert isinstance(plan, list)
    assert len(plan) > 0
    assert "Analyze operational requirements" in plan[0]


@pytest.mark.asyncio
async def test_execute_plan(executor):
    """Test plan execution."""
    task = {
        "id": "T-101",
        "title": "Test task",
        "type": "dev",
        "acceptance": ["test criteria"]
    }
    
    plan = [
        "Analyze requirements",
        "Implement solution",
        "Write tests",
        "Update documentation"
    ]
    
    with patch.object(executor, '_implement_solution') as mock_implement, \
         patch.object(executor, '_create_tests') as mock_tests, \
         patch.object(executor, '_update_documentation') as mock_docs:
        
        mock_implement.return_value = ["file1.py", "file2.py"]
        mock_tests.return_value = ["test_file1.py"]
        mock_docs.return_value = ["README.md"]
        
        actions = await executor._execute_plan(plan, task)
        
        assert isinstance(actions, list)
        assert len(actions) > 0
        mock_implement.assert_called_once()
        mock_tests.assert_called_once()
        mock_docs.assert_called_once()


@pytest.mark.asyncio
async def test_run_quality_checks(executor):
    """Test quality checks execution."""
    with patch.object(executor.code_runner, 'run_tests') as mock_tests, \
         patch.object(executor.code_runner, 'run_lint') as mock_lint, \
         patch.object(executor.code_runner, 'run_type_check') as mock_type:
        
        mock_tests.return_value = {"passed": True, "coverage": {"total": 75}}
        mock_lint.return_value = {"passed": True, "issues": []}
        mock_type.return_value = {"passed": True, "issues": []}
        
        results = await executor._run_quality_checks()
        
        assert isinstance(results, dict)
        assert "tests" in results
        assert "lint" in results
        assert "type_check" in results
        assert "overall" in results
        
        mock_tests.assert_called_once()
        mock_lint.assert_called_once()
        mock_type.assert_called_once()


@pytest.mark.asyncio
async def test_generate_result(executor):
    """Test result generation."""
    task = {
        "id": "T-101",
        "title": "Test task",
        "type": "dev"
    }
    
    plan = ["step1", "step2", "step3"]
    actions = ["file1.py", "file2.py"]
    quality_results = {
        "tests": {"passed": True},
        "lint": {"passed": True},
        "type_check": {"passed": True},
        "overall": "pass"
    }
    
    result = await executor._generate_result(task, plan, actions, quality_results)
    
    assert isinstance(result, dict)
    assert result["task_id"] == "T-101"
    assert result["task_title"] == "Test task"
    assert result["status"] == "completed"
    assert result["plan_steps"] == 3
    assert result["files_modified"] == 2
    assert result["quality_checks"] == quality_results
    assert "timestamp" in result


@pytest.mark.asyncio
async def test_create_pr(executor):
    """Test PR creation."""
    task = {
        "id": "T-101",
        "title": "Test task"
    }
    
    actions = ["file1.py", "file2.py"]
    
    with patch.object(executor.git, 'create_branch') as mock_branch, \
         patch.object(executor.git, 'commit') as mock_commit, \
         patch.object(executor.git, 'generate_pr_file') as mock_pr:
        
        mock_branch.return_value = True
        mock_commit.return_value = True
        mock_pr.return_value = {
            "pr_id": "PR-T-101",
            "file_path": "reports/prs/PR-T-101.md"
        }
        
        pr_info = await executor._create_pr(task, actions)
        
        assert isinstance(pr_info, dict)
        assert "pr_id" in pr_info
        assert "file_path" in pr_info
        
        mock_branch.assert_called_once()
        mock_commit.assert_called_once()
        mock_pr.assert_called_once()


@pytest.mark.asyncio
async def test_execute_single_task_success(executor, mock_client):
    """Test successful single task execution."""
    task = {
        "id": "T-101",
        "title": "Test task",
        "type": "dev",
        "acceptance": ["test criteria"]
    }
    
    with patch.object(executor, '_generate_plan') as mock_plan, \
         patch.object(executor, '_execute_plan') as mock_execute, \
         patch.object(executor, '_run_quality_checks') as mock_quality, \
         patch.object(executor, '_generate_result') as mock_result, \
         patch.object(executor, '_create_pr') as mock_pr:
        
        mock_plan.return_value = ["step1", "step2"]
        mock_execute.return_value = ["file1.py"]
        mock_quality.return_value = {"overall": "pass"}
        mock_result.return_value = {"status": "completed"}
        mock_pr.return_value = {"pr_id": "PR-T-101"}
        
        result = await executor._execute_single_task(task)
        
        assert isinstance(result, dict)
        assert result["status"] == "completed"
        assert "duration_sec" in result
        
        # Verify all methods were called
        mock_plan.assert_called_once_with(task)
        mock_execute.assert_called_once()
        mock_quality.assert_called_once()
        mock_result.assert_called_once()
        mock_pr.assert_called_once()
        
        # Verify task status was updated
        mock_client.update_task_status.assert_called_once_with("T-101", "done")


@pytest.mark.asyncio
async def test_execute_single_task_failure(executor, mock_client):
    """Test single task execution failure."""
    task = {
        "id": "T-101",
        "title": "Test task",
        "type": "dev"
    }
    
    with patch.object(executor, '_generate_plan') as mock_plan:
        mock_plan.side_effect = Exception("Test error")
        
        with pytest.raises(Exception):
            await executor._execute_single_task(task)
        
        # Verify task status was updated to blocked
        mock_client.update_task_status.assert_called_once_with("T-101", "blocked")
