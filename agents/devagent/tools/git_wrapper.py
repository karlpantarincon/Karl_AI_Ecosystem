"""
Git operations wrapper for DevAgent.

This module provides Git functionality for the DevAgent including
branch creation, commits, and PR generation (simulated).
"""

import os
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional

from loguru import logger


class GitWrapper:
    """Git operations wrapper."""
    
    def __init__(self, repo_path: str = "."):
        """
        Initialize Git wrapper.
        
        Args:
            repo_path: Path to Git repository
        """
        self.repo_path = repo_path
        self.pr_dir = os.path.join(repo_path, "reports", "prs")
        os.makedirs(self.pr_dir, exist_ok=True)
    
    async def create_branch(self, branch_name: str) -> bool:
        """
        Create a new Git branch.
        
        Args:
            branch_name: Name of the branch to create
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if branch already exists
            result = subprocess.run(
                ["git", "branch", "--list", branch_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                logger.info(f"Branch {branch_name} already exists")
                return True
            
            # Create new branch
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Created branch: {branch_name}")
                return True
            else:
                logger.error(f"Failed to create branch: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Git branch creation failed: {e}")
            return False
    
    async def commit(self, message: str, files: List[str]) -> bool:
        """
        Create a Git commit.
        
        Args:
            message: Commit message
            files: List of files to commit
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add files to staging
            for file_path in files:
                if os.path.exists(file_path):
                    subprocess.run(
                        ["git", "add", file_path],
                        cwd=self.repo_path,
                        capture_output=True
                    )
                    logger.debug(f"Added to staging: {file_path}")
                else:
                    logger.warning(f"File not found: {file_path}")
            
            # Create commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Created commit: {message[:50]}...")
                return True
            else:
                logger.error(f"Failed to create commit: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Git commit failed: {e}")
            return False
    
    async def generate_pr_file(self, task_id: str, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a PR file (simulated).
        
        Args:
            task_id: Task identifier
            pr_data: PR data including title, branch, files, etc.
            
        Returns:
            Dict with PR information
        """
        try:
            pr_filename = f"PR-{task_id}.md"
            pr_path = os.path.join(self.pr_dir, pr_filename)
            
            # Generate PR content
            pr_content = self._generate_pr_content(task_id, pr_data)
            
            # Write PR file
            with open(pr_path, "w", encoding="utf-8") as f:
                f.write(pr_content)
            
            logger.info(f"📝 Generated PR file: {pr_path}")
            
            return {
                "pr_id": f"PR-{task_id}",
                "file_path": pr_path,
                "branch": pr_data.get("branch", ""),
                "title": pr_data.get("title", ""),
                "files": pr_data.get("files", []),
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"PR generation failed: {e}")
            return {}
    
    def _generate_pr_content(self, task_id: str, pr_data: Dict[str, Any]) -> str:
        """
        Generate PR content in markdown format.
        
        Args:
            task_id: Task identifier
            pr_data: PR data
            
        Returns:
            PR content as string
        """
        title = pr_data.get("title", f"Task {task_id}")
        branch = pr_data.get("branch", f"feat/{task_id.lower()}")
        files = pr_data.get("files", [])
        commit = pr_data.get("commit", "")
        
        content = f"""# PR: {task_id} - {title}

## Descripción
Implementación de la tarea {task_id} del kanban.

## Cambios
- {title}
- Archivos modificados: {len(files)}

## Archivos modificados
{chr(10).join([f"- {file}" for file in files])}

## Commit
```
{commit}
```

## Tests
- [ ] Tests unitarios pasando
- [ ] Tests de integración pasando
- [ ] Coverage ≥ 70%
- [ ] Lint clean

## Review checklist
- [ ] Lógica correcta
- [ ] Tests adecuados
- [ ] Docs actualizadas
- [ ] Performance aceptable

## Métricas
- Tarea: {task_id}
- Branch: {branch}
- Archivos: {len(files)}
- Creado: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

---
*PR generado automáticamente por DevAgent*
"""
        
        return content
    
    async def get_current_branch(self) -> Optional[str]:
        """
        Get current Git branch.
        
        Returns:
            Current branch name or None if failed
        """
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"Failed to get current branch: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Git branch check failed: {e}")
            return None
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get Git repository status.
        
        Returns:
            Dict with Git status information
        """
        try:
            # Get status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Get current branch
            branch = await self.get_current_branch()
            
            return {
                "branch": branch,
                "modified_files": len([line for line in status_lines if line.startswith('M')]),
                "untracked_files": len([line for line in status_lines if line.startswith('??')]),
                "staged_files": len([line for line in status_lines if line.startswith('A') or line.startswith('M')]),
                "status_lines": status_lines
            }
            
        except Exception as e:
            logger.error(f"Git status check failed: {e}")
            return {
                "branch": None,
                "modified_files": 0,
                "untracked_files": 0,
                "staged_files": 0,
                "status_lines": []
            }
