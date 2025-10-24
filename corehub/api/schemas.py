"""
Simple schemas for API responses without Pydantic.
Optimized for cloud deployment without compilation issues.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum


# Enums for better type safety
class TaskStatus(str, Enum):
    """Task status enumeration."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class RunStatus(str, Enum):
    """Run status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EventType(str, Enum):
    """Event type enumeration."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


# Simple response schemas without Pydantic
def create_task_response(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a task response dictionary."""
    return {
        "id": task_data.get("id"),
        "title": task_data.get("title"),
        "description": task_data.get("description"),
        "status": task_data.get("status"),
        "priority": task_data.get("priority"),
        "created_at": task_data.get("created_at").isoformat() if task_data.get("created_at") else None,
        "updated_at": task_data.get("updated_at").isoformat() if task_data.get("updated_at") else None,
        "agent_id": task_data.get("agent_id"),
        "run_id": task_data.get("run_id")
    }


def create_run_response(run_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a run response dictionary."""
    return {
        "id": run_data.get("id"),
        "task_id": run_data.get("task_id"),
        "status": run_data.get("status"),
        "started_at": run_data.get("started_at").isoformat() if run_data.get("started_at") else None,
        "completed_at": run_data.get("completed_at").isoformat() if run_data.get("completed_at") else None,
        "output": run_data.get("output"),
        "error": run_data.get("error")
    }


def create_event_response(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create an event response dictionary."""
    return {
        "id": event_data.get("id"),
        "type": event_data.get("type"),
        "message": event_data.get("message"),
        "timestamp": event_data.get("timestamp").isoformat() if event_data.get("timestamp") else None,
        "agent_id": event_data.get("agent_id"),
        "task_id": event_data.get("task_id"),
        "run_id": event_data.get("run_id")
    }


def create_dashboard_overview_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a dashboard overview response."""
    return {
        "total_tasks": data.get("total_tasks", 0),
        "active_tasks": data.get("active_tasks", 0),
        "completed_tasks": data.get("completed_tasks", 0),
        "total_runs": data.get("total_runs", 0),
        "successful_runs": data.get("successful_runs", 0),
        "failed_runs": data.get("failed_runs", 0),
        "active_agents": data.get("active_agents", 0),
        "system_health": data.get("system_health", "healthy")
    }


def create_agent_response(agent_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create an agent response dictionary."""
    return {
        "id": agent_data.get("id"),
        "name": agent_data.get("name"),
        "status": agent_data.get("status"),
        "last_heartbeat": agent_data.get("last_heartbeat").isoformat() if agent_data.get("last_heartbeat") else None,
        "current_task": agent_data.get("current_task"),
        "total_tasks": agent_data.get("total_tasks", 0)
    }


def create_metrics_response(metrics_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a metrics response dictionary."""
    return {
        "cpu_usage": metrics_data.get("cpu_usage", 0),
        "memory_usage": metrics_data.get("memory_usage", 0),
        "disk_usage": metrics_data.get("disk_usage", 0),
        "active_connections": metrics_data.get("active_connections", 0),
        "requests_per_minute": metrics_data.get("requests_per_minute", 0),
        "timestamp": datetime.utcnow().isoformat()
    }


def create_log_response(log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a log response dictionary."""
    return {
        "id": log_data.get("id"),
        "level": log_data.get("level"),
        "message": log_data.get("message"),
        "timestamp": log_data.get("timestamp").isoformat() if log_data.get("timestamp") else None,
        "source": log_data.get("source"),
        "agent_id": log_data.get("agent_id")
    }


# Simple validation functions
def validate_task_status(status: str) -> bool:
    """Validate task status."""
    return status in [e.value for e in TaskStatus]


def validate_run_status(status: str) -> bool:
    """Validate run status."""
    return status in [e.value for e in RunStatus]


def validate_event_type(event_type: str) -> bool:
    """Validate event type."""
    return event_type in [e.value for e in EventType]


# Simple request validation
def validate_task_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean task request data."""
    if not data.get("title"):
        raise ValueError("Title is required")
    
    return {
        "title": data.get("title"),
        "description": data.get("description", ""),
        "priority": data.get("priority", 1),
        "agent_id": data.get("agent_id")
    }


def validate_agent_control_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate agent control request."""
    action = data.get("action")
    if action not in ["start", "stop", "pause", "resume"]:
        raise ValueError("Invalid action. Must be one of: start, stop, pause, resume")
    
    return {"action": action}