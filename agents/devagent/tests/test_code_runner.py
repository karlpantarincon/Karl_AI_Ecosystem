"""
Tests for code runner.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import subprocess

from agents.devagent.tools.code_runner import CodeRunner


@pytest.fixture
def code_runner():
    """Create CodeRunner instance."""
    return CodeRunner(".")


def test_run_tests_success(code_runner):
    """Test successful test execution."""
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """
        ========================== test session starts ==========================
        corehub/tests/test_api_health.py::test_health_check_basic PASSED
        corehub/tests/test_api_tasks.py::test_get_next_task_success PASSED
        ========================== 2 passed in 0.05s ==========================
        
        ---------- coverage: platform win32, python 3.11.0 -----------
        Name                     Stmts   Miss  Cover   Missing
        -----------------------------------------------------
        corehub/api/health.py       15      0   100%
        corehub/api/tasks.py        25      3    88%
        -----------------------------------------------------
        TOTAL                       40      3    92%
        """
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = code_runner.run_tests()
        
        assert result["passed"] is True
        assert result["returncode"] == 0
        assert "coverage" in result
        assert result["coverage"]["total"] == 92.0


def test_run_tests_failure(code_runner):
    """Test test execution failure."""
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "Some test output"
        mock_result.stderr = "Test failure"
        mock_run.return_value = mock_result
        
        result = code_runner.run_tests()
        
        assert result["passed"] is False
        assert result["returncode"] == 1
        assert "Test failure" in result["error"]


def test_run_tests_timeout(code_runner):
    """Test test execution timeout."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired("pytest", 300)
        
        result = code_runner.run_tests()
        
        assert result["passed"] is False
        assert result["returncode"] == -1
        assert "Tests timed out" in result["error"]


def test_run_tests_exception(code_runner):
    """Test test execution with exception."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = Exception("Test execution error")
        
        result = code_runner.run_tests()
        
        assert result["passed"] is False
        assert result["returncode"] == -1
        assert "Test execution error" in result["error"]


def test_run_tests_with_path(code_runner):
    """Test test execution with specific path."""
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Tests passed"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = code_runner.run_tests("corehub/tests/test_specific.py")
        
        assert result["passed"] is True
        
        # Check that the command included the specific path
        call_args = mock_run.call_args[0][0]
        assert "corehub/tests/test_specific.py" in call_args


def test_run_lint_success(code_runner):
    """Test successful lint execution."""
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = code_runner.run_lint()
        
        assert result["passed"] is True
        assert result["returncode"] == 0
        assert result["issues"] == []


def test_run_lint_with_issues(code_runner):
    """Test lint execution with issues."""
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = """
        corehub/api/health.py:15:1: E501 line too long (88 > 79 characters)
        corehub/api/tasks.py:25:5: F401 'unused_import' imported but unused
        """
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = code_runner.run_lint()
        
        assert result["passed"] is False
        assert result["returncode"] == 1
        assert len(result["issues"]) == 2
        assert "E501" in result["issues"][0]
        assert "F401" in result["issues"][1]


def test_run_lint_exception(code_runner):
    """Test lint execution with exception."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = Exception("Lint execution error")
        
        result = code_runner.run_lint()
        
        assert result["passed"] is False
        assert result["returncode"] == -1
        assert "Lint execution error" in result["error"]


def test_run_type_check_success(code_runner):
    """Test successful type check execution."""
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success: no issues found"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = code_runner.run_type_check()
        
        assert result["passed"] is True
        assert result["returncode"] == 0
        assert result["issues"] == []


def test_run_type_check_with_issues(code_runner):
    """Test type check execution with issues."""
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = """
        corehub/api/health.py:15: error: Argument 1 to "health_check" has incompatible type "str"; expected "int"
        corehub/api/tasks.py:25: error: "None" has no attribute "get"
        """
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = code_runner.run_type_check()
        
        assert result["passed"] is False
        assert result["returncode"] == 1
        assert len(result["issues"]) == 2
        assert "incompatible type" in result["issues"][0]
        assert "has no attribute" in result["issues"][1]


def test_run_type_check_exception(code_runner):
    """Test type check execution with exception."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = Exception("Type check execution error")
        
        result = code_runner.run_type_check()
        
        assert result["passed"] is False
        assert result["returncode"] == -1
        assert "Type check execution error" in result["error"]


def test_run_format_check_success(code_runner):
    """Test successful format check execution."""
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "All done! ✨ 🍰 ✨"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = code_runner.run_format_check()
        
        assert result["passed"] is True
        assert result["returncode"] == 0


def test_run_format_check_needs_formatting(code_runner):
    """Test format check when formatting is needed."""
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "would reformat corehub/api/health.py"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = code_runner.run_format_check()
        
        assert result["passed"] is False
        assert result["returncode"] == 1


def test_run_format_check_exception(code_runner):
    """Test format check execution with exception."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = Exception("Format check execution error")
        
        result = code_runner.run_format_check()
        
        assert result["passed"] is False
        assert result["returncode"] == -1
        assert "Format check execution error" in result["error"]


def test_run_all_quality_checks_success(code_runner):
    """Test successful execution of all quality checks."""
    with patch.object(code_runner, 'run_tests') as mock_tests, \
         patch.object(code_runner, 'run_lint') as mock_lint, \
         patch.object(code_runner, 'run_type_check') as mock_type, \
         patch.object(code_runner, 'run_format_check') as mock_format:
        
        mock_tests.return_value = {"passed": True, "coverage": {"total": 85}}
        mock_lint.return_value = {"passed": True, "issues": []}
        mock_type.return_value = {"passed": True, "issues": []}
        mock_format.return_value = {"passed": True}
        
        result = code_runner.run_all_quality_checks()
        
        assert result["overall"] == "pass"
        assert result["tests"]["passed"] is True
        assert result["lint"]["passed"] is True
        assert result["type_check"]["passed"] is True
        assert result["format_check"]["passed"] is True


def test_run_all_quality_checks_failure(code_runner):
    """Test quality checks with some failures."""
    with patch.object(code_runner, 'run_tests') as mock_tests, \
         patch.object(code_runner, 'run_lint') as mock_lint, \
         patch.object(code_runner, 'run_type_check') as mock_type, \
         patch.object(code_runner, 'run_format_check') as mock_format:
        
        mock_tests.return_value = {"passed": True, "coverage": {"total": 85}}
        mock_lint.return_value = {"passed": False, "issues": ["E501"]}
        mock_type.return_value = {"passed": True, "issues": []}
        mock_format.return_value = {"passed": True}
        
        result = code_runner.run_all_quality_checks()
        
        assert result["overall"] == "fail"
        assert result["tests"]["passed"] is True
        assert result["lint"]["passed"] is False
        assert result["type_check"]["passed"] is True
        assert result["format_check"]["passed"] is True


def test_run_all_quality_checks_exception(code_runner):
    """Test quality checks with exceptions."""
    with patch.object(code_runner, 'run_tests') as mock_tests, \
         patch.object(code_runner, 'run_lint') as mock_lint, \
         patch.object(code_runner, 'run_type_check') as mock_type, \
         patch.object(code_runner, 'run_format_check') as mock_format:
        
        mock_tests.return_value = Exception("Test error")
        mock_lint.return_value = {"passed": True, "issues": []}
        mock_type.return_value = {"passed": True, "issues": []}
        mock_format.return_value = {"passed": True}
        
        result = code_runner.run_all_quality_checks()
        
        assert result["overall"] == "fail"
        assert result["tests"]["passed"] is False
        assert "Test error" in result["tests"]["error"]


def test_extract_coverage(code_runner):
    """Test coverage extraction from pytest output."""
    output = """
    ========================== test session starts ==========================
    corehub/tests/test_api_health.py::test_health_check_basic PASSED
    ========================== 1 passed in 0.05s ==========================
    
    ---------- coverage: platform win32, python 3.11.0 -----------
    Name                     Stmts   Miss  Cover   Missing
    -----------------------------------------------------
    corehub/api/health.py       15      0   100%
    corehub/api/tasks.py        25      3    88%
    -----------------------------------------------------
    TOTAL                       40      3    92%
    """
    
    coverage = code_runner._extract_coverage(output)
    
    assert coverage["total"] == 92.0


def test_extract_coverage_no_data(code_runner):
    """Test coverage extraction with no coverage data."""
    output = "No coverage data available"
    
    coverage = code_runner._extract_coverage(output)
    
    assert coverage == {}


def test_extract_percentage(code_runner):
    """Test percentage extraction from line."""
    line = "corehub/api/health.py       15      0   100%"
    
    percentage = code_runner._extract_percentage(line)
    
    assert percentage == 100.0


def test_extract_percentage_no_percentage(code_runner):
    """Test percentage extraction with no percentage."""
    line = "corehub/api/health.py       15      0"
    
    percentage = code_runner._extract_percentage(line)
    
    assert percentage == 0.0
