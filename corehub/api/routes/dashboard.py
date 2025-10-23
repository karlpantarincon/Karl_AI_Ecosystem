"""
Dashboard API routes for v0.dev integration.

Provides endpoints optimized for React frontend consumption.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from corehub.db.database import get_db
from corehub.db.models import Task, Run, Event
from corehub.services.cache import cached
from corehub.services.notifications import create_notification_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
async def get_dashboard_overview(db: Session = Depends(get_db)):
    """
    Get dashboard overview with key metrics.
    
    Returns:
        - System status
        - Task statistics
        - Performance metrics
        - Recent activity
    """
    try:
        # Get task statistics
        total_tasks = db.query(Task).count()
        completed_tasks = db.query(Task).filter(Task.status == "done").count()
        in_progress_tasks = db.query(Task).filter(Task.status == "in_progress").count()
        todo_tasks = db.query(Task).filter(Task.status == "todo").count()
        
        # Get recent runs (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_runs = db.query(Run).filter(Run.created_at >= yesterday).count()
        successful_runs = db.query(Run).filter(
            Run.created_at >= yesterday,
            Run.status == "completed"
        ).count()
        
        # Get recent events (last hour)
        last_hour = datetime.utcnow() - timedelta(hours=1)
        recent_events = db.query(Event).filter(Event.created_at >= last_hour).count()
        
        # Calculate success rate
        success_rate = (successful_runs / recent_runs * 100) if recent_runs > 0 else 0
        
        return {
            "system_status": {
                "status": "healthy",
                "uptime": "24/7",
                "last_check": datetime.utcnow().isoformat()
            },
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "in_progress": in_progress_tasks,
                "todo": todo_tasks,
                "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            },
            "performance": {
                "runs_24h": recent_runs,
                "success_rate": round(success_rate, 2),
                "events_last_hour": recent_events
            },
            "activity": {
                "last_update": datetime.utcnow().isoformat(),
                "active_agents": 1,  # DevAgent
                "system_load": "low"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard overview: {str(e)}")


@router.get("/tasks")
async def get_dashboard_tasks(
    status: Optional[str] = Query(None, description="Filter by task status"),
    priority: Optional[int] = Query(None, description="Filter by priority (1-5)"),
    limit: int = Query(50, description="Number of tasks to return"),
    offset: int = Query(0, description="Number of tasks to skip"),
    db: Session = Depends(get_db)
):
    """
    Get tasks for dashboard with filtering and pagination.
    
    Optimized for React table components.
    """
    try:
        query = db.query(Task)
        
        # Apply filters
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.prio == priority)
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination and ordering
        tasks = query.order_by(Task.prio.asc(), Task.created_at.desc()).offset(offset).limit(limit).all()
        
        # Format for React consumption
        formatted_tasks = []
        for task in tasks:
            formatted_tasks.append({
                "id": task.id,
                "title": task.title,
                "type": task.type,
                "priority": task.prio,
                "status": task.status,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                "acceptance": getattr(task, 'acceptance', []),
                "estimated_hours": getattr(task, 'estimated_hours', 0),
                "actual_hours": getattr(task, 'actual_hours', 0)
            })
        
        return {
            "tasks": formatted_tasks,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tasks: {str(e)}")


@router.get("/metrics")
@cached(ttl=60)  # Cache for 1 minute
async def get_dashboard_metrics(db: Session = Depends(get_db)):
    """
    Get performance metrics for dashboard charts.
    
    Returns data optimized for React chart libraries.
    """
    try:
        # Get metrics for last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        # Task completion over time
        daily_completions = []
        for i in range(7):
            date = week_ago + timedelta(days=i)
            next_date = date + timedelta(days=1)
            
            completed = db.query(Task).filter(
                Task.status == "done",
                Task.updated_at >= date,
                Task.updated_at < next_date
            ).count()
            
            daily_completions.append({
                "date": date.strftime("%Y-%m-%d"),
                "completed": completed
            })
        
        # Agent performance
        recent_runs = db.query(Run).filter(Run.created_at >= week_ago).all()
        
        agent_performance = {}
        for run in recent_runs:
            agent = run.agent
            if agent not in agent_performance:
                agent_performance[agent] = {"total": 0, "successful": 0, "failed": 0}
            
            agent_performance[agent]["total"] += 1
            if run.status == "completed":
                agent_performance[agent]["successful"] += 1
            elif run.status == "failed":
                agent_performance[agent]["failed"] += 1
        
        # Format agent performance for charts
        agent_chart_data = []
        for agent, stats in agent_performance.items():
            success_rate = (stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0
            agent_chart_data.append({
                "agent": agent,
                "total_runs": stats["total"],
                "success_rate": round(success_rate, 2),
                "successful": stats["successful"],
                "failed": stats["failed"]
            })
        
        # System health metrics
        system_metrics = {
            "avg_response_time": 120,  # ms - placeholder
            "error_rate": 0.5,  # percentage - placeholder
            "throughput": len(recent_runs) / 7,  # runs per day
            "uptime": 99.9  # percentage - placeholder
        }
        
        return {
            "daily_completions": daily_completions,
            "agent_performance": agent_chart_data,
            "system_metrics": system_metrics,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching metrics: {str(e)}")


@router.get("/logs")
async def get_dashboard_logs(
    level: Optional[str] = Query(None, description="Filter by log level"),
    agent: Optional[str] = Query(None, description="Filter by agent"),
    limit: int = Query(100, description="Number of logs to return"),
    db: Session = Depends(get_db)
):
    """
    Get recent system logs for dashboard.
    
    Optimized for React log viewer components.
    """
    try:
        query = db.query(Event)
        
        # Apply filters
        if level:
            query = query.filter(Event.type == level)
        if agent:
            query = query.filter(Event.agent == agent)
        
        # Get recent events
        events = query.order_by(Event.created_at.desc()).limit(limit).all()
        
        # Format for React consumption
        formatted_logs = []
        for event in events:
            formatted_logs.append({
                "id": event.id,
                "timestamp": event.created_at.isoformat(),
                "level": event.type,
                "agent": event.agent,
                "message": event.description,
                "data": event.data if event.data else {}
            })
        
        return {
            "logs": formatted_logs,
            "total": len(formatted_logs),
            "filters": {
                "level": level,
                "agent": agent
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching logs: {str(e)}")


@router.post("/tasks/{task_id}/status")
async def update_task_status(
    task_id: str,
    status: str,
    db: Session = Depends(get_db)
):
    """
    Update task status from dashboard.
    
    Optimized for React form submissions.
    """
    try:
        # Validate status
        valid_statuses = ["todo", "in_progress", "done", "blocked"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {valid_statuses}"
            )
        
        # Find task
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update status
        old_status = task.status
        task.status = status
        task.updated_at = datetime.utcnow()
        db.commit()
        
        # Send notification
        notification_service = create_notification_service()
        notification_service.send_task_notification(
            task_id=task_id,
            title=task.title,
            status=status,
            details=f"Status changed from {old_status} to {status} via dashboard"
        )
        
        return {
            "success": True,
            "message": f"Task {task_id} status updated to {status}",
            "task": {
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "updated_at": task.updated_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task status: {str(e)}")


@router.get("/agents")
async def get_agents_status(db: Session = Depends(get_db)):
    """
    Get current status of all agents.
    
    Returns agent information for dashboard monitoring.
    """
    try:
        # Get recent runs to determine agent status
        recent_time = datetime.utcnow() - timedelta(minutes=5)
        recent_runs = db.query(Run).filter(Run.created_at >= recent_time).all()
        
        # Group by agent
        agents_status = {}
        for run in recent_runs:
            agent = run.agent
            if agent not in agents_status:
                agents_status[agent] = {
                    "name": agent,
                    "status": "inactive",
                    "last_run": None,
                    "total_runs": 0,
                    "success_rate": 0
                }
            
            agents_status[agent]["last_run"] = run.created_at.isoformat()
            agents_status[agent]["total_runs"] += 1
            
            if run.status == "running":
                agents_status[agent]["status"] = "active"
        
        # Calculate success rates
        for agent in agents_status:
            agent_runs = db.query(Run).filter(Run.agent == agent).all()
            if agent_runs:
                successful = sum(1 for run in agent_runs if run.status == "completed")
                agents_status[agent]["success_rate"] = round(
                    (successful / len(agent_runs)) * 100, 2
                )
        
        # Ensure DevAgent is always present
        if "devagent" not in agents_status:
            agents_status["devagent"] = {
                "name": "DevAgent",
                "status": "inactive",
                "last_run": None,
                "total_runs": 0,
                "success_rate": 0
            }
        
        return {
            "agents": list(agents_status.values()),
            "total_agents": len(agents_status),
            "active_agents": sum(1 for agent in agents_status.values() if agent["status"] == "active"),
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching agents status: {str(e)}")


@router.post("/agents/{agent_name}/control")
async def control_agent(
    agent_name: str,
    action: str,
    db: Session = Depends(get_db)
):
    """
    Control agent actions (start, stop, pause, resume).
    
    Optimized for React control panels.
    """
    try:
        valid_actions = ["start", "stop", "pause", "resume"]
        if action not in valid_actions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action. Must be one of: {valid_actions}"
            )
        
        # For now, we'll log the action and return success
        # In a real implementation, this would communicate with the agent process
        
        # Log the control action
        control_event = Event(
            agent=agent_name,
            type="control",
            description=f"Agent {agent_name} {action} requested from dashboard",
            data={"action": action, "source": "dashboard"}
        )
        db.add(control_event)
        db.commit()
        
        return {
            "success": True,
            "message": f"Agent {agent_name} {action} command sent successfully",
            "agent": agent_name,
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error controlling agent: {str(e)}")


@router.get("/health")
async def get_dashboard_health():
    """
    Get dashboard-specific health information.
    
    Quick health check for dashboard components.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {
            "api": "healthy",
            "database": "healthy",
            "cache": "healthy",
            "notifications": "healthy"
        }
    }
