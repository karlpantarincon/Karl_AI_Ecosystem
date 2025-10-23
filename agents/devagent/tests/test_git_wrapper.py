"""
Tests for Git wrapper.
"""

import os
import tempfile
from unittest.mock import patch, MagicMock
import pytest

from agents.devagent.tools.git_wrapper import GitWrapper


@pytest.fixture
def temp_repo():
    """Create temporary Git repository for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repo
        import subprocess
        subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
        
        # Create some test files
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        
        yield temp_dir


@pytest.fixture
def git_wrapper(temp_repo):
    """Create GitWrapper with temporary repository."""
    return GitWrapper(temp_repo)


def test_create_branch_success(git_wrapper):
    """Test successful branch creation."""
    branch_name = "feat/test-branch"
    
    result = git_wrapper.create_branch(branch_name)
    
    assert result is True


def test_create_branch_already_exists(git_wrapper):
    """Test branch creation when branch already exists."""
    branch_name = "feat/test-branch"
    
    # Create branch first time
    git_wrapper.create_branch(branch_name)
    
    # Try to create same branch again
    result = git_wrapper.create_branch(branch_name)
    
    assert result is True  # Should return True even if exists


def test_create_branch_failure(git_wrapper):
    """Test branch creation failure."""
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Git error"
        mock_run.return_value = mock_result
        
        result = git_wrapper.create_branch("invalid-branch")
        
        assert result is False


def test_commit_success(git_wrapper):
    """Test successful commit."""
    # Create test file
    test_file = os.path.join(git_wrapper.repo_path, "test_commit.txt")
    with open(test_file, "w") as f:
        f.write("test content")
    
    message = "Test commit"
    files = [test_file]
    
    result = git_wrapper.commit(message, files)
    
    assert result is True


def test_commit_missing_file(git_wrapper):
    """Test commit with missing file."""
    message = "Test commit"
    files = ["nonexistent.txt"]
    
    result = git_wrapper.commit(message, files)
    
    assert result is True  # Should still succeed even with missing files


def test_commit_failure(git_wrapper):
    """Test commit failure."""
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Git commit error"
        mock_run.return_value = mock_result
        
        result = git_wrapper.commit("Test commit", [])
        
        assert result is False


def test_generate_pr_file_success(git_wrapper):
    """Test successful PR file generation."""
    task_id = "T-101"
    pr_data = {
        "title": "Test PR",
        "branch": "feat/T-101-test",
        "files": ["file1.py", "file2.py"],
        "commit": "feat: Test PR"
    }
    
    result = git_wrapper.generate_pr_file(task_id, pr_data)
    
    assert isinstance(result, dict)
    assert "pr_id" in result
    assert "file_path" in result
    assert "branch" in result
    assert "title" in result
    assert "files" in result
    assert "created_at" in result
    
    # Check that PR file was created
    pr_file_path = result["file_path"]
    assert os.path.exists(pr_file_path)
    
    # Check file content
    with open(pr_file_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "# PR: T-101 - Test PR" in content
        assert "## Cambios" in content
        assert "## Archivos modificados" in content


def test_generate_pr_file_failure(git_wrapper):
    """Test PR file generation failure."""
    with patch('builtins.open', side_effect=IOError("File error")):
        result = git_wrapper.generate_pr_file("T-101", {})
        
        assert result == {}


def test_get_current_branch_success(git_wrapper):
    """Test successful current branch retrieval."""
    result = git_wrapper.get_current_branch()
    
    # Should return a branch name (usually 'main' or 'master')
    assert result is not None
    assert isinstance(result, str)


def test_get_current_branch_failure(git_wrapper):
    """Test current branch retrieval failure."""
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Git error"
        mock_run.return_value = mock_result
        
        result = git_wrapper.get_current_branch()
        
        assert result is None


def test_get_status_success(git_wrapper):
    """Test successful status retrieval."""
    result = git_wrapper.get_status()
    
    assert isinstance(result, dict)
    assert "branch" in result
    assert "modified_files" in result
    assert "untracked_files" in result
    assert "staged_files" in result
    assert "status_lines" in result
    
    # Check that all values are integers
    assert isinstance(result["modified_files"], int)
    assert isinstance(result["untracked_files"], int)
    assert isinstance(result["staged_files"], int)
    assert isinstance(result["status_lines"], list)


def test_get_status_failure(git_wrapper):
    """Test status retrieval failure."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = Exception("Git error")
        
        result = git_wrapper.get_status()
        
        assert isinstance(result, dict)
        assert result["branch"] is None
        assert result["modified_files"] == 0
        assert result["untracked_files"] == 0
        assert result["staged_files"] == 0
        assert result["status_lines"] == []


def test_generate_pr_content(git_wrapper):
    """Test PR content generation."""
    task_id = "T-101"
    pr_data = {
        "title": "Test PR",
        "branch": "feat/T-101-test",
        "files": ["file1.py", "file2.py"],
        "commit": "feat: Test PR"
    }
    
    content = git_wrapper._generate_pr_content(task_id, pr_data)
    
    assert isinstance(content, str)
    assert "# PR: T-101 - Test PR" in content
    assert "## Descripción" in content
    assert "## Cambios" in content
    assert "## Archivos modificados" in content
    assert "## Commit" in content
    assert "## Tests" in content
    assert "## Review checklist" in content
    assert "## Métricas" in content
    assert "*PR generado automáticamente por DevAgent*" in content


def test_generate_pr_content_with_files(git_wrapper):
    """Test PR content generation with specific files."""
    task_id = "T-102"
    pr_data = {
        "title": "Another Test PR",
        "branch": "feat/T-102-another",
        "files": ["corehub/api/routes/new.py", "corehub/tests/test_new.py"],
        "commit": "feat: Another test PR"
    }
    
    content = git_wrapper._generate_pr_content(task_id, pr_data)
    
    assert "T-102" in content
    assert "Another Test PR" in content
    assert "corehub/api/routes/new.py" in content
    assert "corehub/tests/test_new.py" in content
    assert "feat: Another test PR" in content


def test_generate_pr_content_minimal_data(git_wrapper):
    """Test PR content generation with minimal data."""
    task_id = "T-103"
    pr_data = {}
    
    content = git_wrapper._generate_pr_content(task_id, pr_data)
    
    assert "T-103" in content
    assert "## Descripción" in content
    assert "## Cambios" in content
    assert "## Archivos modificados" in content
