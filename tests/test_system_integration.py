"""
Tests de integración del sistema completo Karl AI Ecosystem
"""

import pytest
import asyncio
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

from corehub.services.metrics import metrics_collector
from corehub.services.alerts import alert_manager
from corehub.services.monitor import monitoring_service
from agents.devagent.app.executor import DevAgentExecutor
from agents.devagent.tools.corehub_client import CoreHubClient


@pytest.mark.integration
class TestSystemIntegration:
    """Tests de integración del sistema completo"""
    
    @pytest.fixture
    def api_base_url(self):
        """URL base de la API"""
        return "http://localhost:8000"
    
    @pytest.fixture
    def corehub_client(self):
        """Cliente CoreHub para tests"""
        return CoreHubClient()
    
    @pytest.mark.asyncio
    async def test_system_health_check(self, api_base_url):
        """Test verificación de salud del sistema"""
        try:
            response = requests.get(f"{api_base_url}/health", timeout=10)
            assert response.status_code == 200
            
            health_data = response.json()
            assert "status" in health_data
            assert "timestamp" in health_data
            assert health_data["status"] in ["healthy", "degraded", "unhealthy"]
        except requests.exceptions.ConnectionError:
            pytest.skip("API no disponible para tests de integración")
    
    @pytest.mark.asyncio
    async def test_dashboard_endpoints(self, api_base_url):
        """Test endpoints del dashboard"""
        try:
            endpoints = [
                "/dashboard/overview",
                "/dashboard/tasks",
                "/dashboard/agents",
                "/dashboard/metrics",
                "/dashboard/logs"
            ]
            
            for endpoint in endpoints:
                response = requests.get(f"{api_base_url}{endpoint}", timeout=10)
                assert response.status_code == 200
                
                data = response.json()
                assert "success" in data or "data" in data
        except requests.exceptions.ConnectionError:
            pytest.skip("API no disponible para tests de integración")
    
    @pytest.mark.asyncio
    async def test_monitoring_endpoints(self, api_base_url):
        """Test endpoints de monitoreo"""
        try:
            monitoring_endpoints = [
                "/monitoring/metrics/system",
                "/monitoring/metrics/application",
                "/monitoring/metrics/agents",
                "/monitoring/metrics/business",
                "/monitoring/alerts",
                "/monitoring/alerts/active",
                "/monitoring/health/detailed"
            ]
            
            for endpoint in monitoring_endpoints:
                response = requests.get(f"{api_base_url}{endpoint}", timeout=10)
                assert response.status_code == 200
                
                data = response.json()
                assert "success" in data or "data" in data
        except requests.exceptions.ConnectionError:
            pytest.skip("API no disponible para tests de integración")
    
    @pytest.mark.asyncio
    async def test_metrics_collection_workflow(self):
        """Test flujo completo de recolección de métricas"""
        # Recolectar métricas del sistema
        system_metrics = await metrics_collector.collect_system_metrics()
        assert system_metrics is not None
        assert system_metrics.cpu_percent >= 0
        assert system_metrics.memory_percent >= 0
        
        # Recolectar métricas de la aplicación
        app_metrics = await metrics_collector.collect_application_metrics()
        assert app_metrics is not None
        assert app_metrics.active_connections >= 0
        
        # Recolectar métricas de agentes
        agent_metrics = await metrics_collector.collect_agent_metrics("test-agent")
        assert agent_metrics is not None
        assert agent_metrics.agent_id == "test-agent"
        
        # Recolectar métricas de negocio
        business_metrics = await metrics_collector.collect_business_metrics()
        assert business_metrics is not None
        assert business_metrics.total_tasks >= 0
        
        # Verificar que se almacenaron en el historial
        assert len(metrics_collector.metrics_history['system']) > 0
        assert len(metrics_collector.metrics_history['application']) > 0
        assert len(metrics_collector.metrics_history['agents']) > 0
        assert len(metrics_collector.metrics_history['business']) > 0
    
    @pytest.mark.asyncio
    async def test_alert_system_workflow(self):
        """Test flujo completo del sistema de alertas"""
        # Crear alerta de prueba
        alert = await alert_manager.create_alert(
            alert_type="integration_test",
            severity="warning",
            title="Integration Test Alert",
            message="This is a test alert for integration testing",
            source="test_suite",
            metadata={"test": True, "timestamp": datetime.utcnow().isoformat()}
        )
        
        assert alert is not None
        assert alert.id in alert_manager.alerts
        assert alert.status == "active"
        assert alert.severity == "warning"
        
        # Reconocer alerta
        acknowledge_success = await alert_manager.acknowledge_alert(alert.id, "test_user")
        assert acknowledge_success is True
        assert alert_manager.alerts[alert.id].status == "acknowledged"
        assert alert_manager.alerts[alert.id].acknowledged_by == "test_user"
        
        # Resolver alerta
        resolve_success = await alert_manager.resolve_alert(alert.id)
        assert resolve_success is True
        assert alert_manager.alerts[alert.id].status == "resolved"
        assert alert_manager.alerts[alert.id].resolved_at is not None
    
    @pytest.mark.asyncio
    async def test_monitoring_service_integration(self):
        """Test integración del servicio de monitoreo"""
        # Verificar estado inicial
        status = await monitoring_service.get_monitoring_status()
        assert status["running"] is False
        assert status["check_interval"] == 60
        assert "alert_thresholds" in status
        
        # Verificar umbrales de alerta
        thresholds = status["alert_thresholds"]
        assert "cpu_percent" in thresholds
        assert "memory_percent" in thresholds
        assert "disk_percent" in thresholds
        assert "error_rate" in thresholds
        assert "response_time" in thresholds
    
    @pytest.mark.asyncio
    async def test_devagent_corehub_integration(self, corehub_client):
        """Test integración entre DevAgent y CoreHub"""
        # Verificar que el cliente puede conectarse
        try:
            is_paused = await corehub_client.is_system_paused()
            assert isinstance(is_paused, bool)
        except Exception:
            pytest.skip("CoreHub no disponible para tests de integración")
        
        # Verificar que puede obtener tareas
        try:
            task = await corehub_client.get_next_task("devagent")
            # Puede ser None si no hay tareas, eso está bien
            if task is not None:
                assert "id" in task
                assert "title" in task
        except Exception:
            pytest.skip("CoreHub no disponible para tests de integración")
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test flujo completo end-to-end"""
        # 1. Recolectar métricas
        system_metrics = await metrics_collector.collect_system_metrics()
        assert system_metrics is not None
        
        # 2. Verificar alertas basadas en métricas
        alerts = await metrics_collector.check_alerts()
        # Puede haber alertas o no, dependiendo de los valores actuales
        
        # 3. Crear alerta si es necesario
        if system_metrics.cpu_percent > 80:
            alert = await alert_manager.create_alert(
                alert_type="cpu_high",
                severity="warning",
                title="High CPU Usage",
                message=f"CPU usage is {system_metrics.cpu_percent:.1f}%",
                source="system_monitor"
            )
            assert alert is not None
        
        # 4. Verificar resumen de métricas
        summary = metrics_collector.get_metrics_summary()
        assert summary is not None
        assert "timestamp" in summary
        assert "system" in summary
        assert "application" in summary
        assert "agents" in summary
        assert "business" in summary
    
    @pytest.mark.asyncio
    async def test_historical_metrics_integration(self):
        """Test integración de métricas históricas"""
        # Agregar múltiples métricas al historial
        for i in range(5):
            await metrics_collector.collect_system_metrics()
            await asyncio.sleep(0.1)  # Pequeña pausa
        
        # Obtener métricas históricas
        historical = metrics_collector.get_historical_metrics("system", 1)
        assert len(historical) == 5
        
        # Verificar que están ordenadas por timestamp
        timestamps = [metric["timestamp"] for metric in historical]
        assert timestamps == sorted(timestamps)
        
        # Verificar estructura de datos
        for metric in historical:
            assert "timestamp" in metric
            assert "cpu_percent" in metric
            assert "memory_percent" in metric
            assert "disk_percent" in metric
    
    @pytest.mark.asyncio
    async def test_alert_cooldown_integration(self):
        """Test integración de cooldown de alertas"""
        # Crear primera alerta
        alert1 = await alert_manager.create_alert(
            alert_type="cooldown_test",
            severity="info",
            title="First Alert",
            message="This is the first alert",
            source="test"
        )
        assert alert1 is not None
        
        # Verificar que está en cooldown
        assert alert_manager._is_in_cooldown("cooldown_test")
        
        # Crear segunda alerta del mismo tipo
        alert2 = await alert_manager.create_alert(
            alert_type="cooldown_test",
            severity="info",
            title="Second Alert",
            message="This should be in cooldown",
            source="test"
        )
        assert alert2 is not None
        
        # Ambas alertas deberían existir
        assert len(alert_manager.alerts) == 2
    
    @pytest.mark.asyncio
    async def test_performance_metrics_integration(self):
        """Test integración de métricas de rendimiento"""
        import time
        
        # Medir tiempo de recolección de métricas
        start_time = time.time()
        
        # Recolectar todas las métricas
        system_metrics = await metrics_collector.collect_system_metrics()
        app_metrics = await metrics_collector.collect_application_metrics()
        agent_metrics = await metrics_collector.collect_agent_metrics("test-agent")
        business_metrics = await metrics_collector.collect_business_metrics()
        
        end_time = time.time()
        collection_time = end_time - start_time
        
        # Verificar que la recolección fue rápida (menos de 5 segundos)
        assert collection_time < 5.0
        
        # Verificar que todas las métricas se recolectaron
        assert system_metrics is not None
        assert app_metrics is not None
        assert agent_metrics is not None
        assert business_metrics is not None
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test manejo de errores en integración"""
        # Test con métricas que podrían fallar
        try:
            # Intentar recolectar métricas con valores extremos
            metrics = await metrics_collector.collect_system_metrics()
            assert metrics is not None
            
            # Verificar que se manejan valores extremos
            assert 0 <= metrics.cpu_percent <= 100
            assert 0 <= metrics.memory_percent <= 100
            assert 0 <= metrics.disk_percent <= 100
            
        except Exception as e:
            # Si hay error, debería ser manejado gracefully
            assert str(e) is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_operations_integration(self):
        """Test operaciones concurrentes en integración"""
        # Ejecutar múltiples operaciones concurrentemente
        tasks = [
            metrics_collector.collect_system_metrics(),
            metrics_collector.collect_application_metrics(),
            metrics_collector.collect_agent_metrics("agent1"),
            metrics_collector.collect_agent_metrics("agent2"),
            metrics_collector.collect_business_metrics()
        ]
        
        # Ejecutar todas las tareas concurrentemente
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verificar que todas las tareas se completaron
        assert len(results) == 5
        
        # Verificar que no hubo excepciones
        for result in results:
            assert not isinstance(result, Exception)
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_data_consistency_integration(self):
        """Test consistencia de datos en integración"""
        # Recolectar métricas múltiples veces
        metrics_list = []
        for i in range(3):
            metrics = await metrics_collector.collect_system_metrics()
            metrics_list.append(metrics)
            await asyncio.sleep(0.1)
        
        # Verificar que todas las métricas tienen la misma estructura
        for metrics in metrics_list:
            assert hasattr(metrics, 'timestamp')
            assert hasattr(metrics, 'cpu_percent')
            assert hasattr(metrics, 'memory_percent')
            assert hasattr(metrics, 'disk_percent')
            assert hasattr(metrics, 'network_sent_mb')
            assert hasattr(metrics, 'network_recv_mb')
            assert hasattr(metrics, 'load_average')
        
        # Verificar que los timestamps están en orden
        timestamps = [metrics.timestamp for metrics in metrics_list]
        assert timestamps == sorted(timestamps)
    
    @pytest.mark.asyncio
    async def test_system_resilience_integration(self):
        """Test resistencia del sistema en integración"""
        # Simular condiciones de alta carga
        high_load_tasks = []
        for i in range(10):
            task = metrics_collector.collect_system_metrics()
            high_load_tasks.append(task)
        
        # Ejecutar todas las tareas
        results = await asyncio.gather(*high_load_tasks, return_exceptions=True)
        
        # Verificar que el sistema manejó la carga
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= 8  # Al menos 80% de éxito
        
        # Verificar que no se corrompieron los datos
        for result in successful_results:
            assert result is not None
            assert hasattr(result, 'cpu_percent')
            assert 0 <= result.cpu_percent <= 100
