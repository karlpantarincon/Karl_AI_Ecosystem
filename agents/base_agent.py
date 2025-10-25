"""
Base Agent Class para Karl AI Ecosystem

Clase base para todos los agentes del ecosistema con capacidades comunes.
"""

import asyncio
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from loguru import logger


class AgentStatus(Enum):
    """Estados de un agente"""
    IDLE = "idle"
    RUNNING = "running"
    BUSY = "busy"
    ERROR = "error"
    STOPPED = "stopped"


class AgentCapabilities(Enum):
    """Capacidades de un agente"""
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    CLOUD_DEPLOYMENT = "cloud_deployment"
    DATA_PROCESSING = "data_processing"
    SECURITY_SCANNING = "security_scanning"
    API_INTEGRATION = "api_integration"
    TASK_ORCHESTRATION = "task_orchestration"
    MONITORING = "monitoring"
    TESTING = "testing"
    DOCUMENTATION = "documentation"


@dataclass
class AgentTask:
    """Estructura de una tarea para un agente"""
    id: str
    type: str
    priority: int
    description: str
    parameters: Dict[str, Any]
    created_at: datetime
    assigned_to: Optional[str] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class AgentMetrics:
    """Métricas de un agente"""
    tasks_completed: int = 0
    tasks_failed: int = 0
    average_execution_time: float = 0.0
    uptime: float = 0.0
    last_activity: Optional[datetime] = None
    resource_usage: Dict[str, float] = field(default_factory=dict)


class BaseAgent(ABC):
    """Clase base para todos los agentes del ecosistema"""
    
    def __init__(self, name: str, capabilities: List[AgentCapabilities]):
        self.id = str(uuid.uuid4())
        self.name = name
        self.capabilities = capabilities
        self.status = AgentStatus.IDLE
        self.metrics = AgentMetrics()
        self.tasks: List[AgentTask] = []
        self.running = False
        self.start_time = datetime.now()
        
        # Callbacks
        self.on_task_completed: Optional[Callable] = None
        self.on_task_failed: Optional[Callable] = None
        self.on_status_changed: Optional[Callable] = None
        
        logger.info(f"Agent {self.name} initialized with capabilities: {[c.value for c in capabilities]}")
    
    @abstractmethod
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Ejecutar una tarea específica del agente"""
        pass
    
    @abstractmethod
    async def get_available_capabilities(self) -> List[str]:
        """Obtener capacidades disponibles del agente"""
        pass
    
    async def start(self):
        """Iniciar el agente"""
        if self.running:
            logger.warning(f"Agent {self.name} is already running")
            return
        
        self.running = True
        self.status = AgentStatus.IDLE
        self.start_time = datetime.now()
        
        logger.info(f"Agent {self.name} started")
        await self._notify_status_change()
    
    async def stop(self):
        """Detener el agente"""
        if not self.running:
            logger.warning(f"Agent {self.name} is not running")
            return
        
        self.running = False
        self.status = AgentStatus.STOPPED
        
        logger.info(f"Agent {self.name} stopped")
        await self._notify_status_change()
    
    async def assign_task(self, task: AgentTask) -> bool:
        """Asignar una tarea al agente"""
        if not self.running:
            logger.error(f"Cannot assign task to stopped agent {self.name}")
            return False
        
        if self.status == AgentStatus.BUSY:
            logger.warning(f"Agent {self.name} is busy, queuing task {task.id}")
        
        task.assigned_to = self.id
        self.tasks.append(task)
        
        logger.info(f"Task {task.id} assigned to agent {self.name}")
        return True
    
    async def process_tasks(self):
        """Procesar tareas pendientes"""
        if not self.running:
            return
        
        pending_tasks = [task for task in self.tasks if task.status == "pending"]
        
        for task in pending_tasks:
            try:
                self.status = AgentStatus.BUSY
                await self._notify_status_change()
                
                logger.info(f"Processing task {task.id} with agent {self.name}")
                
                # Ejecutar la tarea
                result = await self.execute_task(task)
                
                # Actualizar métricas
                self.metrics.tasks_completed += 1
                self.metrics.last_activity = datetime.now()
                
                # Marcar tarea como completada
                task.status = "completed"
                task.result = result
                
                logger.info(f"Task {task.id} completed successfully")
                
                # Notificar callback
                if self.on_task_completed:
                    await self.on_task_completed(self, task, result)
                
            except Exception as e:
                logger.error(f"Error processing task {task.id}: {str(e)}")
                
                # Actualizar métricas
                self.metrics.tasks_failed += 1
                
                # Marcar tarea como fallida
                task.status = "failed"
                task.error = str(e)
                
                # Notificar callback
                if self.on_task_failed:
                    await self.on_task_failed(self, task, str(e))
            
            finally:
                self.status = AgentStatus.IDLE
                await self._notify_status_change()
    
    async def get_status(self) -> Dict[str, Any]:
        """Obtener estado del agente"""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "capabilities": [c.value for c in self.capabilities],
            "metrics": {
                "tasks_completed": self.metrics.tasks_completed,
                "tasks_failed": self.metrics.tasks_failed,
                "uptime": (datetime.now() - self.start_time).total_seconds(),
                "last_activity": self.metrics.last_activity.isoformat() if self.metrics.last_activity else None
            },
            "running": self.running,
            "pending_tasks": len([t for t in self.tasks if t.status == "pending"])
        }
    
    async def _notify_status_change(self):
        """Notificar cambio de estado"""
        if self.on_status_changed:
            await self.on_status_changed(self, self.status)
    
    def __str__(self):
        return f"Agent({self.name}, {self.status.value})"
    
    def __repr__(self):
        return f"Agent(id={self.id}, name={self.name}, status={self.status.value})"
