"""
Karl AI Ecosystem - Agents Module

Este módulo contiene todos los agentes especializados del ecosistema:
- DevAgent: Constructor y desarrollador
- CloudAgent: Gestión de servicios en la nube
- DataAgent: Procesamiento y análisis de datos
- SecurityAgent: Seguridad y monitoreo
- IntegrationAgent: Integración con APIs externas
"""

from .base_agent import BaseAgent, AgentCapabilities, AgentStatus
from .devagent import DevAgent
from .cloud_agent import CloudAgent
from .data_agent import DataAgent
from .security_agent import SecurityAgent
from .integration_agent import IntegrationAgent

__all__ = [
    "BaseAgent",
    "AgentCapabilities", 
    "AgentStatus",
    "DevAgent",
    "CloudAgent",
    "DataAgent",
    "SecurityAgent",
    "IntegrationAgent"
]