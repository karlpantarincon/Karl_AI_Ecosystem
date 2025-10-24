"""
Tests para el sistema de monitoreo
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from corehub.services.metrics import MetricsCollector, SystemMetrics, ApplicationMetrics
from corehub.services.alerts import AlertManager, AlertSeverity, AlertStatus
from corehub.services.monitor import MonitoringService


class TestMetricsCollector:
    """Tests para el recolector de métricas"""
    
    @pytest.fixture
    def metrics_collector(self):
        return MetricsCollector()
    
    @pytest.mark.asyncio
    async def test_collect_system_metrics(self, metrics_collector):
        """Test recolección de métricas del sistema"""
        metrics = await metrics_collector.collect_system_metrics()
        
        assert metrics is not None
        assert isinstance(metrics, SystemMetrics)
        assert metrics.timestamp is not None
        assert 0 <= metrics.cpu_percent <= 100
        assert 0 <= metrics.memory_percent <= 100
        assert metrics.memory_used_mb > 0
        assert metrics.memory_total_mb > 0
        assert 0 <= metrics.disk_percent <= 100
        assert metrics.disk_used_gb > 0
        assert metrics.disk_total_gb > 0
        assert metrics.network_sent_mb >= 0
        assert metrics.network_recv_mb >= 0
        assert len(metrics.load_average) == 3
    
    @pytest.mark.asyncio
    async def test_collect_application_metrics(self, metrics_collector):
        """Test recolección de métricas de la aplicación"""
        metrics = await metrics_collector.collect_application_metrics()
        
        assert metrics is not None
        assert isinstance(metrics, ApplicationMetrics)
        assert metrics.timestamp is not None
        assert metrics.active_connections >= 0
        assert metrics.requests_per_minute >= 0
        assert metrics.response_time_avg >= 0
        assert 0 <= metrics.error_rate <= 100
        assert 0 <= metrics.cache_hit_ratio <= 100
        assert metrics.database_connections >= 0
        assert metrics.queue_size >= 0
    
    @pytest.mark.asyncio
    async def test_collect_agent_metrics(self, metrics_collector):
        """Test recolección de métricas de agentes"""
        agent_id = "test-agent"
        metrics = await metrics_collector.collect_agent_metrics(agent_id)
        
        assert metrics is not None
        assert metrics.agent_id == agent_id
        assert metrics.timestamp is not None
        assert metrics.status in ["running", "stopped", "paused", "error"]
        assert metrics.tasks_completed >= 0
        assert metrics.tasks_failed >= 0
        assert metrics.uptime_seconds >= 0
        assert 0 <= metrics.cpu_usage <= 100
        assert 0 <= metrics.memory_usage <= 100
        assert metrics.last_heartbeat is not None
        assert 0 <= metrics.performance_score <= 1
    
    @pytest.mark.asyncio
    async def test_collect_business_metrics(self, metrics_collector):
        """Test recolección de métricas de negocio"""
        metrics = await metrics_collector.collect_business_metrics()
        
        assert metrics is not None
        assert metrics.timestamp is not None
        assert metrics.total_tasks >= 0
        assert metrics.completed_tasks >= 0
        assert metrics.failed_tasks >= 0
        assert 0 <= metrics.success_rate <= 100
        assert metrics.ai_cost_24h >= 0
        assert metrics.ai_cost_total >= 0
        assert metrics.average_task_duration >= 0
        assert metrics.tasks_per_hour >= 0
        assert metrics.revenue_generated >= 0
    
    def test_get_metrics_summary(self, metrics_collector):
        """Test obtención de resumen de métricas"""
        summary = metrics_collector.get_metrics_summary()
        
        assert isinstance(summary, dict)
        assert "timestamp" in summary
        assert "system" in summary
        assert "application" in summary
        assert "agents" in summary
        assert "business" in summary
        assert "alerts" in summary
        assert "uptime_seconds" in summary
    
    def test_get_historical_metrics(self, metrics_collector):
        """Test obtención de métricas históricas"""
        # Agregar algunas métricas de prueba
        for i in range(5):
            metrics_collector.metrics_history['system'].append(
                SystemMetrics(
                    timestamp=datetime.utcnow().isoformat(),
                    cpu_percent=50.0 + i,
                    memory_percent=60.0 + i,
                    memory_used_mb=1000.0,
                    memory_total_mb=2000.0,
                    disk_percent=70.0,
                    disk_used_gb=100.0,
                    disk_total_gb=200.0,
                    network_sent_mb=10.0,
                    network_recv_mb=20.0,
                    load_average=[1.0, 1.5, 2.0]
                )
            )
        
        historical = metrics_collector.get_historical_metrics("system", 24)
        assert len(historical) == 5
        assert all("timestamp" in metric for metric in historical)
        assert all("cpu_percent" in metric for metric in historical)


class TestAlertManager:
    """Tests para el gestor de alertas"""
    
    @pytest.fixture
    def alert_manager(self):
        return AlertManager()
    
    @pytest.mark.asyncio
    async def test_create_alert(self, alert_manager):
        """Test creación de alerta"""
        alert = await alert_manager.create_alert(
            alert_type="test_alert",
            severity=AlertSeverity.WARNING,
            title="Test Alert",
            message="This is a test alert",
            source="test_source",
            metadata={"test": "data"}
        )
        
        assert alert is not None
        assert alert.type == "test_alert"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.status == AlertStatus.ACTIVE
        assert alert.title == "Test Alert"
        assert alert.message == "This is a test alert"
        assert alert.source == "test_source"
        assert alert.metadata == {"test": "data"}
        assert alert.id in alert_manager.alerts
    
    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, alert_manager):
        """Test reconocimiento de alerta"""
        # Crear alerta
        alert = await alert_manager.create_alert(
            alert_type="test_alert",
            severity=AlertSeverity.WARNING,
            title="Test Alert",
            message="This is a test alert",
            source="test_source"
        )
        
        # Reconocer alerta
        success = await alert_manager.acknowledge_alert(alert.id, "test_user")
        
        assert success is True
        assert alert_manager.alerts[alert.id].status == AlertStatus.ACKNOWLEDGED
        assert alert_manager.alerts[alert.id].acknowledged_by == "test_user"
        assert alert_manager.alerts[alert.id].acknowledged_at is not None
    
    @pytest.mark.asyncio
    async def test_resolve_alert(self, alert_manager):
        """Test resolución de alerta"""
        # Crear alerta
        alert = await alert_manager.create_alert(
            alert_type="test_alert",
            severity=AlertSeverity.WARNING,
            title="Test Alert",
            message="This is a test alert",
            source="test_source"
        )
        
        # Resolver alerta
        success = await alert_manager.resolve_alert(alert.id)
        
        assert success is True
        assert alert_manager.alerts[alert.id].status == AlertStatus.RESOLVED
        assert alert_manager.alerts[alert.id].resolved_at is not None
    
    def test_get_active_alerts(self, alert_manager):
        """Test obtención de alertas activas"""
        # Crear algunas alertas
        alert_manager.alerts["alert1"] = Mock(
            status=AlertStatus.ACTIVE,
            id="alert1"
        )
        alert_manager.alerts["alert2"] = Mock(
            status=AlertStatus.ACKNOWLEDGED,
            id="alert2"
        )
        alert_manager.alerts["alert3"] = Mock(
            status=AlertStatus.ACTIVE,
            id="alert3"
        )
        
        active_alerts = alert_manager.get_active_alerts()
        assert len(active_alerts) == 2
        assert all(alert.status == AlertStatus.ACTIVE for alert in active_alerts)
    
    def test_get_alerts_by_severity(self, alert_manager):
        """Test obtención de alertas por severidad"""
        # Crear algunas alertas
        alert_manager.alerts["alert1"] = Mock(
            severity=AlertSeverity.WARNING,
            id="alert1"
        )
        alert_manager.alerts["alert2"] = Mock(
            severity=AlertSeverity.CRITICAL,
            id="alert2"
        )
        alert_manager.alerts["alert3"] = Mock(
            severity=AlertSeverity.WARNING,
            id="alert3"
        )
        
        warning_alerts = alert_manager.get_alerts_by_severity(AlertSeverity.WARNING)
        assert len(warning_alerts) == 2
        assert all(alert.severity == AlertSeverity.WARNING for alert in warning_alerts)
    
    def test_get_alert_summary(self, alert_manager):
        """Test obtención de resumen de alertas"""
        # Crear algunas alertas
        alert_manager.alerts["alert1"] = Mock(
            status=AlertStatus.ACTIVE,
            severity=AlertSeverity.WARNING,
            id="alert1"
        )
        alert_manager.alerts["alert2"] = Mock(
            status=AlertStatus.ACTIVE,
            severity=AlertSeverity.CRITICAL,
            id="alert2"
        )
        alert_manager.alerts["alert3"] = Mock(
            status=AlertStatus.RESOLVED,
            severity=AlertSeverity.INFO,
            id="alert3"
        )
        
        summary = alert_manager.get_alert_summary()
        assert summary["total_alerts"] == 3
        assert summary["active_alerts"] == 2
        assert summary["severity_counts"]["warning"] == 1
        assert summary["severity_counts"]["critical"] == 1
        assert summary["severity_counts"]["info"] == 1


class TestMonitoringService:
    """Tests para el servicio de monitoreo"""
    
    @pytest.fixture
    def monitoring_service(self):
        return MonitoringService()
    
    def test_initialization(self, monitoring_service):
        """Test inicialización del servicio"""
        assert monitoring_service.running is False
        assert monitoring_service.check_interval == 60
        assert "cpu_percent" in monitoring_service.alert_thresholds
        assert "memory_percent" in monitoring_service.alert_thresholds
        assert "disk_percent" in monitoring_service.alert_thresholds
        assert "error_rate" in monitoring_service.alert_thresholds
        assert "response_time" in monitoring_service.alert_thresholds
    
    @pytest.mark.asyncio
    async def test_get_monitoring_status(self, monitoring_service):
        """Test obtención de estado del monitoreo"""
        status = await monitoring_service.get_monitoring_status()
        
        assert isinstance(status, dict)
        assert "running" in status
        assert "check_interval" in status
        assert "active_tasks" in status
        assert "alert_thresholds" in status
        assert "timestamp" in status
        assert status["running"] is False
        assert status["active_tasks"] == 0
    
    @pytest.mark.asyncio
    async def test_check_system_thresholds(self, monitoring_service):
        """Test verificación de umbrales del sistema"""
        # Mock de métricas con valores altos
        high_cpu_metrics = Mock(
            cpu_percent=90.0,
            memory_percent=95.0,
            disk_percent=95.0
        )
        
        # Mock del alert manager
        with patch.object(monitoring_service, 'alert_manager') as mock_alert_manager:
            await monitoring_service._check_system_thresholds(high_cpu_metrics)
            
            # Verificar que se crearon alertas
            assert mock_alert_manager.create_alert.called
    
    @pytest.mark.asyncio
    async def test_check_application_thresholds(self, monitoring_service):
        """Test verificación de umbrales de la aplicación"""
        # Mock de métricas con valores altos
        high_error_metrics = Mock(
            error_rate=10.0,
            response_time_avg=5.0
        )
        
        # Mock del alert manager
        with patch.object(monitoring_service, 'alert_manager') as mock_alert_manager:
            await monitoring_service._check_application_thresholds(high_error_metrics)
            
            # Verificar que se crearon alertas
            assert mock_alert_manager.create_alert.called
    
    @pytest.mark.asyncio
    async def test_check_agent_health(self, monitoring_service):
        """Test verificación de salud de agentes"""
        # Mock de métricas de agente
        agent_metrics = Mock(
            status="stopped",
            performance_score=0.3
        )
        
        # Mock del alert manager
        with patch.object(monitoring_service, 'alert_manager') as mock_alert_manager:
            await monitoring_service._check_agent_health("test-agent", agent_metrics)
            
            # Verificar que se crearon alertas
            assert mock_alert_manager.create_alert.called
    
    @pytest.mark.asyncio
    async def test_check_business_thresholds(self, monitoring_service):
        """Test verificación de umbrales de negocio"""
        # Mock de métricas de negocio
        business_metrics = Mock(
            success_rate=70.0,
            ai_cost_24h=150.0
        )
        
        # Mock del alert manager
        with patch.object(monitoring_service, 'alert_manager') as mock_alert_manager:
            await monitoring_service._check_business_thresholds(business_metrics)
            
            # Verificar que se crearon alertas
            assert mock_alert_manager.create_alert.called


@pytest.mark.integration
class TestMonitoringIntegration:
    """Tests de integración para el sistema de monitoreo"""
    
    @pytest.mark.asyncio
    async def test_full_monitoring_workflow(self):
        """Test flujo completo de monitoreo"""
        # Crear instancias
        metrics_collector = MetricsCollector()
        alert_manager = AlertManager()
        monitoring_service = MonitoringService()
        
        # Recolectar métricas
        system_metrics = await metrics_collector.collect_system_metrics()
        app_metrics = await metrics_collector.collect_application_metrics()
        
        assert system_metrics is not None
        assert app_metrics is not None
        
        # Crear alerta
        alert = await alert_manager.create_alert(
            alert_type="integration_test",
            severity=AlertSeverity.INFO,
            title="Integration Test Alert",
            message="This is an integration test",
            source="test_suite"
        )
        
        assert alert is not None
        assert alert.id in alert_manager.alerts
        
        # Verificar estado del servicio
        status = await monitoring_service.get_monitoring_status()
        assert status["running"] is False
        
        # Verificar resumen de métricas
        summary = metrics_collector.get_metrics_summary()
        assert summary is not None
        assert "timestamp" in summary
    
    @pytest.mark.asyncio
    async def test_alert_cooldown(self):
        """Test cooldown de alertas"""
        alert_manager = AlertManager()
        
        # Crear primera alerta
        alert1 = await alert_manager.create_alert(
            alert_type="cooldown_test",
            severity=AlertSeverity.WARNING,
            title="First Alert",
            message="This is the first alert",
            source="test"
        )
        
        assert alert1 is not None
        
        # Intentar crear segunda alerta del mismo tipo (debería estar en cooldown)
        alert2 = await alert_manager.create_alert(
            alert_type="cooldown_test",
            severity=AlertSeverity.WARNING,
            title="Second Alert",
            message="This should be in cooldown",
            source="test"
        )
        
        # La segunda alerta debería existir pero no debería enviar notificaciones
        assert alert2 is not None
        assert len(alert_manager.alerts) == 2
    
    @pytest.mark.asyncio
    async def test_historical_metrics_persistence(self):
        """Test persistencia de métricas históricas"""
        metrics_collector = MetricsCollector()
        
        # Recolectar múltiples métricas
        for i in range(10):
            await metrics_collector.collect_system_metrics()
            await asyncio.sleep(0.1)  # Pequeña pausa
        
        # Verificar que se almacenaron las métricas
        assert len(metrics_collector.metrics_history['system']) == 10
        
        # Obtener métricas históricas
        historical = metrics_collector.get_historical_metrics("system", 1)
        assert len(historical) == 10
        
        # Verificar que las métricas están ordenadas por timestamp
        timestamps = [metric["timestamp"] for metric in historical]
        assert timestamps == sorted(timestamps)
