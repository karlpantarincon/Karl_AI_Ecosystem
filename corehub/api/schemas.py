"""
Pydantic schemas for API responses optimized for React/v0.dev consumption.

These schemas ensure consistent data structure and validation for frontend integration.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum

from pydantic import BaseModel, Field, validator


# Enums for better type safety
class TaskStatus(str, Enum):
    """Task status enumeration."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class TaskType(str, Enum):
    """Task type enumeration."""
    DEV = "dev"
    OPS = "ops"
    TEST = "test"
    DOCS = "docs"


class TaskPriority(int, Enum):
    """Task priority enumeration."""
    HIGHEST = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    LOWEST = 5


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
    DEBUG = "debug"
    CONTROL = "control"


class AgentStatus(str, Enum):
    """Agent status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    ERROR = "error"


# Base schemas
class BaseResponse(BaseModel):
    """Base response schema with common fields."""
    success: bool = Field(True, description="Whether the operation was successful")
    message: Optional[str] = Field(None, description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = Field(False, description="Operation failed")
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


# Task schemas
class TaskBase(BaseModel):
    """Base task schema."""
    title: str = Field(..., description="Task title", max_length=255)
    type: TaskType = Field(..., description="Task type")
    priority: TaskPriority = Field(..., description="Task priority (1=highest, 5=lowest)")
    acceptance: List[str] = Field(default_factory=list, description="Acceptance criteria")
    estimated_hours: Optional[float] = Field(None, ge=0, description="Estimated hours to complete")
    description: Optional[str] = Field(None, description="Task description")


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, max_length=255)
    type: Optional[TaskType] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    acceptance: Optional[List[str]] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    actual_hours: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None


class TaskResponse(TaskBase):
    """Schema for task responses."""
    id: str = Field(..., description="Task ID")
    status: TaskStatus = Field(..., description="Current task status")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    actual_hours: Optional[float] = Field(None, description="Actual hours spent")

    class Config:
        from_attributes = True


class TaskListResponse(BaseResponse):
    """Schema for task list responses."""
    tasks: List[TaskResponse] = Field(..., description="List of tasks")
    pagination: Dict[str, Any] = Field(..., description="Pagination information")


# Run schemas
class RunBase(BaseModel):
    """Base run schema."""
    agent: str = Field(..., description="Agent that executed the run")
    task_id: Optional[str] = Field(None, description="Associated task ID")


class RunCreate(RunBase):
    """Schema for creating a new run."""
    pass


class RunResponse(RunBase):
    """Schema for run responses."""
    id: str = Field(..., description="Run ID")
    status: RunStatus = Field(..., description="Run status")
    created_at: datetime = Field(..., description="Run start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Run completion timestamp")
    duration_seconds: Optional[float] = Field(None, description="Run duration in seconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        from_attributes = True


# Event schemas
class EventBase(BaseModel):
    """Base event schema."""
    agent: str = Field(..., description="Agent that generated the event")
    type: EventType = Field(..., description="Event type")
    description: str = Field(..., description="Event description")


class EventCreate(EventBase):
    """Schema for creating a new event."""
    data: Optional[Dict[str, Any]] = Field(None, description="Additional event data")


class EventResponse(EventBase):
    """Schema for event responses."""
    id: str = Field(..., description="Event ID")
    created_at: datetime = Field(..., description="Event timestamp")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional event data")

    class Config:
        from_attributes = True


# Dashboard schemas
class SystemStatus(BaseModel):
    """System status schema."""
    status: str = Field(..., description="System status")
    uptime: str = Field(..., description="System uptime")
    last_check: datetime = Field(..., description="Last health check timestamp")


class TaskStats(BaseModel):
    """Task statistics schema."""
    total: int = Field(..., description="Total number of tasks")
    completed: int = Field(..., description="Number of completed tasks")
    in_progress: int = Field(..., description="Number of tasks in progress")
    todo: int = Field(..., description="Number of todo tasks")
    completion_rate: float = Field(..., description="Task completion rate percentage")


class PerformanceMetrics(BaseModel):
    """Performance metrics schema."""
    runs_24h: int = Field(..., description="Number of runs in last 24 hours")
    success_rate: float = Field(..., description="Success rate percentage")
    events_last_hour: int = Field(..., description="Number of events in last hour")


class ActivityInfo(BaseModel):
    """Activity information schema."""
    last_update: datetime = Field(..., description="Last update timestamp")
    active_agents: int = Field(..., description="Number of active agents")
    system_load: str = Field(..., description="System load level")


class DashboardOverview(BaseResponse):
    """Dashboard overview response schema."""
    system_status: SystemStatus = Field(..., description="System status information")
    tasks: TaskStats = Field(..., description="Task statistics")
    performance: PerformanceMetrics = Field(..., description="Performance metrics")
    activity: ActivityInfo = Field(..., description="Activity information")


class DailyCompletion(BaseModel):
    """Daily completion data for charts."""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    completed: int = Field(..., description="Number of tasks completed")


class AgentPerformance(BaseModel):
    """Agent performance data for charts."""
    agent: str = Field(..., description="Agent name")
    total_runs: int = Field(..., description="Total number of runs")
    success_rate: float = Field(..., description="Success rate percentage")
    successful: int = Field(..., description="Number of successful runs")
    failed: int = Field(..., description="Number of failed runs")


class SystemMetrics(BaseModel):
    """System metrics for monitoring."""
    avg_response_time: float = Field(..., description="Average response time in ms")
    error_rate: float = Field(..., description="Error rate percentage")
    throughput: float = Field(..., description="Throughput (runs per day)")
    uptime: float = Field(..., description="System uptime percentage")


class DashboardMetrics(BaseResponse):
    """Dashboard metrics response schema."""
    daily_completions: List[DailyCompletion] = Field(..., description="Daily completion data")
    agent_performance: List[AgentPerformance] = Field(..., description="Agent performance data")
    system_metrics: SystemMetrics = Field(..., description="System metrics")
    generated_at: datetime = Field(..., description="Metrics generation timestamp")


# Log schemas
class LogEntry(BaseModel):
    """Log entry schema for dashboard logs."""
    id: str = Field(..., description="Log entry ID")
    timestamp: datetime = Field(..., description="Log timestamp")
    level: str = Field(..., description="Log level")
    agent: str = Field(..., description="Agent that generated the log")
    message: str = Field(..., description="Log message")
    data: Dict[str, Any] = Field(default_factory=dict, description="Additional log data")


class LogsResponse(BaseResponse):
    """Logs response schema."""
    logs: List[LogEntry] = Field(..., description="List of log entries")
    total: int = Field(..., description="Total number of logs")
    filters: Dict[str, Optional[str]] = Field(..., description="Applied filters")


# Agent schemas
class AgentInfo(BaseModel):
    """Agent information schema."""
    name: str = Field(..., description="Agent name")
    status: AgentStatus = Field(..., description="Agent status")
    last_run: Optional[datetime] = Field(None, description="Last run timestamp")
    total_runs: int = Field(..., description="Total number of runs")
    success_rate: float = Field(..., description="Success rate percentage")


class AgentsResponse(BaseResponse):
    """Agents response schema."""
    agents: List[AgentInfo] = Field(..., description="List of agents")
    total_agents: int = Field(..., description="Total number of agents")
    active_agents: int = Field(..., description="Number of active agents")
    last_updated: datetime = Field(..., description="Last update timestamp")


class AgentControlRequest(BaseModel):
    """Agent control request schema."""
    action: str = Field(..., description="Control action", pattern="^(start|stop|pause|resume)$")


class AgentControlResponse(BaseResponse):
    """Agent control response schema."""
    agent: str = Field(..., description="Agent name")
    action: str = Field(..., description="Action performed")
    timestamp: datetime = Field(..., description="Action timestamp")


# WebSocket schemas
class WebSocketMessage(BaseModel):
    """Base WebSocket message schema."""
    type: str = Field(..., description="Message type")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    data: Dict[str, Any] = Field(..., description="Message data")


class DashboardSnapshot(WebSocketMessage):
    """Dashboard snapshot WebSocket message."""
    type: str = Field("dashboard_snapshot", description="Message type")


class TaskUpdateMessage(WebSocketMessage):
    """Task update WebSocket message."""
    type: str = Field("task_update", description="Message type")


class LogMessage(WebSocketMessage):
    """Log WebSocket message."""
    type: str = Field("logs", description="Message type")


class MetricsMessage(WebSocketMessage):
    """Metrics WebSocket message."""
    type: str = Field("metrics", description="Message type")


class SystemAlert(WebSocketMessage):
    """System alert WebSocket message."""
    type: str = Field("system_alert", description="Message type")


# Health check schemas
class ComponentHealth(BaseModel):
    """Component health schema."""
    api: str = Field(..., description="API component status")
    database: str = Field(..., description="Database component status")
    cache: str = Field(..., description="Cache component status")
    notifications: str = Field(..., description="Notifications component status")


class HealthResponse(BaseResponse):
    """Health check response schema."""
    status: str = Field(..., description="Overall system status")
    version: str = Field(..., description="System version")
    components: ComponentHealth = Field(..., description="Component health status")


# Pagination schemas
class PaginationInfo(BaseModel):
    """Pagination information schema."""
    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Number of items per page")
    offset: int = Field(..., description="Number of items to skip")
    has_more: bool = Field(..., description="Whether there are more items")


# Filter schemas
class TaskFilters(BaseModel):
    """Task filtering options."""
    status: Optional[TaskStatus] = Field(None, description="Filter by status")
    type: Optional[TaskType] = Field(None, description="Filter by type")
    priority: Optional[TaskPriority] = Field(None, description="Filter by priority")
    agent: Optional[str] = Field(None, description="Filter by agent")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date")


class LogFilters(BaseModel):
    """Log filtering options."""
    level: Optional[str] = Field(None, description="Filter by log level")
    agent: Optional[str] = Field(None, description="Filter by agent")
    since: Optional[datetime] = Field(None, description="Filter by timestamp")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of logs")


# Validation functions
def validate_task_priority(priority: int) -> int:
    """Validate task priority is between 1 and 5."""
    if not 1 <= priority <= 5:
        raise ValueError("Priority must be between 1 and 5")
    return priority


def validate_estimated_hours(hours: Optional[float]) -> Optional[float]:
    """Validate estimated hours is non-negative."""
    if hours is not None and hours < 0:
        raise ValueError("Estimated hours must be non-negative")
    return hours


# Custom validators for TaskResponse
@validator('actual_hours', pre=True, always=True)
def validate_actual_hours(cls, v):
    """Validate actual hours is non-negative."""
    if v is not None and v < 0:
        raise ValueError("Actual hours must be non-negative")
    return v


@validator('completion_rate', pre=True, always=True)
def validate_completion_rate(cls, v):
    """Validate completion rate is between 0 and 100."""
    if not 0 <= v <= 100:
        raise ValueError("Completion rate must be between 0 and 100")
    return round(v, 2)


@validator('success_rate', pre=True, always=True)
def validate_success_rate(cls, v):
    """Validate success rate is between 0 and 100."""
    if not 0 <= v <= 100:
        raise ValueError("Success rate must be between 0 and 100")
    return round(v, 2)
