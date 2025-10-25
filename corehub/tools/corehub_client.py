"""
CoreHub Client para comunicación con la API
"""

import requests
from typing import Dict, Any, Optional
from loguru import logger


class CoreHubClient:
    """Cliente para comunicación con CoreHub API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def health_check(self) -> Dict[str, Any]:
        """Verificar salud del sistema"""
        try:
            response = self.session.get(f"{self.base_url}/health/")
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code,
                "response": response.json() if response.content else {}
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_dashboard_overview(self) -> Dict[str, Any]:
        """Obtener vista general del dashboard"""
        try:
            response = self.session.get(f"{self.base_url}/dashboard/overview")
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            logger.error(f"Dashboard overview failed: {e}")
            return {}
    
    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear nueva tarea"""
        try:
            response = self.session.post(f"{self.base_url}/tasks/", json=task_data)
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            logger.error(f"Create task failed: {e}")
            return {}
    
    def get_tasks(self) -> Dict[str, Any]:
        """Obtener lista de tareas"""
        try:
            response = self.session.get(f"{self.base_url}/tasks/")
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            logger.error(f"Get tasks failed: {e}")
            return {}
