"""
Endpoints de Monitoreo para Karl AI Ecosystem
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from corehub.services.metrics import metrics_collector, SystemMetrics, ApplicationMetrics, AgentMetrics, BusinessMetrics
from corehub.services.alerts import alert_manager, AlertSeverity, AlertStatus
from corehub.api.schemas import BaseResponse

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/metrics/system", response_model=BaseResponse)
async def get_system_metrics():
    """Obtener métricas del sistema"""
    try:
        metrics = await metrics_collector.collect_system_metrics()
        if not metrics:
            raise HTTPException(status_code=500, detail="Error collecting system metrics")
        
        return BaseResponse(
            success=True,
            data={
                "timestamp": metrics.timestamp,
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
                "memory_used_mb": metrics.memory_used_mb,
                "memory_total_mb": metrics.memory_total_mb,
                "disk_percent": metrics.disk_percent,
                "disk_used_gb": metrics.disk_used_gb,
                "disk_total_gb": metrics.disk_total_gb,
                "network_sent_mb": metrics.network_sent_mb,
                "network_recv_mb": metrics.network_recv_mb,
                "load_average": metrics.load_average
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/application", response_model=BaseResponse)
async def get_application_metrics():
    """Obtener métricas de la aplicación"""
    try:
        metrics = await metrics_collector.collect_application_metrics()
        if not metrics:
            raise HTTPException(status_code=500, detail="Error collecting application metrics")
        
        return BaseResponse(
            success=True,
            data={
                "timestamp": metrics.timestamp,
                "active_connections": metrics.active_connections,
                "requests_per_minute": metrics.requests_per_minute,
                "response_time_avg": metrics.response_time_avg,
                "error_rate": metrics.error_rate,
                "cache_hit_ratio": metrics.cache_hit_ratio,
                "database_connections": metrics.database_connections,
                "queue_size": metrics.queue_size
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/agents", response_model=BaseResponse)
async def get_agents_metrics():
    """Obtener métricas de agentes"""
    try:
        # Obtener lista de agentes (esto sería implementado con la DB)
        agent_ids = ["devagent", "monitoring-agent"]  # Placeholder
        
        agents_metrics = []
        for agent_id in agent_ids:
            metrics = await metrics_collector.collect_agent_metrics(agent_id)
            if metrics:
                agents_metrics.append({
                    "agent_id": metrics.agent_id,
                    "status": metrics.status,
                    "tasks_completed": metrics.tasks_completed,
                    "tasks_failed": metrics.tasks_failed,
                    "uptime_seconds": metrics.uptime_seconds,
                    "cpu_usage": metrics.cpu_usage,
                    "memory_usage": metrics.memory_usage,
                    "last_heartbeat": metrics.last_heartbeat,
                    "performance_score": metrics.performance_score
                })
        
        return BaseResponse(
            success=True,
            data={
                "timestamp": datetime.utcnow().isoformat(),
                "agents": agents_metrics
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/business", response_model=BaseResponse)
async def get_business_metrics():
    """Obtener métricas de negocio"""
    try:
        metrics = await metrics_collector.collect_business_metrics()
        if not metrics:
            raise HTTPException(status_code=500, detail="Error collecting business metrics")
        
        return BaseResponse(
            success=True,
            data={
                "timestamp": metrics.timestamp,
                "total_tasks": metrics.total_tasks,
                "completed_tasks": metrics.completed_tasks,
                "failed_tasks": metrics.failed_tasks,
                "success_rate": metrics.success_rate,
                "ai_cost_24h": metrics.ai_cost_24h,
                "ai_cost_total": metrics.ai_cost_total,
                "average_task_duration": metrics.average_task_duration,
                "tasks_per_hour": metrics.tasks_per_hour,
                "revenue_generated": metrics.revenue_generated
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/summary", response_model=BaseResponse)
async def get_metrics_summary():
    """Obtener resumen de todas las métricas"""
    try:
        summary = metrics_collector.get_metrics_summary()
        return BaseResponse(success=True, data=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/historical", response_model=BaseResponse)
async def get_historical_metrics(
    metric_type: str = Query(..., description="Tipo de métrica (system, application, agents, business)"),
    hours: int = Query(24, description="Horas hacia atrás")
):
    """Obtener métricas históricas"""
    try:
        if metric_type not in ["system", "application", "agents", "business"]:
            raise HTTPException(status_code=400, detail="Invalid metric type")
        
        historical = metrics_collector.get_historical_metrics(metric_type, hours)
        return BaseResponse(success=True, data=historical)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=BaseResponse)
async def get_alerts(
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    severity: Optional[str] = Query(None, description="Filtrar por severidad"),
    limit: int = Query(100, description="Límite de resultados")
):
    """Obtener alertas del sistema"""
    try:
        alerts = list(alert_manager.alerts.values())
        
        # Filtrar por estado
        if status:
            alerts = [alert for alert in alerts if alert.status.value == status]
        
        # Filtrar por severidad
        if severity:
            alerts = [alert for alert in alerts if alert.severity.value == severity]
        
        # Limitar resultados
        alerts = alerts[:limit]
        
        # Convertir a dict
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                "id": alert.id,
                "type": alert.type,
                "severity": alert.severity.value,
                "status": alert.status.value,
                "title": alert.title,
                "message": alert.message,
                "timestamp": alert.timestamp,
                "source": alert.source,
                "metadata": alert.metadata,
                "acknowledged_by": alert.acknowledged_by,
                "acknowledged_at": alert.acknowledged_at,
                "resolved_at": alert.resolved_at
            })
        
        return BaseResponse(success=True, data=alerts_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/active", response_model=BaseResponse)
async def get_active_alerts():
    """Obtener alertas activas"""
    try:
        active_alerts = alert_manager.get_active_alerts()
        alerts_data = []
        
        for alert in active_alerts:
            alerts_data.append({
                "id": alert.id,
                "type": alert.type,
                "severity": alert.severity.value,
                "title": alert.title,
                "message": alert.message,
                "timestamp": alert.timestamp,
                "source": alert.source,
                "metadata": alert.metadata
            })
        
        return BaseResponse(success=True, data=alerts_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/acknowledge", response_model=BaseResponse)
async def acknowledge_alert(
    alert_id: str,
    acknowledged_by: str = Query(..., description="Usuario que reconoce la alerta")
):
    """Reconocer una alerta"""
    try:
        success = await alert_manager.acknowledge_alert(alert_id, acknowledged_by)
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return BaseResponse(success=True, data={"message": "Alert acknowledged"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/resolve", response_model=BaseResponse)
async def resolve_alert(alert_id: str):
    """Resolver una alerta"""
    try:
        success = await alert_manager.resolve_alert(alert_id)
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return BaseResponse(success=True, data={"message": "Alert resolved"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/summary", response_model=BaseResponse)
async def get_alerts_summary():
    """Obtener resumen de alertas"""
    try:
        summary = alert_manager.get_alert_summary()
        return BaseResponse(success=True, data=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/detailed", response_model=BaseResponse)
async def get_detailed_health():
    """Obtener estado de salud detallado del sistema"""
    try:
        # Recolectar métricas
        system_metrics = await metrics_collector.collect_system_metrics()
        app_metrics = await metrics_collector.collect_application_metrics()
        
        # Verificar alertas
        alerts = await metrics_collector.check_alerts()
        
        # Determinar estado general
        overall_status = "healthy"
        if system_metrics and system_metrics.cpu_percent > 90:
            overall_status = "degraded"
        if system_metrics and system_metrics.memory_percent > 95:
            overall_status = "critical"
        if alerts:
            overall_status = "degraded"
        
        health_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": overall_status,
            "system": {
                "cpu_percent": system_metrics.cpu_percent if system_metrics else 0,
                "memory_percent": system_metrics.memory_percent if system_metrics else 0,
                "disk_percent": system_metrics.disk_percent if system_metrics else 0
            },
            "application": {
                "active_connections": app_metrics.active_connections if app_metrics else 0,
                "error_rate": app_metrics.error_rate if app_metrics else 0,
                "response_time_avg": app_metrics.response_time_avg if app_metrics else 0
            },
            "alerts": {
                "total": len(alerts),
                "active": len(alert_manager.get_active_alerts())
            },
            "uptime_seconds": int((datetime.utcnow() - datetime.utcnow()).total_seconds())
        }
        
        return BaseResponse(success=True, data=health_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
