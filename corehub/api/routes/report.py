"""
Report generation endpoints.

Handles daily report generation and retrieval.
"""

import os
from datetime import datetime, date
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from corehub.db.database import get_db
from corehub.db.models import Task, Run, Event

router = APIRouter()


@router.get("/daily")
async def get_daily_report(
    report_date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate daily report for a specific date.
    
    Args:
        report_date: Date for the report (defaults to today)
        db: Database session dependency
        
    Returns:
        Dict containing daily report data
    """
    # Parse date or use today
    if report_date:
        try:
            target_date = datetime.strptime(report_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    else:
        target_date = date.today()
    
    # Get tasks completed on the target date
    completed_tasks = db.query(Task).filter(
        Task.status == "done",
        Task.updated_at >= datetime.combine(target_date, datetime.min.time()),
        Task.updated_at < datetime.combine(target_date, datetime.min.time()).replace(day=target_date.day + 1)
    ).all()
    
    # Get runs for the target date
    runs = db.query(Run).filter(
        Run.created_at >= datetime.combine(target_date, datetime.min.time()),
        Run.created_at < datetime.combine(target_date, datetime.min.time()).replace(day=target_date.day + 1)
    ).all()
    
    # Get events for the target date
    events = db.query(Event).filter(
        Event.created_at >= datetime.combine(target_date, datetime.min.time()),
        Event.created_at < datetime.combine(target_date, datetime.min.time()).replace(day=target_date.day + 1)
    ).all()
    
    # Calculate metrics
    total_cost = sum(run.cost_usd or 0 for run in runs)
    total_duration = sum(run.duration_sec or 0 for run in runs)
    successful_runs = len([r for r in runs if r.status == "completed"])
    success_rate = (successful_runs / len(runs) * 100) if runs else 0
    
    # Generate report content
    report_content = f"""# Resumen Diario - {target_date}

## Tareas Completadas ({len(completed_tasks)})
{chr(10).join([f"- [{task.id}] {task.title}" for task in completed_tasks])}

## Métricas del Día
- Total de runs: {len(runs)}
- Runs exitosos: {successful_runs}
- Tasa de éxito: {success_rate:.1f}%
- Costo total: ${total_cost:.2f}
- Tiempo total: {total_duration:.1f}s

## Eventos del Día ({len(events)})
{chr(10).join([f"- {event.created_at.strftime('%H:%M')}: {event.type} ({event.agent or 'system'})" for event in events])}

## Próximas Acciones
- Revisar tareas pendientes
- Analizar métricas de rendimiento
- Planificar siguiente sprint

---
*Reporte generado automáticamente por CoreHub*
"""
    
    # Save report to file
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "reports", "daily")
    os.makedirs(reports_dir, exist_ok=True)
    
    report_filename = f"{target_date}.md"
    report_path = os.path.join(reports_dir, report_filename)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    return {
        "date": target_date.isoformat(),
        "report_path": report_path,
        "metrics": {
            "completed_tasks": len(completed_tasks),
            "total_runs": len(runs),
            "successful_runs": successful_runs,
            "success_rate": round(success_rate, 1),
            "total_cost": round(total_cost, 2),
            "total_duration": round(total_duration, 1),
            "total_events": len(events)
        },
        "content": report_content
    }


@router.get("/daily/{report_date}")
async def get_daily_report_file(
    report_date: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get daily report file if it exists.
    
    Args:
        report_date: Date in YYYY-MM-DD format
        db: Database session dependency
        
    Returns:
        Dict containing report file content
        
    Raises:
        HTTPException: If report file not found
    """
    try:
        target_date = datetime.strptime(report_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "reports", "daily")
    report_filename = f"{target_date}.md"
    report_path = os.path.join(reports_dir, report_filename)
    
    if not os.path.exists(report_path):
        raise HTTPException(
            status_code=404,
            detail=f"Report for {report_date} not found"
        )
    
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return {
        "date": report_date,
        "content": content,
        "file_path": report_path
    }
