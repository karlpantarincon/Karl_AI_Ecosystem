"""
Code execution and quality checks for DevAgent.

This module provides functionality to run tests, lint, and other quality checks.
"""

import asyncio
import subprocess
from typing import Dict, Any, List, Optional

from loguru import logger


class CodeRunner:
    """Code execution and quality checks."""
    
    def __init__(self, project_root: str = "."):
        """
        Initialize code runner.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
    
    async def run_tests(self, test_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Run tests using pytest.
        
        Args:
            test_path: Specific test path or None for all tests
            
        Returns:
            Dict with test results
        """
        try:
            cmd = ["python", "-m", "pytest"]
            
            if test_path:
                cmd.append(test_path)
            else:
                cmd.extend(["corehub/tests", "agents/devagent/tests"])
            
            cmd.extend([
                "--cov=corehub",
                "--cov=agents",
                "--cov-report=term-missing",
                "--tb=short",
                "-v"
            ])
            
            logger.info(f"🧪 Running tests: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Parse results
            passed = result.returncode == 0
            output = result.stdout
            error = result.stderr
            
            # Extract coverage info if available
            coverage = self._extract_coverage(output)
            
            return {
                "passed": passed,
                "returncode": result.returncode,
                "output": output,
                "error": error,
                "coverage": coverage
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Tests timed out after 5 minutes")
            return {
                "passed": False,
                "returncode": -1,
                "output": "",
                "error": "Tests timed out",
                "coverage": {}
            }
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return {
                "passed": False,
                "returncode": -1,
                "output": "",
                "error": str(e),
                "coverage": {}
            }
    
    async def run_lint(self) -> Dict[str, Any]:
        """
        Run linting using ruff.
        
        Returns:
            Dict with lint results
        """
        try:
            cmd = ["python", "-m", "ruff", "check", "corehub/", "agents/"]
            
            logger.info(f"🔍 Running lint: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            # Ruff returns 0 for no issues, 1 for issues found
            passed = result.returncode == 0
            issues = result.stdout.split('\n') if result.stdout else []
            
            return {
                "passed": passed,
                "returncode": result.returncode,
                "issues": issues,
                "output": result.stdout,
                "error": result.stderr
            }
            
        except Exception as e:
            logger.error(f"Lint execution failed: {e}")
            return {
                "passed": False,
                "returncode": -1,
                "issues": [],
                "output": "",
                "error": str(e)
            }
    
    async def run_type_check(self) -> Dict[str, Any]:
        """
        Run type checking using mypy.
        
        Returns:
            Dict with type check results
        """
        try:
            cmd = ["python", "-m", "mypy", "corehub/", "agents/"]
            
            logger.info(f"🔍 Running type check: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            # Mypy returns 0 for no issues, 1 for issues found
            passed = result.returncode == 0
            issues = result.stdout.split('\n') if result.stdout else []
            
            return {
                "passed": passed,
                "returncode": result.returncode,
                "issues": issues,
                "output": result.stdout,
                "error": result.stderr
            }
            
        except Exception as e:
            logger.error(f"Type check execution failed: {e}")
            return {
                "passed": False,
                "returncode": -1,
                "issues": [],
                "output": "",
                "error": str(e)
            }
    
    async def run_format_check(self) -> Dict[str, Any]:
        """
        Check code formatting using black.
        
        Returns:
            Dict with format check results
        """
        try:
            cmd = ["python", "-m", "black", "--check", "corehub/", "agents/"]
            
            logger.info(f"🎨 Running format check: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            # Black returns 0 if formatting is correct, 1 if changes needed
            passed = result.returncode == 0
            
            return {
                "passed": passed,
                "returncode": result.returncode,
                "output": result.stdout,
                "error": result.stderr
            }
            
        except Exception as e:
            logger.error(f"Format check execution failed: {e}")
            return {
                "passed": False,
                "returncode": -1,
                "output": "",
                "error": str(e)
            }
    
    async def run_all_quality_checks(self) -> Dict[str, Any]:
        """
        Run all quality checks.
        
        Returns:
            Dict with all quality check results
        """
        logger.info("🔍 Running all quality checks...")
        
        # Run checks in parallel
        tests_task = asyncio.create_task(self.run_tests())
        lint_task = asyncio.create_task(self.run_lint())
        type_check_task = asyncio.create_task(self.run_type_check())
        format_check_task = asyncio.create_task(self.run_format_check())
        
        # Wait for all to complete
        tests_result, lint_result, type_result, format_result = await asyncio.gather(
            tests_task, lint_task, type_check_task, format_check_task,
            return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(tests_result, Exception):
            tests_result = {"passed": False, "error": str(tests_result)}
        if isinstance(lint_result, Exception):
            lint_result = {"passed": False, "error": str(lint_result)}
        if isinstance(type_result, Exception):
            type_result = {"passed": False, "error": str(type_result)}
        if isinstance(format_result, Exception):
            format_result = {"passed": False, "error": str(format_result)}
        
        # Calculate overall result
        overall_passed = all([
            tests_result.get("passed", False),
            lint_result.get("passed", False),
            type_result.get("passed", False),
            format_result.get("passed", False)
        ])
        
        return {
            "overall": "pass" if overall_passed else "fail",
            "tests": tests_result,
            "lint": lint_result,
            "type_check": type_result,
            "format_check": format_result
        }
    
    def _extract_coverage(self, output: str) -> Dict[str, Any]:
        """
        Extract coverage information from pytest output.
        
        Args:
            output: Pytest output
            
        Returns:
            Dict with coverage information
        """
        coverage = {}
        
        try:
            lines = output.split('\n')
            for line in lines:
                if "TOTAL" in line and "%" in line:
                    # Extract percentage
                    parts = line.split()
                    for part in parts:
                        if "%" in part:
                            coverage["total"] = float(part.replace("%", ""))
                            break
                elif "corehub" in line and "%" in line:
                    coverage["corehub"] = self._extract_percentage(line)
                elif "agents" in line and "%" in line:
                    coverage["agents"] = self._extract_percentage(line)
        except Exception as e:
            logger.debug(f"Failed to extract coverage: {e}")
        
        return coverage
    
    def _extract_percentage(self, line: str) -> float:
        """Extract percentage from a line."""
        try:
            parts = line.split()
            for part in parts:
                if "%" in part:
                    return float(part.replace("%", ""))
        except Exception:
            pass
        return 0.0
