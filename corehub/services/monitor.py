"""
Servicio de Monitoreo Continuo para Karl AI Ecosystem
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os

from loguru import logger

from corehub.services.metrics import metrics_collector
from corehub.services.alerts import alert_manager, AlertSeverity
from corehub.tools.corehub_client import CoreHubClient


class MonitoringService:
    """Servicio de monitoreo continuo"""
    
    def __init__(self):
        self.running = False
        self.monitoring_tasks = []
        self.check_interval = int(os.getenv('MONITORING_INTERVAL', '60'))  # segundos
        self.alert_thresholds = {
            'cpu_percent': float(os.getenv('CPU_THRESHOLD', '80.0')),
            'memory_percent': float(os.getenv('MEMORY_THRESHOLD', '85.0')),
            'disk_percent': float(os.getenv('DISK_THRESHOLD', '90.0')),
            'error_rate': float(os.getenv('ERROR_RATE_THRESHOLD', '5.0')),
            'response_time': float(os.getenv('RESPONSE_TIME_THRESHOLD', '2.0'))
        }
        self.corehub_client = CoreHubClient()
        
    async def start_monitoring(self):
        """Iniciar monitoreo continuo"""
        if self.running:
            logger.warning("Monitoring service is already running")
            return
        
        self.running = True
        logger.info("🔍 Starting monitoring service...")
        
        # Crear tareas de monitoreo
        self.monitoring_tasks = [
            asyncio.create_task(self._monitor_system_metrics()),
            asyncio.create_task(self._monitor_application_metrics()),
            asyncio.create_task(self._monitor_agents()),
            asyncio.create_task(self._monitor_business_metrics()),
            asyncio.create_task(self._check_alerts())
        ]
        
        logger.info("✅ Monitoring service started")
        
        # Ejecutar tareas
        try:
            await asyncio.gather(*self.monitoring_tasks)
        except Exception as e:
            logger.error(f"Error in monitoring tasks: {e}")
        finally:
            await self.stop_monitoring()
    
    async def stop_monitoring(self):
        """Detener monitoreo"""
        if not self.running:
            return
        
        self.running = False
        logger.info("🛑 Stopping monitoring service...")
        
        # Cancelar tareas
        for task in self.monitoring_tasks:
            if not task.done():
                task.cancel()
        
        # Esperar a que terminen
        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        
        logger.info("✅ Monitoring service stopped")
    
    async def _monitor_system_metrics(self):
        """Monitorear métricas del sistema"""
        while self.running:
            try:
                metrics = await metrics_collector.collect_system_metrics()
                if metrics:
                    # Verificar umbrales
                    await self._check_system_thresholds(metrics)
                
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error monitoring system metrics: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _monitor_application_metrics(self):
        """Monitorear métricas de la aplicación"""
        while self.running:
            try:
                metrics = await metrics_collector.collect_application_metrics()
                if metrics:
                    # Verificar umbrales
                    await self._check_application_thresholds(metrics)
                
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error monitoring application metrics: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _monitor_agents(self):
        """Monitorear agentes"""
        while self.running:
            try:
                # Obtener lista de agentes
                agent_ids = await self._get_agent_ids()
                
                for agent_id in agent_ids:
                    metrics = await metrics_collector.collect_agent_metrics(agent_id)
                    if metrics:
                        # Verificar estado del agente
                        await self._check_agent_health(agent_id, metrics)
                
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error monitoring agents: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _monitor_business_metrics(self):
        """Monitorear métricas de negocio"""
        while self.running:
            try:
                metrics = await metrics_collector.collect_business_metrics()
                if metrics:
                    # Verificar métricas de negocio
                    await self._check_business_thresholds(metrics)
                
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error monitoring business metrics: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_alerts(self):
        """Verificar alertas"""
        while self.running:
            try:
                alerts = await metrics_collector.check_alerts()
                if alerts:
                    logger.info(f"Generated {len(alerts)} alerts")
                
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error checking alerts: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_system_thresholds(self, metrics):
        """Verificar umbrales del sistema"""
        # CPU
        if metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            await alert_manager.create_alert(
                alert_type="cpu_high",
                severity=AlertSeverity.WARNING,
                title="High CPU Usage",
                message=f"CPU usage is {metrics.cpu_percent:.1f}% (threshold: {self.alert_thresholds['cpu_percent']}%)",
                source="system_monitor",
                metadata={"cpu_percent": metrics.cpu_percent, "threshold": self.alert_thresholds['cpu_percent']}
            )
        
        # Memoria
        if metrics.memory_percent > self.alert_thresholds['memory_percent']:
            await alert_manager.create_alert(
                alert_type="memory_high",
                severity=AlertSeverity.WARNING,
                title="High Memory Usage",
                message=f"Memory usage is {metrics.memory_percent:.1f}% (threshold: {self.alert_thresholds['memory_percent']}%)",
                source="system_monitor",
                metadata={"memory_percent": metrics.memory_percent, "threshold": self.alert_thresholds['memory_percent']}
            )
        
        # Disco
        if metrics.disk_percent > self.alert_thresholds['disk_percent']:
            await alert_manager.create_alert(
                alert_type="disk_high",
                severity=AlertSeverity.CRITICAL,
                title="High Disk Usage",
                message=f"Disk usage is {metrics.disk_percent:.1f}% (threshold: {self.alert_thresholds['disk_percent']}%)",
                source="system_monitor",
                metadata={"disk_percent": metrics.disk_percent, "threshold": self.alert_thresholds['disk_percent']}
            )
    
    async def _check_application_thresholds(self, metrics):
        """Verificar umbrales de la aplicación"""
        # Tasa de errores
        if metrics.error_rate > self.alert_thresholds['error_rate']:
            await alert_manager.create_alert(
                alert_type="error_rate_high",
                severity=AlertSeverity.WARNING,
                title="High Error Rate",
                message=f"Error rate is {metrics.error_rate:.1f}% (threshold: {self.alert_thresholds['error_rate']}%)",
                source="application_monitor",
                metadata={"error_rate": metrics.error_rate, "threshold": self.alert_thresholds['error_rate']}
            )
        
        # Tiempo de respuesta
        if metrics.response_time_avg > self.alert_thresholds['response_time']:
            await alert_manager.create_alert(
                alert_type="response_time_high",
                severity=AlertSeverity.WARNING,
                title="High Response Time",
                message=f"Response time is {metrics.response_time_avg:.2f}s (threshold: {self.alert_thresholds['response_time']}s)",
                source="application_monitor",
                metadata={"response_time": metrics.response_time_avg, "threshold": self.alert_thresholds['response_time']}
            )
    
    async def _check_agent_health(self, agent_id: str, metrics):
        """Verificar salud de un agente"""
        # Verificar si el agente está respondiendo
        if metrics.status != "running":
            await alert_manager.create_alert(
                alert_type="agent_down",
                severity=AlertSeverity.CRITICAL,
                title=f"Agent {agent_id} is down",
                message=f"Agent {agent_id} is not running (status: {metrics.status})",
                source="agent_monitor",
                metadata={"agent_id": agent_id, "status": metrics.status}
            )
        
        # Verificar rendimiento del agente
        if metrics.performance_score < 0.5:
            await alert_manager.create_alert(
                alert_type="agent_performance_low",
                severity=AlertSeverity.WARNING,
                title=f"Agent {agent_id} performance is low",
                message=f"Agent {agent_id} performance score is {metrics.performance_score:.2f}",
                source="agent_monitor",
                metadata={"agent_id": agent_id, "performance_score": metrics.performance_score}
            )
    
    async def _check_business_thresholds(self, metrics):
        """Verificar umbrales de negocio"""
        # Tasa de éxito baja
        if metrics.success_rate < 80.0:
            await alert_manager.create_alert(
                alert_type="success_rate_low",
                severity=AlertSeverity.WARNING,
                title="Low Success Rate",
                message=f"Success rate is {metrics.success_rate:.1f}% (threshold: 80%)",
                source="business_monitor",
                metadata={"success_rate": metrics.success_rate, "threshold": 80.0}
            )
        
        # Costo de IA alto
        if metrics.ai_cost_24h > 100.0:  # $100 por día
            await alert_manager.create_alert(
                alert_type="ai_cost_high",
                severity=AlertSeverity.WARNING,
                title="High AI Cost",
                message=f"AI cost for 24h is ${metrics.ai_cost_24h:.2f} (threshold: $100)",
                source="business_monitor",
                metadata={"ai_cost_24h": metrics.ai_cost_24h, "threshold": 100.0}
            )
    
    async def _get_agent_ids(self) -> List[str]:
        """Obtener lista de IDs de agentes"""
        # Esto sería implementado con la conexión a la DB
        return ["devagent", "monitoring-agent"]  # Placeholder
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Obtener estado del servicio de monitoreo"""
        return {
            "running": self.running,
            "check_interval": self.check_interval,
            "active_tasks": len([task for task in self.monitoring_tasks if not task.done()]),
            "alert_thresholds": self.alert_thresholds,
            "timestamp": datetime.utcnow().isoformat()
        }


# Instancia global del servicio de monitoreo
monitoring_service = MonitoringService()
