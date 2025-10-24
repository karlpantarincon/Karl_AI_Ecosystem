"""
Sistema de Métricas Avanzadas para Karl AI Ecosystem
"""

import time
import psutil
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import json

from loguru import logger


@dataclass
class SystemMetrics:
    """Métricas del sistema"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    network_sent_mb: float
    network_recv_mb: float
    load_average: List[float]


@dataclass
class ApplicationMetrics:
    """Métricas de la aplicación"""
    timestamp: str
    active_connections: int
    requests_per_minute: int
    response_time_avg: float
    error_rate: float
    cache_hit_ratio: float
    database_connections: int
    queue_size: int


@dataclass
class AgentMetrics:
    """Métricas de agentes"""
    timestamp: str
    agent_id: str
    status: str
    tasks_completed: int
    tasks_failed: int
    uptime_seconds: int
    cpu_usage: float
    memory_usage: float
    last_heartbeat: str
    performance_score: float


@dataclass
class BusinessMetrics:
    """Métricas de negocio"""
    timestamp: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    success_rate: float
    ai_cost_24h: float
    ai_cost_total: float
    average_task_duration: float
    tasks_per_hour: float
    revenue_generated: float


class MetricsCollector:
    """Recolector de métricas del sistema"""
    
    def __init__(self):
        self.metrics_history = {
            'system': deque(maxlen=1000),
            'application': deque(maxlen=1000),
            'agents': deque(maxlen=1000),
            'business': deque(maxlen=1000)
        }
        self.alerts = []
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'error_rate': 5.0,
            'response_time': 2.0,
            'cache_hit_ratio': 70.0
        }
        self.start_time = time.time()
        self.network_initial = psutil.net_io_counters()
        
    async def collect_system_metrics(self) -> SystemMetrics:
        """Recolectar métricas del sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memoria
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / 1024 / 1024
            memory_total_mb = memory.total / 1024 / 1024
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_used_gb = disk.used / 1024 / 1024 / 1024
            disk_total_gb = disk.total / 1024 / 1024 / 1024
            
            # Red
            network = psutil.net_io_counters()
            network_sent_mb = (network.bytes_sent - self.network_initial.bytes_sent) / 1024 / 1024
            network_recv_mb = (network.bytes_recv - self.network_initial.bytes_recv) / 1024 / 1024
            
            # Load average
            load_average = list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else [0.0, 0.0, 0.0]
            
            metrics = SystemMetrics(
                timestamp=datetime.utcnow().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_total_mb=memory_total_mb,
                disk_percent=disk_percent,
                disk_used_gb=disk_used_gb,
                disk_total_gb=disk_total_gb,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                load_average=load_average
            )
            
            self.metrics_history['system'].append(metrics)
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return None
    
    async def collect_application_metrics(self) -> ApplicationMetrics:
        """Recolectar métricas de la aplicación"""
        try:
            # Métricas básicas de la aplicación
            active_connections = len(psutil.net_connections())
            requests_per_minute = self._calculate_requests_per_minute()
            response_time_avg = self._calculate_avg_response_time()
            error_rate = self._calculate_error_rate()
            cache_hit_ratio = self._calculate_cache_hit_ratio()
            database_connections = self._get_database_connections()
            queue_size = self._get_queue_size()
            
            metrics = ApplicationMetrics(
                timestamp=datetime.utcnow().isoformat(),
                active_connections=active_connections,
                requests_per_minute=requests_per_minute,
                response_time_avg=response_time_avg,
                error_rate=error_rate,
                cache_hit_ratio=cache_hit_ratio,
                database_connections=database_connections,
                queue_size=queue_size
            )
            
            self.metrics_history['application'].append(metrics)
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return None
    
    async def collect_agent_metrics(self, agent_id: str) -> AgentMetrics:
        """Recolectar métricas de un agente específico"""
        try:
            # Obtener métricas del agente desde la base de datos
            # Esto sería implementado con la conexión a la DB
            status = "running"  # Placeholder
            tasks_completed = 0  # Placeholder
            tasks_failed = 0    # Placeholder
            uptime_seconds = int(time.time() - self.start_time)
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            last_heartbeat = datetime.utcnow().isoformat()
            performance_score = self._calculate_agent_performance(agent_id)
            
            metrics = AgentMetrics(
                timestamp=datetime.utcnow().isoformat(),
                agent_id=agent_id,
                status=status,
                tasks_completed=tasks_completed,
                tasks_failed=tasks_failed,
                uptime_seconds=uptime_seconds,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                last_heartbeat=last_heartbeat,
                performance_score=performance_score
            )
            
            self.metrics_history['agents'].append(metrics)
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting agent metrics for {agent_id}: {e}")
            return None
    
    async def collect_business_metrics(self) -> BusinessMetrics:
        """Recolectar métricas de negocio"""
        try:
            # Obtener métricas de negocio desde la base de datos
            # Esto sería implementado con la conexión a la DB
            total_tasks = 0      # Placeholder
            completed_tasks = 0  # Placeholder
            failed_tasks = 0     # Placeholder
            success_rate = 0.0   # Placeholder
            ai_cost_24h = 0.0    # Placeholder
            ai_cost_total = 0.0  # Placeholder
            average_task_duration = 0.0  # Placeholder
            tasks_per_hour = 0.0  # Placeholder
            revenue_generated = 0.0  # Placeholder
            
            metrics = BusinessMetrics(
                timestamp=datetime.utcnow().isoformat(),
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                failed_tasks=failed_tasks,
                success_rate=success_rate,
                ai_cost_24h=ai_cost_24h,
                ai_cost_total=ai_cost_total,
                average_task_duration=average_task_duration,
                tasks_per_hour=tasks_per_hour,
                revenue_generated=revenue_generated
            )
            
            self.metrics_history['business'].append(metrics)
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting business metrics: {e}")
            return None
    
    def _calculate_requests_per_minute(self) -> int:
        """Calcular requests por minuto"""
        # Implementación placeholder
        return 0
    
    def _calculate_avg_response_time(self) -> float:
        """Calcular tiempo promedio de respuesta"""
        # Implementación placeholder
        return 0.0
    
    def _calculate_error_rate(self) -> float:
        """Calcular tasa de errores"""
        # Implementación placeholder
        return 0.0
    
    def _calculate_cache_hit_ratio(self) -> float:
        """Calcular ratio de cache hits"""
        # Implementación placeholder
        return 0.0
    
    def _get_database_connections(self) -> int:
        """Obtener número de conexiones a la base de datos"""
        # Implementación placeholder
        return 0
    
    def _get_queue_size(self) -> int:
        """Obtener tamaño de la cola"""
        # Implementación placeholder
        return 0
    
    def _calculate_agent_performance(self, agent_id: str) -> float:
        """Calcular score de rendimiento del agente"""
        # Implementación placeholder
        return 0.0
    
    async def check_alerts(self) -> List[Dict[str, Any]]:
        """Verificar alertas basadas en métricas"""
        alerts = []
        
        # Obtener métricas más recientes
        if self.metrics_history['system']:
            system_metrics = self.metrics_history['system'][-1]
            
            # Alertas de CPU
            if system_metrics.cpu_percent > self.thresholds['cpu_percent']:
                alerts.append({
                    'type': 'cpu_high',
                    'severity': 'warning',
                    'message': f"CPU usage is {system_metrics.cpu_percent:.1f}% (threshold: {self.thresholds['cpu_percent']}%)",
                    'timestamp': system_metrics.timestamp,
                    'value': system_metrics.cpu_percent,
                    'threshold': self.thresholds['cpu_percent']
                })
            
            # Alertas de memoria
            if system_metrics.memory_percent > self.thresholds['memory_percent']:
                alerts.append({
                    'type': 'memory_high',
                    'severity': 'warning',
                    'message': f"Memory usage is {system_metrics.memory_percent:.1f}% (threshold: {self.thresholds['memory_percent']}%)",
                    'timestamp': system_metrics.timestamp,
                    'value': system_metrics.memory_percent,
                    'threshold': self.thresholds['memory_percent']
                })
            
            # Alertas de disco
            if system_metrics.disk_percent > self.thresholds['disk_percent']:
                alerts.append({
                    'type': 'disk_high',
                    'severity': 'critical',
                    'message': f"Disk usage is {system_metrics.disk_percent:.1f}% (threshold: {self.thresholds['disk_percent']}%)",
                    'timestamp': system_metrics.timestamp,
                    'value': system_metrics.disk_percent,
                    'threshold': self.thresholds['disk_percent']
                })
        
        if self.metrics_history['application']:
            app_metrics = self.metrics_history['application'][-1]
            
            # Alertas de tasa de errores
            if app_metrics.error_rate > self.thresholds['error_rate']:
                alerts.append({
                    'type': 'error_rate_high',
                    'severity': 'warning',
                    'message': f"Error rate is {app_metrics.error_rate:.1f}% (threshold: {self.thresholds['error_rate']}%)",
                    'timestamp': app_metrics.timestamp,
                    'value': app_metrics.error_rate,
                    'threshold': self.thresholds['error_rate']
                })
            
            # Alertas de tiempo de respuesta
            if app_metrics.response_time_avg > self.thresholds['response_time']:
                alerts.append({
                    'type': 'response_time_high',
                    'severity': 'warning',
                    'message': f"Response time is {app_metrics.response_time_avg:.2f}s (threshold: {self.thresholds['response_time']}s)",
                    'timestamp': app_metrics.timestamp,
                    'value': app_metrics.response_time_avg,
                    'threshold': self.thresholds['response_time']
                })
        
        # Agregar alertas a la lista
        self.alerts.extend(alerts)
        
        return alerts
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Obtener resumen de métricas"""
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'system': None,
            'application': None,
            'agents': [],
            'business': None,
            'alerts': len(self.alerts),
            'uptime_seconds': int(time.time() - self.start_time)
        }
        
        # Métricas del sistema
        if self.metrics_history['system']:
            summary['system'] = asdict(self.metrics_history['system'][-1])
        
        # Métricas de la aplicación
        if self.metrics_history['application']:
            summary['application'] = asdict(self.metrics_history['application'][-1])
        
        # Métricas de agentes
        if self.metrics_history['agents']:
            summary['agents'] = [asdict(agent) for agent in list(self.metrics_history['agents'])[-10:]]
        
        # Métricas de negocio
        if self.metrics_history['business']:
            summary['business'] = asdict(self.metrics_history['business'][-1])
        
        return summary
    
    def get_historical_metrics(self, metric_type: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Obtener métricas históricas"""
        if metric_type not in self.metrics_history:
            return []
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        historical = []
        
        for metric in self.metrics_history[metric_type]:
            metric_time = datetime.fromisoformat(metric.timestamp.replace('Z', '+00:00'))
            if metric_time >= cutoff_time:
                historical.append(asdict(metric))
        
        return historical


# Instancia global del recolector de métricas
metrics_collector = MetricsCollector()
