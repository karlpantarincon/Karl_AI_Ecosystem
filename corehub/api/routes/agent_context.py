"""
Endpoints de Contexto de Agentes para Karl AI Ecosystem
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime

from corehub.services.agent_context import (
    agent_context_manager, AgentContext, ProjectContext, TaskContext,
    AgentStatus, AgentCapability
)
from corehub.api.schemas import BaseResponse

router = APIRouter(prefix="/agent-context", tags=["agent-context"])


@router.post("/agents/register", response_model=BaseResponse)
async def register_agent(
    agent_id: str,
    name: str,
    capabilities: List[str],
    version: str = "1.0.0",
    environment: str = "production"
):
    """Registrar un nuevo agente"""
    try:
        # Convertir strings a enums
        capability_enums = [AgentCapability(cap) for cap in capabilities]
        
        context = agent_context_manager.register_agent(
            agent_id=agent_id,
            name=name,
            capabilities=capability_enums,
            version=version,
            environment=environment
        )
        
        return BaseResponse(
            success=True,
            data={
                "agent_id": context.agent_id,
                "name": context.name,
                "status": context.status.value,
                "capabilities": [c.value for c in context.capabilities],
                "version": context.version,
                "environment": context.environment,
                "context_hash": context.context_hash
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid capability: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/agents/{agent_id}/status", response_model=BaseResponse)
async def update_agent_status(
    agent_id: str,
    status: str,
    current_task: Optional[str] = None
):
    """Actualizar estado de un agente"""
    try:
        status_enum = AgentStatus(status)
        success = agent_context_manager.update_agent_status(
            agent_id=agent_id,
            status=status_enum,
            current_task=current_task
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return BaseResponse(success=True, data={"message": "Agent status updated"})
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/agents/{agent_id}/metrics", response_model=BaseResponse)
async def update_agent_metrics(
    agent_id: str,
    metrics: Dict[str, Any]
):
    """Actualizar métricas de un agente"""
    try:
        success = agent_context_manager.update_agent_metrics(
            agent_id=agent_id,
            metrics=metrics
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return BaseResponse(success=True, data={"message": "Agent metrics updated"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/agents/{agent_id}/resources", response_model=BaseResponse)
async def update_agent_resources(
    agent_id: str,
    resources: Dict[str, Any]
):
    """Actualizar uso de recursos de un agente"""
    try:
        success = agent_context_manager.update_agent_resources(
            agent_id=agent_id,
            resources=resources
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return BaseResponse(success=True, data={"message": "Agent resources updated"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}", response_model=BaseResponse)
async def get_agent_context(agent_id: str):
    """Obtener contexto de un agente"""
    try:
        context = agent_context_manager.get_agent_context(agent_id)
        
        if not context:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return BaseResponse(
            success=True,
            data={
                "agent_id": context.agent_id,
                "name": context.name,
                "status": context.status.value,
                "capabilities": [c.value for c in context.capabilities],
                "current_task": context.current_task,
                "performance_metrics": context.performance_metrics,
                "resource_usage": context.resource_usage,
                "last_activity": context.last_activity,
                "uptime_seconds": context.uptime_seconds,
                "version": context.version,
                "environment": context.environment,
                "configuration": context.configuration,
                "dependencies": context.dependencies,
                "health_score": context.health_score,
                "context_hash": context.context_hash
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents", response_model=BaseResponse)
async def get_all_agent_contexts():
    """Obtener contextos de todos los agentes"""
    try:
        contexts = agent_context_manager.get_all_agent_contexts()
        
        agents_data = []
        for context in contexts:
            agents_data.append({
                "agent_id": context.agent_id,
                "name": context.name,
                "status": context.status.value,
                "capabilities": [c.value for c in context.capabilities],
                "current_task": context.current_task,
                "last_activity": context.last_activity,
                "uptime_seconds": context.uptime_seconds,
                "version": context.version,
                "environment": context.environment,
                "health_score": context.health_score
            })
        
        return BaseResponse(success=True, data={"agents": agents_data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}/recommendations", response_model=BaseResponse)
async def get_agent_recommendations(agent_id: str):
    """Obtener recomendaciones para un agente"""
    try:
        recommendations = agent_context_manager.get_agent_recommendations(agent_id)
        
        return BaseResponse(
            success=True,
            data={
                "agent_id": agent_id,
                "recommendations": recommendations,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/project/context", response_model=BaseResponse)
async def set_project_context(
    project_name: str,
    project_type: str,
    technologies: List[str],
    architecture: str
):
    """Establecer contexto del proyecto"""
    try:
        context = agent_context_manager.set_project_context(
            project_name=project_name,
            project_type=project_type,
            technologies=technologies,
            architecture=architecture
        )
        
        return BaseResponse(
            success=True,
            data={
                "project_name": context.project_name,
                "project_type": context.project_type,
                "technologies": context.technologies,
                "architecture": context.architecture,
                "current_phase": context.current_phase,
                "business_rules": context.business_rules,
                "constraints": context.constraints,
                "goals": context.goals,
                "last_updated": context.last_updated
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/project/context", response_model=BaseResponse)
async def get_project_context():
    """Obtener contexto del proyecto"""
    try:
        context = agent_context_manager.get_project_context()
        
        if not context:
            raise HTTPException(status_code=404, detail="Project context not set")
        
        return BaseResponse(
            success=True,
            data={
                "project_name": context.project_name,
                "project_type": context.project_type,
                "technologies": context.technologies,
                "architecture": context.architecture,
                "current_phase": context.current_phase,
                "business_rules": context.business_rules,
                "constraints": context.constraints,
                "goals": context.goals,
                "metrics": context.metrics,
                "last_updated": context.last_updated
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/project/business-rule", response_model=BaseResponse)
async def add_business_rule(rule: str):
    """Agregar regla de negocio"""
    try:
        success = agent_context_manager.add_business_rule(rule)
        
        if not success:
            raise HTTPException(status_code=400, detail="No project context set")
        
        return BaseResponse(success=True, data={"message": "Business rule added"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/project/constraint", response_model=BaseResponse)
async def add_constraint(constraint: str):
    """Agregar restricción"""
    try:
        success = agent_context_manager.add_constraint(constraint)
        
        if not success:
            raise HTTPException(status_code=400, detail="No project context set")
        
        return BaseResponse(success=True, data={"message": "Constraint added"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/project/goal", response_model=BaseResponse)
async def add_goal(goal: str):
    """Agregar objetivo"""
    try:
        success = agent_context_manager.add_goal(goal)
        
        if not success:
            raise HTTPException(status_code=400, detail="No project context set")
        
        return BaseResponse(success=True, data={"message": "Goal added"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/context", response_model=BaseResponse)
async def create_task_context(
    task_id: str,
    task_type: str,
    priority: int,
    complexity: str,
    estimated_duration: int,
    required_capabilities: List[str]
):
    """Crear contexto de tarea"""
    try:
        # Convertir strings a enums
        capability_enums = [AgentCapability(cap) for cap in required_capabilities]
        
        context = agent_context_manager.create_task_context(
            task_id=task_id,
            task_type=task_type,
            priority=priority,
            complexity=complexity,
            estimated_duration=estimated_duration,
            required_capabilities=capability_enums
        )
        
        return BaseResponse(
            success=True,
            data={
                "task_id": context.task_id,
                "task_type": context.task_type,
                "priority": context.priority,
                "complexity": context.complexity,
                "estimated_duration": context.estimated_duration,
                "required_capabilities": [c.value for c in context.required_capabilities],
                "dependencies": context.dependencies,
                "acceptance_criteria": context.acceptance_criteria,
                "business_value": context.business_value,
                "technical_requirements": context.technical_requirements,
                "constraints": context.constraints,
                "related_tasks": context.related_tasks
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid capability: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}/best-agent", response_model=BaseResponse)
async def get_best_agent_for_task(task_id: str):
    """Obtener el mejor agente para una tarea"""
    try:
        best_agent = agent_context_manager.get_best_agent_for_task(task_id)
        
        if not best_agent:
            raise HTTPException(status_code=404, detail="No suitable agent found")
        
        return BaseResponse(
            success=True,
            data={
                "task_id": task_id,
                "best_agent": best_agent,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}/context", response_model=BaseResponse)
async def get_task_context(task_id: str):
    """Obtener contexto de una tarea"""
    try:
        context = agent_context_manager.get_task_context(task_id)
        
        if not context:
            raise HTTPException(status_code=404, detail="Task context not found")
        
        return BaseResponse(
            success=True,
            data={
                "task_id": context.task_id,
                "task_type": context.task_type,
                "priority": context.priority,
                "complexity": context.complexity,
                "estimated_duration": context.estimated_duration,
                "required_capabilities": [c.value for c in context.required_capabilities],
                "dependencies": context.dependencies,
                "acceptance_criteria": context.acceptance_criteria,
                "business_value": context.business_value,
                "technical_requirements": context.technical_requirements,
                "constraints": context.constraints,
                "related_tasks": context.related_tasks
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/insights", response_model=BaseResponse)
async def get_system_insights():
    """Obtener insights del sistema"""
    try:
        insights = agent_context_manager.get_system_insights()
        return BaseResponse(success=True, data=insights)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
