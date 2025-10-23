"""
Task management endpoints.

Handles task retrieval from kanban and task status updates.
"""

import json
import os
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from corehub.db.database import get_db
from corehub.db.models import Task

router = APIRouter()


def load_kanban() -> Dict[str, Any]:
    """
    Load kanban configuration from file.
    
    Returns:
        Dict containing kanban configuration
        
    Raises:
        HTTPException: If kanban file cannot be loaded
    """
    kanban_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "configs", "kanban.json")
    
    try:
        with open(kanban_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Kanban configuration not found"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Invalid kanban configuration format"
        )


@router.post("/next")
async def get_next_task(
    request: Dict[str, str],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get next prioritized task for an agent.
    
    Args:
        request: Request body with agent name
        db: Database session dependency
        
    Returns:
        Dict containing the next task to work on
        
    Raises:
        HTTPException: If no tasks available or agent not specified
    """
    agent = request.get("agent")
    if not agent:
        raise HTTPException(
            status_code=400,
            detail="Agent name is required"
        )
    
    # Load kanban configuration
    kanban = load_kanban()
    
    # Find next available task
    available_tasks = [
        task for task in kanban.get("tasks", [])
        if task.get("status") == "todo"
    ]
    
    if not available_tasks:
        return {
            "task": None,
            "message": "No tasks available",
            "agent": agent
        }
    
    # Sort by priority (lower number = higher priority)
    available_tasks.sort(key=lambda x: x.get("prio", 999))
    next_task = available_tasks[0]
    
    # Update task status to in_progress
    next_task["status"] = "in_progress"
    
    # Save updated kanban
    kanban_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "configs", "kanban.json")
    with open(kanban_path, "w", encoding="utf-8") as f:
        json.dump(kanban, f, indent=2, ensure_ascii=False)
    
    return {
        "task": next_task,
        "agent": agent,
        "timestamp": next_task.get("updated_at", "unknown")
    }


@router.get("/")
async def list_tasks(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    List all tasks with optional status filter.
    
    Args:
        status: Optional status filter (todo, in_progress, done, blocked)
        db: Database session dependency
        
    Returns:
        Dict containing list of tasks
    """
    kanban = load_kanban()
    tasks = kanban.get("tasks", [])
    
    if status:
        tasks = [task for task in tasks if task.get("status") == status]
    
    return {
        "tasks": tasks,
        "total": len(tasks),
        "filter": {"status": status} if status else None
    }


@router.get("/{task_id}")
async def get_task(
    task_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get specific task by ID.
    
    Args:
        task_id: Task identifier
        db: Database session dependency
        
    Returns:
        Dict containing task details
        
    Raises:
        HTTPException: If task not found
    """
    kanban = load_kanban()
    tasks = kanban.get("tasks", [])
    
    task = next((t for t in tasks if t.get("id") == task_id), None)
    
    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )
    
    return {
        "task": task
    }


@router.put("/{task_id}/status")
async def update_task_status(
    task_id: str,
    request: Dict[str, str],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update task status.
    
    Args:
        task_id: Task identifier
        request: Request body with new status
        db: Database session dependency
        
    Returns:
        Dict containing updated task
        
    Raises:
        HTTPException: If task not found or invalid status
    """
    new_status = request.get("status")
    if not new_status:
        raise HTTPException(
            status_code=400,
            detail="Status is required"
        )
    
    valid_statuses = ["todo", "in_progress", "done", "blocked"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    # Load and update kanban
    kanban = load_kanban()
    tasks = kanban.get("tasks", [])
    
    task = next((t for t in tasks if t.get("id") == task_id), None)
    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )
    
    # Update task
    task["status"] = new_status
    task["updated_at"] = "2025-10-22T20:45:00Z"  # TODO: Use actual timestamp
    
    # Save updated kanban
    kanban_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "configs", "kanban.json")
    with open(kanban_path, "w", encoding="utf-8") as f:
        json.dump(kanban, f, indent=2, ensure_ascii=False)
    
    return {
        "task": task,
        "message": f"Task {task_id} status updated to {new_status}"
    }
