"""
APScheduler jobs for CoreHub.

This module contains all scheduled jobs:
- Daily report generation
- Health checks
- System maintenance
"""

import os
from datetime import datetime, date
from typing import Dict, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import sessionmaker

from corehub.db.database import engine, check_db_connection
from corehub.db.models import Event, Task, Run, Flag

# Create session factory for scheduler
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Global scheduler instance
scheduler = None


def start_scheduler() -> None:
    """Start the APScheduler with all configured jobs."""
    global scheduler
    
    if scheduler is not None:
        return  # Already started
    
    scheduler = AsyncIOScheduler()
    
    # Daily report job - 9:00 AM Lima time
    scheduler.add_job(
        daily_report_job,
        CronTrigger(hour=9, minute=0, timezone="America/Lima"),
        id="daily_report",
        name="Daily Report Generation",
        replace_existing=True
    )
    
    # Health check job - every 5 minutes
    scheduler.add_job(
        health_check_job,
        IntervalTrigger(minutes=5),
        id="health_check",
        name="System Health Check",
        replace_existing=True
    )
    
    scheduler.start()
    print("Scheduler started with jobs: daily_report, health_check")


def stop_scheduler() -> None:
    """Stop the APScheduler."""
    global scheduler
    
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        print("Scheduler stopped")


async def daily_report_job() -> None:
    """
    Generate daily report job.
    
    This job runs every day at 9:00 AM Lima time and generates
    a daily report with metrics from the previous day.
    """
    print("Running daily report job...")
    
    try:
        # Get yesterday's date
        yesterday = date.today()
        
        # Generate report content
        report_content = await _generate_daily_report_content(yesterday)
        
        # Save report to file
        reports_dir = os.path.join(os.path.dirname(__file__), "..", "..", "reports", "daily")
        os.makedirs(reports_dir, exist_ok=True)
        
        report_filename = f"{yesterday}.md"
        report_path = os.path.join(reports_dir, report_filename)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        # Log the event
        await _log_event("system", "daily_report_generated", {
            "date": yesterday.isoformat(),
            "file_path": report_path
        })
        
        print(f"Daily report generated: {report_path}")
        
    except Exception as e:
        print(f"Daily report job failed: {e}")
        await _log_event("system", "daily_report_failed", {
            "error": str(e),
            "date": yesterday.isoformat()
        })


async def health_check_job() -> None:
    """
    System health check job.
    
    This job runs every 5 minutes and checks:
    - Database connectivity
    - Pending tasks
    - System flags
    """
    print("Running health check job...")
    
    try:
        # Check database connection
        db_healthy = check_db_connection()
        
        # Get system status
        with SessionLocal() as db:
            # Check for system pause flag
            pause_flag = db.query(Flag).filter(Flag.key == "system_paused").first()
            is_paused = pause_flag and pause_flag.value.lower() == "true"
            
            # Count pending tasks
            pending_tasks = db.query(Task).filter(Task.status == "todo").count()
            
            # Count recent events
            recent_events = db.query(Event).filter(
                Event.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            ).count()
        
        # Determine health status
        health_status = "healthy" if db_healthy and not is_paused else "degraded"
        
        # Log health check event
        await _log_event("system", "health_check", {
            "status": health_status,
            "database_healthy": db_healthy,
            "system_paused": is_paused,
            "pending_tasks": pending_tasks,
            "recent_events": recent_events
        })
        
        if health_status == "degraded":
            print(f"Health check: {health_status} (DB: {db_healthy}, Paused: {is_paused})")
        else:
            print(f"Health check: {health_status}")
            
    except Exception as e:
        print(f"Health check job failed: {e}")
        await _log_event("system", "health_check_failed", {
            "error": str(e)
        })


async def _generate_daily_report_content(report_date: date) -> str:
    """
    Generate daily report content.
    
    Args:
        report_date: Date for the report
        
    Returns:
        str: Report content in markdown format
    """
    with SessionLocal() as db:
        # Get tasks completed on the report date
        start_datetime = datetime.combine(report_date, datetime.min.time())
        end_datetime = datetime.combine(report_date, datetime.min.time()).replace(day=report_date.day + 1)
        
        completed_tasks = db.query(Task).filter(
            Task.status == "done",
            Task.updated_at >= start_datetime,
            Task.updated_at < end_datetime
        ).all()
        
        # Get runs for the report date
        runs = db.query(Run).filter(
            Run.created_at >= start_datetime,
            Run.created_at < end_datetime
        ).all()
        
        # Get events for the report date
        events = db.query(Event).filter(
            Event.created_at >= start_datetime,
            Event.created_at < end_datetime
        ).all()
        
        # Calculate metrics
        total_cost = sum(run.cost_usd or 0 for run in runs)
        total_duration = sum(run.duration_sec or 0 for run in runs)
        successful_runs = len([r for r in runs if r.status == "completed"])
        success_rate = (successful_runs / len(runs) * 100) if runs else 0
        
        # Generate report content
        report_content = f"""# Resumen Diario - {report_date}

## Tareas Completadas ({len(completed_tasks)})
{chr(10).join([f"- [{task.id}] {task.title}" for task in completed_tasks]) if completed_tasks else "- No hay tareas completadas"}

## Métricas del Día
- Total de runs: {len(runs)}
- Runs exitosos: {successful_runs}
- Tasa de éxito: {success_rate:.1f}%
- Costo total: ${total_cost:.2f}
- Tiempo total: {total_duration:.1f}s

## Eventos del Día ({len(events)})
{chr(10).join([f"- {event.created_at.strftime('%H:%M')}: {event.type} ({event.agent or 'system'})" for event in events]) if events else "- No hay eventos registrados"}

## Próximas Acciones
- Revisar tareas pendientes
- Analizar métricas de rendimiento
- Planificar siguiente sprint

---
*Reporte generado automáticamente por CoreHub*
"""
        
        return report_content


async def _log_event(agent: str, event_type: str, payload: Dict[str, Any]) -> None:
    """
    Log an event to the database.
    
    Args:
        agent: Agent name (or "system")
        event_type: Type of event
        payload: Event payload data
    """
    try:
        with SessionLocal() as db:
            event = Event(
                agent=agent,
                type=event_type,
                payload=payload,
                created_at=datetime.utcnow()
            )
            db.add(event)
            db.commit()
    except Exception as e:
        print(f"Failed to log event: {e}")
