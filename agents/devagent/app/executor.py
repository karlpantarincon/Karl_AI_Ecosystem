"""
DevAgent Executor - Core execution logic.

This module handles the main execution flow of the DevAgent.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from loguru import logger

from agents.devagent.tools.corehub_client import CoreHubClient
from agents.devagent.tools.git_wrapper import GitWrapper
from agents.devagent.tools.code_runner import CodeRunner
from agents.devagent.tools.scaffold import ScaffoldGenerator


class DevAgentExecutor:
    """Main executor for DevAgent tasks."""
    
    def __init__(self, client: CoreHubClient):
        """
        Initialize DevAgent executor.
        
        Args:
            client: CoreHub API client
        """
        self.client = client
        self.git = GitWrapper()
        self.code_runner = CodeRunner()
        self.scaffold = ScaffoldGenerator()
        
    async def execute_task(self) -> Optional[Dict[str, Any]]:
        """
        Execute a single task from the kanban.
        
        Returns:
            Dict with execution result or None if no task available
        """
        try:
            # Fetch next task
            task = await self.client.get_next_task("devagent")
            if not task:
                logger.info("No tasks available")
                return None
            
            logger.info(f"📋 Processing task: {task['id']} - {task['title']}")
            
            # Execute the task
            result = await self._execute_single_task(task)
            
            # Log completion event
            await self.client.log_event("devagent", "task_completed", {
                "task_id": task["id"],
                "result": result
            })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Task execution failed: {e}")
            
            # Log error event
            await self.client.log_event("devagent", "task_failed", {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            raise
    
    async def execute_specific_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Execute a specific task by ID.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Dict with execution result or None if task not found
        """
        try:
            # Get specific task
            task = await self.client.get_task(task_id)
            if not task:
                logger.warning(f"Task {task_id} not found")
                return None
            
            logger.info(f"🎯 Processing specific task: {task['id']} - {task['title']}")
            
            # Execute the task
            result = await self._execute_single_task(task)
            
            # Log completion event
            await self.client.log_event("devagent", "specific_task_completed", {
                "task_id": task["id"],
                "result": result
            })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Specific task execution failed: {e}")
            
            # Log error event
            await self.client.log_event("devagent", "specific_task_failed", {
                "task_id": task_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            raise
    
    async def _execute_single_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single task.
        
        Args:
            task: Task data from kanban
            
        Returns:
            Dict with execution result
        """
        task_id = task["id"]
        task_title = task["title"]
        task_type = task.get("type", "dev")
        acceptance_criteria = task.get("acceptance", [])
        
        logger.info(f"🔧 Executing task {task_id}: {task_title}")
        
        # Start timing
        start_time = datetime.utcnow()
        
        try:
            # Generate implementation plan
            plan = await self._generate_plan(task)
            logger.info(f"📝 Plan generated: {len(plan)} steps")
            
            # Execute plan
            actions = await self._execute_plan(plan, task)
            logger.info(f"⚡ Actions executed: {len(actions)} files modified")
            
            # Run quality checks
            quality_results = await self._run_quality_checks()
            logger.info(f"✅ Quality checks: {quality_results}")
            
            # Generate result summary
            result = await self._generate_result(task, plan, actions, quality_results)
            
            # Create PR (simulated)
            pr_info = await self._create_pr(task, actions)
            result["pr"] = pr_info
            
            # Calculate execution time
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            result["duration_sec"] = duration
            
            # Update task status
            await self.client.update_task_status(task_id, "done")
            
            logger.success(f"✅ Task {task_id} completed in {duration:.1f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Task {task_id} failed: {e}")
            
            # Update task status to failed
            await self.client.update_task_status(task_id, "blocked")
            
            raise
    
    async def _generate_plan(self, task: Dict[str, Any]) -> list:
        """
        Generate implementation plan for a task.
        
        Args:
            task: Task data
            
        Returns:
            List of plan steps
        """
        task_type = task.get("type", "dev")
        acceptance_criteria = task.get("acceptance", [])
        
        # Simple plan generation based on task type
        if task_type == "dev":
            plan = [
                f"Analyze requirements: {task['title']}",
                f"Implement solution for: {', '.join(acceptance_criteria)}",
                "Create/update code files",
                "Write tests",
                "Update documentation",
                "Run quality checks"
            ]
        elif task_type == "ops":
            plan = [
                f"Analyze operational requirements: {task['title']}",
                f"Implement solution for: {', '.join(acceptance_criteria)}",
                "Create/update configuration",
                "Write operational tests",
                "Update runbooks",
                "Run quality checks"
            ]
        else:
            plan = [
                f"Analyze requirements: {task['title']}",
                f"Implement solution for: {', '.join(acceptance_criteria)}",
                "Create/update files",
                "Run quality checks"
            ]
        
        return plan
    
    async def _execute_plan(self, plan: list, task: Dict[str, Any]) -> list:
        """
        Execute the implementation plan.
        
        Args:
            plan: List of plan steps
            task: Task data
            
        Returns:
            List of actions taken
        """
        actions = []
        
        for step in plan:
            logger.info(f"🔄 Executing step: {step}")
            
            # Simulate step execution
            if "Implement solution" in step:
                # Generate code files
                files_created = await self._implement_solution(task)
                actions.extend(files_created)
                
            elif "Write tests" in step:
                # Generate test files
                test_files = await self._create_tests(task)
                actions.extend(test_files)
                
            elif "Update documentation" in step:
                # Update docs
                doc_files = await self._update_documentation(task)
                actions.extend(doc_files)
            
            # Simulate some processing time
            await asyncio.sleep(0.1)
        
        return actions
    
    async def _implement_solution(self, task: Dict[str, Any]) -> list:
        """Implement the solution for a task."""
        task_id = task["id"]
        task_type = task.get("type", "dev")
        
        # Generate appropriate files based on task type
        if task_type == "dev":
            files = [
                f"corehub/api/routes/{task_id.lower()}.py",
                f"corehub/services/{task_id.lower()}_service.py"
            ]
        elif task_type == "ops":
            files = [
                f"scripts/{task_id.lower()}.py",
                f"configs/{task_id.lower()}.yaml"
            ]
        else:
            files = [
                f"misc/{task_id.lower()}.py"
            ]
        
        # Simulate file creation
        for file_path in files:
            logger.info(f"📝 Creating file: {file_path}")
        
        return files
    
    async def _create_tests(self, task: Dict[str, Any]) -> list:
        """Create test files for a task."""
        task_id = task["id"]
        
        test_files = [
            f"corehub/tests/test_{task_id.lower()}.py"
        ]
        
        # Simulate test file creation
        for file_path in test_files:
            logger.info(f"🧪 Creating test: {file_path}")
        
        return test_files
    
    async def _update_documentation(self, task: Dict[str, Any]) -> list:
        """Update documentation for a task."""
        doc_files = [
            "README.md",
            "docs/api.md"
        ]
        
        # Simulate doc updates
        for file_path in doc_files:
            logger.info(f"📚 Updating docs: {file_path}")
        
        return doc_files
    
    async def _run_quality_checks(self) -> Dict[str, Any]:
        """
        Run quality checks (tests, lint, etc.).
        
        Returns:
            Dict with quality check results
        """
        logger.info("🔍 Running quality checks...")
        
        # Simulate running tests
        test_results = await self.code_runner.run_tests()
        
        # Simulate running lint
        lint_results = await self.code_runner.run_lint()
        
        # Simulate running type check
        type_results = await self.code_runner.run_type_check()
        
        return {
            "tests": test_results,
            "lint": lint_results,
            "type_check": type_results,
            "overall": "pass" if all([
                test_results.get("passed", False),
                lint_results.get("passed", False),
                type_results.get("passed", False)
            ]) else "fail"
        }
    
    async def _generate_result(self, task: Dict[str, Any], plan: list, actions: list, quality_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate result summary.
        
        Args:
            task: Task data
            plan: Implementation plan
            actions: Actions taken
            quality_results: Quality check results
            
        Returns:
            Dict with result summary
        """
        return {
            "task_id": task["id"],
            "task_title": task["title"],
            "status": "completed",
            "plan_steps": len(plan),
            "files_modified": len(actions),
            "quality_checks": quality_results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _create_pr(self, task: Dict[str, Any], actions: list) -> Dict[str, Any]:
        """
        Create a pull request (simulated).
        
        Args:
            task: Task data
            actions: Actions taken
            
        Returns:
            Dict with PR information
        """
        task_id = task["id"]
        task_title = task["title"]
        
        # Create branch
        branch_name = f"feat/{task_id.lower()}-{task_title.lower().replace(' ', '-')}"
        await self.git.create_branch(branch_name)
        
        # Create commit
        commit_message = f"feat: {task_title}\n\n- Task ID: {task_id}\n- Files: {', '.join(actions)}"
        await self.git.commit(commit_message, actions)
        
        # Generate PR file
        pr_info = await self.git.generate_pr_file(task_id, {
            "title": task_title,
            "branch": branch_name,
            "files": actions,
            "commit": commit_message
        })
        
        return pr_info
