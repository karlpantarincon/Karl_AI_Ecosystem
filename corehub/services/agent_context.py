"""
Sistema de Contexto de Agentes para Karl AI Ecosystem
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

from loguru import logger


class AgentStatus(Enum):
    """Estados de agentes"""
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class AgentCapability(Enum):
    """Capacidades de agentes"""
    CODE_GENERATION = "code_generation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    ANALYSIS = "analysis"
    OPTIMIZATION = "optimization"


@dataclass
class AgentContext:
    """Contexto completo de un agente"""
    agent_id: str
    name: str
    status: AgentStatus
    capabilities: List[AgentCapability]
    current_task: Optional[str]
    performance_metrics: Dict[str, Any]
    resource_usage: Dict[str, Any]
    last_activity: str
    uptime_seconds: int
    version: str
    environment: str
    configuration: Dict[str, Any]
    dependencies: List[str]
    health_score: float
    context_hash: str


@dataclass
class ProjectContext:
    """Contexto del proyecto actual"""
    project_name: str
    project_type: str
    technologies: List[str]
    architecture: str
    current_phase: str
    business_rules: List[str]
    constraints: List[str]
    goals: List[str]
    metrics: Dict[str, Any]
    last_updated: str


@dataclass
class TaskContext:
    """Contexto de una tarea específica"""
    task_id: str
    task_type: str
    priority: int
    complexity: str
    estimated_duration: int
    required_capabilities: List[AgentCapability]
    dependencies: List[str]
    acceptance_criteria: List[str]
    business_value: str
    technical_requirements: List[str]
    constraints: List[str]
    related_tasks: List[str]


class AgentContextManager:
    """Gestor de contexto de agentes"""
    
    def __init__(self):
        self.agent_contexts: Dict[str, AgentContext] = {}
        self.project_context: Optional[ProjectContext] = None
        self.task_contexts: Dict[str, TaskContext] = {}
        self.context_history: List[Dict[str, Any]] = []
        self.learning_data: Dict[str, Any] = {}
        
    def register_agent(self, agent_id: str, name: str, capabilities: List[AgentCapability], 
                      version: str = "1.0.0", environment: str = "production") -> AgentContext:
        """Registrar un nuevo agente"""
        context = AgentContext(
            agent_id=agent_id,
            name=name,
            status=AgentStatus.IDLE,
            capabilities=capabilities,
            current_task=None,
            performance_metrics={},
            resource_usage={},
            last_activity=datetime.utcnow().isoformat(),
            uptime_seconds=0,
            version=version,
            environment=environment,
            configuration={},
            dependencies=[],
            health_score=1.0,
            context_hash=""
        )
        
        # Generar hash del contexto
        context.context_hash = self._generate_context_hash(context)
        
        self.agent_contexts[agent_id] = context
        logger.info(f"Agent {agent_id} registered with capabilities: {[c.value for c in capabilities]}")
        
        return context
    
    def update_agent_status(self, agent_id: str, status: AgentStatus, 
                           current_task: Optional[str] = None) -> bool:
        """Actualizar estado de un agente"""
        if agent_id not in self.agent_contexts:
            logger.warning(f"Agent {agent_id} not found")
            return False
        
        context = self.agent_contexts[agent_id]
        context.status = status
        context.current_task = current_task
        context.last_activity = datetime.utcnow().isoformat()
        
        # Actualizar hash del contexto
        context.context_hash = self._generate_context_hash(context)
        
        logger.info(f"Agent {agent_id} status updated to {status.value}")
        return True
    
    def update_agent_metrics(self, agent_id: str, metrics: Dict[str, Any]) -> bool:
        """Actualizar métricas de un agente"""
        if agent_id not in self.agent_contexts:
            logger.warning(f"Agent {agent_id} not found")
            return False
        
        context = self.agent_contexts[agent_id]
        context.performance_metrics.update(metrics)
        context.last_activity = datetime.utcnow().isoformat()
        
        # Calcular health score
        context.health_score = self._calculate_health_score(context)
        
        # Actualizar hash del contexto
        context.context_hash = self._generate_context_hash(context)
        
        logger.info(f"Agent {agent_id} metrics updated")
        return True
    
    def update_agent_resources(self, agent_id: str, resources: Dict[str, Any]) -> bool:
        """Actualizar uso de recursos de un agente"""
        if agent_id not in self.agent_contexts:
            logger.warning(f"Agent {agent_id} not found")
            return False
        
        context = self.agent_contexts[agent_id]
        context.resource_usage.update(resources)
        context.last_activity = datetime.utcnow().isoformat()
        
        # Actualizar hash del contexto
        context.context_hash = self._generate_context_hash(context)
        
        logger.info(f"Agent {agent_id} resources updated")
        return True
    
    def set_project_context(self, project_name: str, project_type: str, 
                           technologies: List[str], architecture: str) -> ProjectContext:
        """Establecer contexto del proyecto"""
        self.project_context = ProjectContext(
            project_name=project_name,
            project_type=project_type,
            technologies=technologies,
            architecture=architecture,
            current_phase="development",
            business_rules=[],
            constraints=[],
            goals=[],
            metrics={},
            last_updated=datetime.utcnow().isoformat()
        )
        
        logger.info(f"Project context set for {project_name}")
        return self.project_context
    
    def add_business_rule(self, rule: str) -> bool:
        """Agregar regla de negocio"""
        if not self.project_context:
            logger.warning("No project context set")
            return False
        
        self.project_context.business_rules.append(rule)
        self.project_context.last_updated = datetime.utcnow().isoformat()
        
        logger.info(f"Business rule added: {rule}")
        return True
    
    def add_constraint(self, constraint: str) -> bool:
        """Agregar restricción"""
        if not self.project_context:
            logger.warning("No project context set")
            return False
        
        self.project_context.constraints.append(constraint)
        self.project_context.last_updated = datetime.utcnow().isoformat()
        
        logger.info(f"Constraint added: {constraint}")
        return True
    
    def add_goal(self, goal: str) -> bool:
        """Agregar objetivo"""
        if not self.project_context:
            logger.warning("No project context set")
            return False
        
        self.project_context.goals.append(goal)
        self.project_context.last_updated = datetime.utcnow().isoformat()
        
        logger.info(f"Goal added: {goal}")
        return True
    
    def create_task_context(self, task_id: str, task_type: str, priority: int,
                           complexity: str, estimated_duration: int,
                           required_capabilities: List[AgentCapability]) -> TaskContext:
        """Crear contexto de tarea"""
        context = TaskContext(
            task_id=task_id,
            task_type=task_type,
            priority=priority,
            complexity=complexity,
            estimated_duration=estimated_duration,
            required_capabilities=required_capabilities,
            dependencies=[],
            acceptance_criteria=[],
            business_value="",
            technical_requirements=[],
            constraints=[],
            related_tasks=[]
        )
        
        self.task_contexts[task_id] = context
        logger.info(f"Task context created for {task_id}")
        
        return context
    
    def get_best_agent_for_task(self, task_id: str) -> Optional[str]:
        """Obtener el mejor agente para una tarea"""
        if task_id not in self.task_contexts:
            logger.warning(f"Task {task_id} not found")
            return None
        
        task_context = self.task_contexts[task_id]
        required_capabilities = task_context.required_capabilities
        
        # Filtrar agentes disponibles
        available_agents = [
            agent_id for agent_id, context in self.agent_contexts.items()
            if context.status in [AgentStatus.IDLE, AgentStatus.ACTIVE]
        ]
        
        if not available_agents:
            logger.warning("No available agents found")
            return None
        
        # Calcular score para cada agente
        agent_scores = {}
        for agent_id in available_agents:
            context = self.agent_contexts[agent_id]
            score = self._calculate_agent_task_score(context, task_context)
            agent_scores[agent_id] = score
        
        # Retornar agente con mejor score
        best_agent = max(agent_scores, key=agent_scores.get)
        logger.info(f"Best agent for task {task_id}: {best_agent} (score: {agent_scores[best_agent]})")
        
        return best_agent
    
    def get_agent_context(self, agent_id: str) -> Optional[AgentContext]:
        """Obtener contexto de un agente"""
        return self.agent_contexts.get(agent_id)
    
    def get_all_agent_contexts(self) -> List[AgentContext]:
        """Obtener contextos de todos los agentes"""
        return list(self.agent_contexts.values())
    
    def get_project_context(self) -> Optional[ProjectContext]:
        """Obtener contexto del proyecto"""
        return self.project_context
    
    def get_task_context(self, task_id: str) -> Optional[TaskContext]:
        """Obtener contexto de una tarea"""
        return self.task_contexts.get(task_id)
    
    def get_agent_recommendations(self, agent_id: str) -> List[str]:
        """Obtener recomendaciones para un agente"""
        if agent_id not in self.agent_contexts:
            return []
        
        context = self.agent_contexts[agent_id]
        recommendations = []
        
        # Recomendaciones basadas en health score
        if context.health_score < 0.7:
            recommendations.append("Consider restarting the agent due to low health score")
        
        # Recomendaciones basadas en uso de recursos
        if context.resource_usage.get('cpu_percent', 0) > 80:
            recommendations.append("High CPU usage detected, consider optimization")
        
        if context.resource_usage.get('memory_percent', 0) > 85:
            recommendations.append("High memory usage detected, consider memory optimization")
        
        # Recomendaciones basadas en métricas de rendimiento
        if context.performance_metrics.get('error_rate', 0) > 5:
            recommendations.append("High error rate detected, review recent tasks")
        
        if context.performance_metrics.get('success_rate', 100) < 80:
            recommendations.append("Low success rate detected, review task execution")
        
        return recommendations
    
    def get_system_insights(self) -> Dict[str, Any]:
        """Obtener insights del sistema"""
        total_agents = len(self.agent_contexts)
        active_agents = len([a for a in self.agent_contexts.values() if a.status == AgentStatus.ACTIVE])
        idle_agents = len([a for a in self.agent_contexts.values() if a.status == AgentStatus.IDLE])
        busy_agents = len([a for a in self.agent_contexts.values() if a.status == AgentStatus.BUSY])
        error_agents = len([a for a in self.agent_contexts.values() if a.status == AgentStatus.ERROR])
        
        avg_health_score = sum(a.health_score for a in self.agent_contexts.values()) / total_agents if total_agents > 0 else 0
        
        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "idle_agents": idle_agents,
            "busy_agents": busy_agents,
            "error_agents": error_agents,
            "average_health_score": avg_health_score,
            "system_status": "healthy" if error_agents == 0 and avg_health_score > 0.8 else "degraded",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _generate_context_hash(self, context: AgentContext) -> str:
        """Generar hash del contexto"""
        context_data = {
            "agent_id": context.agent_id,
            "status": context.status.value,
            "capabilities": [c.value for c in context.capabilities],
            "current_task": context.current_task,
            "performance_metrics": context.performance_metrics,
            "resource_usage": context.resource_usage,
            "version": context.version,
            "environment": context.environment
        }
        
        context_str = json.dumps(context_data, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()
    
    def _calculate_health_score(self, context: AgentContext) -> float:
        """Calcular score de salud del agente"""
        score = 1.0
        
        # Penalizar por errores
        error_rate = context.performance_metrics.get('error_rate', 0)
        score -= error_rate / 100
        
        # Penalizar por uso alto de recursos
        cpu_usage = context.resource_usage.get('cpu_percent', 0)
        if cpu_usage > 80:
            score -= (cpu_usage - 80) / 200
        
        memory_usage = context.resource_usage.get('memory_percent', 0)
        if memory_usage > 85:
            score -= (memory_usage - 85) / 150
        
        # Bonificar por buen rendimiento
        success_rate = context.performance_metrics.get('success_rate', 100)
        score += (success_rate - 80) / 200 if success_rate > 80 else 0
        
        return max(0.0, min(1.0, score))
    
    def _calculate_agent_task_score(self, agent_context: AgentContext, task_context: TaskContext) -> float:
        """Calcular score de agente para una tarea específica"""
        score = 0.0
        
        # Score por capacidades requeridas
        required_capabilities = set(task_context.required_capabilities)
        agent_capabilities = set(agent_context.capabilities)
        capability_match = len(required_capabilities.intersection(agent_capabilities))
        score += capability_match / len(required_capabilities) * 0.4
        
        # Score por health score
        score += agent_context.health_score * 0.3
        
        # Score por estado del agente
        if agent_context.status == AgentStatus.IDLE:
            score += 0.2
        elif agent_context.status == AgentStatus.ACTIVE:
            score += 0.1
        
        # Score por rendimiento
        success_rate = agent_context.performance_metrics.get('success_rate', 100)
        score += success_rate / 100 * 0.1
        
        return score


# Instancia global del gestor de contexto
agent_context_manager = AgentContextManager()
