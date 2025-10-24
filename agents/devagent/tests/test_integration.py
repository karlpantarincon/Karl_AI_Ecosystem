"""
Tests de integración para DevAgent
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

from agents.devagent.app.executor import DevAgentExecutor
from agents.devagent.tools.corehub_client import CoreHubClient
from agents.devagent.tools.git_wrapper import GitWrapper
from agents.devagent.tools.code_runner import CodeRunner
from agents.devagent.tools.scaffold import ScaffoldGenerator


@pytest.mark.integration
class TestDevAgentIntegration:
    """Tests de integración para DevAgent"""
    
    @pytest.fixture
    def mock_corehub_client(self):
        """Mock del cliente CoreHub"""
        client = Mock(spec=CoreHubClient)
        client.is_system_paused = AsyncMock(return_value=False)
        client.get_next_task = AsyncMock(return_value={
            "id": "T-001",
            "title": "Test Task",
            "type": "dev",
            "acceptance": ["Implement feature", "Write tests"],
            "priority": 1
        })
        client.log_event = AsyncMock(return_value=True)
        client.update_task_status = AsyncMock(return_value=True)
        return client
    
    @pytest.fixture
    def mock_git_wrapper(self):
        """Mock del wrapper de Git"""
        git = Mock(spec=GitWrapper)
        git.create_branch = AsyncMock(return_value=True)
        git.commit = AsyncMock(return_value=True)
        git.generate_pr_file = AsyncMock(return_value={
            "pr_id": "PR-001",
            "url": "https://github.com/test/repo/pull/1",
            "status": "created"
        })
        return git
    
    @pytest.fixture
    def mock_code_runner(self):
        """Mock del runner de código"""
        runner = Mock(spec=CodeRunner)
        runner.run_tests = AsyncMock(return_value={"passed": True, "coverage": 85})
        runner.run_lint = AsyncMock(return_value={"passed": True, "issues": 0})
        runner.run_type_check = AsyncMock(return_value={"passed": True, "errors": 0})
        return runner
    
    @pytest.fixture
    def mock_scaffold_generator(self):
        """Mock del generador de scaffolding"""
        scaffold = Mock(spec=ScaffoldGenerator)
        scaffold.generate_structure = AsyncMock(return_value=["file1.py", "file2.py"])
        return scaffold
    
    @pytest.fixture
    def devagent_executor(self, mock_corehub_client, mock_git_wrapper, mock_code_runner, mock_scaffold_generator):
        """Crear executor de DevAgent con mocks"""
        executor = DevAgentExecutor(mock_corehub_client)
        executor.git = mock_git_wrapper
        executor.code_runner = mock_code_runner
        executor.scaffold = mock_scaffold_generator
        return executor
    
    @pytest.mark.asyncio
    async def test_execute_task_full_workflow(self, devagent_executor, mock_corehub_client):
        """Test ejecución completa de una tarea"""
        # Ejecutar tarea
        result = await devagent_executor.execute_task()
        
        # Verificar que se obtuvo la tarea
        mock_corehub_client.get_next_task.assert_called_once_with("devagent")
        
        # Verificar que se logró el evento de completado
        mock_corehub_client.log_event.assert_called_with("devagent", "task_completed", {
            "task_id": "T-001",
            "result": result
        })
        
        # Verificar que se actualizó el estado de la tarea
        mock_corehub_client.update_task_status.assert_called_once_with("T-001", "done")
        
        # Verificar resultado
        assert result is not None
        assert result["task_id"] == "T-001"
        assert result["status"] == "completed"
        assert "plan_steps" in result
        assert "files_modified" in result
        assert "quality_checks" in result
        assert "duration_sec" in result
    
    @pytest.mark.asyncio
    async def test_execute_specific_task(self, devagent_executor, mock_corehub_client):
        """Test ejecución de tarea específica"""
        # Configurar mock para tarea específica
        mock_corehub_client.get_task = AsyncMock(return_value={
            "id": "T-002",
            "title": "Specific Task",
            "type": "ops",
            "acceptance": ["Configure system", "Test deployment"],
            "priority": 2
        })
        
        # Ejecutar tarea específica
        result = await devagent_executor.execute_specific_task("T-002")
        
        # Verificar que se obtuvo la tarea específica
        mock_corehub_client.get_task.assert_called_once_with("T-002")
        
        # Verificar resultado
        assert result is not None
        assert result["task_id"] == "T-002"
        assert result["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_task_execution_with_different_types(self, devagent_executor, mock_corehub_client):
        """Test ejecución de tareas de diferentes tipos"""
        task_types = ["dev", "ops", "test"]
        
        for task_type in task_types:
            # Configurar mock para cada tipo
            mock_corehub_client.get_next_task = AsyncMock(return_value={
                "id": f"T-{task_type}",
                "title": f"{task_type.title()} Task",
                "type": task_type,
                "acceptance": [f"Implement {task_type} feature"],
                "priority": 1
            })
            
            # Ejecutar tarea
            result = await devagent_executor.execute_task()
            
            # Verificar resultado
            assert result is not None
            assert result["task_id"] == f"T-{task_type}"
            assert result["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_error_handling_in_task_execution(self, devagent_executor, mock_corehub_client):
        """Test manejo de errores en ejecución de tareas"""
        # Configurar mock para lanzar excepción
        mock_corehub_client.get_next_task = AsyncMock(side_effect=Exception("Database connection failed"))
        
        # Ejecutar tarea (debería manejar el error)
        with pytest.raises(Exception):
            await devagent_executor.execute_task()
        
        # Verificar que se logró el evento de error
        mock_corehub_client.log_event.assert_called_with("devagent", "task_failed", {
            "error": "Database connection failed",
            "timestamp": mock_corehub_client.log_event.call_args[0][2]["timestamp"]
        })
    
    @pytest.mark.asyncio
    async def test_quality_checks_integration(self, devagent_executor, mock_code_runner):
        """Test integración de verificaciones de calidad"""
        # Configurar mocks para diferentes resultados
        mock_code_runner.run_tests.return_value = {"passed": True, "coverage": 90}
        mock_code_runner.run_lint.return_value = {"passed": False, "issues": 5}
        mock_code_runner.run_type_check.return_value = {"passed": True, "errors": 0}
        
        # Ejecutar verificaciones de calidad
        quality_results = await devagent_executor._run_quality_checks()
        
        # Verificar que se ejecutaron todas las verificaciones
        mock_code_runner.run_tests.assert_called_once()
        mock_code_runner.run_lint.assert_called_once()
        mock_code_runner.run_type_check.assert_called_once()
        
        # Verificar resultados
        assert quality_results["tests"]["passed"] is True
        assert quality_results["lint"]["passed"] is False
        assert quality_results["type_check"]["passed"] is True
        assert quality_results["overall"] == "fail"  # Porque lint falló
    
    @pytest.mark.asyncio
    async def test_git_integration(self, devagent_executor, mock_git_wrapper):
        """Test integración con Git"""
        # Configurar mock para tarea
        task = {
            "id": "T-003",
            "title": "Git Integration Test",
            "type": "dev",
            "acceptance": ["Create feature branch", "Commit changes"]
        }
        
        actions = ["file1.py", "file2.py", "test_file1.py"]
        
        # Ejecutar creación de PR
        pr_info = await devagent_executor._create_pr(task, actions)
        
        # Verificar que se creó la rama
        mock_git_wrapper.create_branch.assert_called_once()
        
        # Verificar que se hizo commit
        mock_git_wrapper.commit.assert_called_once()
        
        # Verificar que se generó archivo de PR
        mock_git_wrapper.generate_pr_file.assert_called_once()
        
        # Verificar resultado
        assert pr_info is not None
        assert "pr_id" in pr_info
        assert "url" in pr_info
        assert "status" in pr_info
    
    @pytest.mark.asyncio
    async def test_scaffold_integration(self, devagent_executor, mock_scaffold_generator):
        """Test integración con generador de scaffolding"""
        # Configurar mock
        mock_scaffold_generator.generate_structure.return_value = [
            "src/main.py",
            "src/utils.py",
            "tests/test_main.py"
        ]
        
        # Ejecutar generación de estructura
        structure = await mock_scaffold_generator.generate_structure("test_project")
        
        # Verificar resultado
        assert len(structure) == 3
        assert "src/main.py" in structure
        assert "tests/test_main.py" in structure
    
    @pytest.mark.asyncio
    async def test_system_paused_handling(self, devagent_executor, mock_corehub_client):
        """Test manejo cuando el sistema está pausado"""
        # Configurar mock para sistema pausado
        mock_corehub_client.is_system_paused = AsyncMock(return_value=True)
        
        # Ejecutar tarea (debería retornar None)
        result = await devagent_executor.execute_task()
        
        # Verificar que no se procesó la tarea
        assert result is None
        mock_corehub_client.get_next_task.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_no_tasks_available(self, devagent_executor, mock_corehub_client):
        """Test cuando no hay tareas disponibles"""
        # Configurar mock para no hay tareas
        mock_corehub_client.get_next_task = AsyncMock(return_value=None)
        
        # Ejecutar tarea
        result = await devagent_executor.execute_task()
        
        # Verificar que no se procesó nada
        assert result is None
        mock_corehub_client.log_event.assert_not_called()
        mock_corehub_client.update_task_status.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_task_execution_performance(self, devagent_executor, mock_corehub_client):
        """Test rendimiento de ejecución de tareas"""
        import time
        
        # Medir tiempo de ejecución
        start_time = time.time()
        result = await devagent_executor.execute_task()
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Verificar que la ejecución fue rápida (menos de 1 segundo para el mock)
        assert execution_time < 1.0
        
        # Verificar que se registró el tiempo de duración
        assert result["duration_sec"] > 0
        assert result["duration_sec"] < 1.0
    
    @pytest.mark.asyncio
    async def test_concurrent_task_execution(self, devagent_executor, mock_corehub_client):
        """Test ejecución concurrente de tareas"""
        # Configurar mocks para múltiples tareas
        tasks = [
            {"id": "T-001", "title": "Task 1", "type": "dev", "acceptance": ["Feature 1"], "priority": 1},
            {"id": "T-002", "title": "Task 2", "type": "ops", "acceptance": ["Config 2"], "priority": 2},
            {"id": "T-003", "title": "Task 3", "type": "test", "acceptance": ["Test 3"], "priority": 3}
        ]
        
        # Simular ejecución concurrente
        async def execute_task_with_id(task_id):
            mock_corehub_client.get_next_task = AsyncMock(return_value=tasks[int(task_id.split('-')[1]) - 1])
            return await devagent_executor.execute_task()
        
        # Ejecutar tareas concurrentemente
        results = await asyncio.gather(
            execute_task_with_id("T-001"),
            execute_task_with_id("T-002"),
            execute_task_with_id("T-003")
        )
        
        # Verificar que todas las tareas se ejecutaron
        assert len(results) == 3
        assert all(result is not None for result in results)
        assert all(result["status"] == "completed"] for result in results)
    
    @pytest.mark.asyncio
    async def test_metadata_persistence(self, devagent_executor, mock_corehub_client):
        """Test persistencia de metadatos durante ejecución"""
        # Configurar mock para tarea con metadatos
        task_with_metadata = {
            "id": "T-META",
            "title": "Task with Metadata",
            "type": "dev",
            "acceptance": ["Store metadata"],
            "priority": 1,
            "metadata": {
                "estimated_duration": 30,
                "complexity": "medium",
                "dependencies": ["T-001", "T-002"]
            }
        }
        
        mock_corehub_client.get_next_task = AsyncMock(return_value=task_with_metadata)
        
        # Ejecutar tarea
        result = await devagent_executor.execute_task()
        
        # Verificar que se preservaron los metadatos
        assert result["task_id"] == "T-META"
        assert result["status"] == "completed"
        
        # Verificar que se logró con metadatos
        log_call = mock_corehub_client.log_event.call_args
        assert log_call[0][1] == "task_completed"
        assert "result" in log_call[0][2]
