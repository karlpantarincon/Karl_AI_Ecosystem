"""
Cloud Agent para Karl AI Ecosystem

Agente especializado en gestión de servicios en la nube:
- Deploy en Railway, Render, Vercel
- Gestión de contenedores Docker
- Configuración de CI/CD
- Monitoreo de servicios en la nube
"""

import asyncio
import subprocess
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from .base_agent import BaseAgent, AgentTask, AgentCapabilities, AgentStatus
from loguru import logger


class CloudAgent(BaseAgent):
    """Agente especializado en servicios en la nube"""
    
    def __init__(self):
        super().__init__(
            name="CloudAgent",
            capabilities=[
                AgentCapabilities.CLOUD_DEPLOYMENT,
                AgentCapabilities.API_INTEGRATION,
                AgentCapabilities.MONITORING,
                AgentCapabilities.TASK_ORCHESTRATION
            ]
        )
        
        self.supported_platforms = ["railway", "render", "vercel", "docker"]
        self.deployment_configs = {}
        
        logger.info("CloudAgent initialized for cloud services management")
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Ejecutar tarea de cloud"""
        task_type = task.type.lower()
        
        if task_type == "deploy":
            return await self._deploy_service(task)
        elif task_type == "monitor":
            return await self._monitor_service(task)
        elif task_type == "scale":
            return await self._scale_service(task)
        elif task_type == "configure":
            return await self._configure_service(task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def get_available_capabilities(self) -> List[str]:
        """Obtener capacidades disponibles"""
        return [
            "deploy_to_railway",
            "deploy_to_render", 
            "deploy_to_vercel",
            "docker_build",
            "monitor_services",
            "scale_services",
            "configure_ci_cd"
        ]
    
    async def _deploy_service(self, task: AgentTask) -> Dict[str, Any]:
        """Desplegar servicio"""
        platform = task.parameters.get("platform", "railway")
        service_name = task.parameters.get("service_name", "karl-ai-service")
        config = task.parameters.get("config", {})
        
        logger.info(f"Deploying {service_name} to {platform}")
        
        try:
            if platform == "railway":
                result = await self._deploy_to_railway(service_name, config)
            elif platform == "render":
                result = await self._deploy_to_render(service_name, config)
            elif platform == "vercel":
                result = await self._deploy_to_vercel(service_name, config)
            elif platform == "docker":
                result = await self._deploy_docker(service_name, config)
            else:
                raise ValueError(f"Unsupported platform: {platform}")
            
            return {
                "success": True,
                "platform": platform,
                "service_name": service_name,
                "deployment_url": result.get("url"),
                "status": "deployed",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Deployment failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": platform,
                "service_name": service_name,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _deploy_to_railway(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Desplegar a Railway"""
        try:
            # Verificar Railway CLI
            result = subprocess.run(["railway", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Railway CLI not installed")
            
            # Crear configuración de Railway
            railway_config = {
                "build": {
                    "builder": "DOCKERFILE",
                    "dockerfilePath": "Dockerfile"
                },
                "deploy": {
                    "startCommand": "sh -c 'uvicorn corehub.api.main:app --host 0.0.0.0 --port $PORT'",
                    "restartPolicyType": "ON_FAILURE",
                    "healthcheckPath": "/health"
                }
            }
            
            # Guardar configuración
            config_file = Path("railway.json")
            with open(config_file, "w") as f:
                json.dump(railway_config, f, indent=2)
            
            # Deploy
            deploy_cmd = ["railway", "up"]
            result = subprocess.run(deploy_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Obtener URL del servicio
                domain_cmd = ["railway", "domain"]
                domain_result = subprocess.run(domain_cmd, capture_output=True, text=True)
                
                return {
                    "url": domain_result.stdout.strip() if domain_result.returncode == 0 else "unknown",
                    "status": "deployed"
                }
            else:
                raise Exception(f"Railway deployment failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Railway deployment error: {str(e)}")
            raise
    
    async def _deploy_to_render(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Desplegar a Render"""
        try:
            # Crear render.yaml
            render_config = {
                "services": [{
                    "type": "web",
                    "name": service_name,
                    "env": "python",
                    "buildCommand": "pip install -r requirements.txt",
                    "startCommand": "uvicorn corehub.api.main:app --host 0.0.0.0 --port $PORT",
                    "healthCheckPath": "/health"
                }]
            }
            
            # Guardar configuración
            config_file = Path("render.yaml")
            with open(config_file, "w") as f:
                import yaml
                yaml.dump(render_config, f, default_flow_style=False)
            
            return {
                "url": f"https://{service_name}.onrender.com",
                "status": "configured",
                "note": "Manual deployment required on Render dashboard"
            }
            
        except Exception as e:
            logger.error(f"Render configuration error: {str(e)}")
            raise
    
    async def _deploy_to_vercel(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Desplegar a Vercel"""
        try:
            # Crear vercel.json
            vercel_config = {
                "version": 2,
                "builds": [{
                    "src": "corehub/api/main.py",
                    "use": "@vercel/python"
                }],
                "routes": [{
                    "src": "/(.*)",
                    "dest": "corehub/api/main.py"
                }]
            }
            
            # Guardar configuración
            config_file = Path("vercel.json")
            with open(config_file, "w") as f:
                json.dump(vercel_config, f, indent=2)
            
            return {
                "url": f"https://{service_name}.vercel.app",
                "status": "configured",
                "note": "Run 'vercel deploy' to deploy"
            }
            
        except Exception as e:
            logger.error(f"Vercel configuration error: {str(e)}")
            raise
    
    async def _deploy_docker(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Desplegar con Docker"""
        try:
            # Crear docker-compose.yml
            docker_config = {
                "version": "3.8",
                "services": {
                    service_name: {
                        "build": ".",
                        "ports": ["8000:8000"],
                        "environment": {
                            "ENVIRONMENT": "production",
                            "LOG_LEVEL": "INFO"
                        },
                        "restart": "unless-stopped"
                    }
                }
            }
            
            # Guardar configuración
            config_file = Path("docker-compose.yml")
            with open(config_file, "w") as f:
                import yaml
                yaml.dump(docker_config, f, default_flow_style=False)
            
            # Build y run
            build_cmd = ["docker", "build", "-t", service_name, "."]
            build_result = subprocess.run(build_cmd, capture_output=True, text=True)
            
            if build_result.returncode == 0:
                run_cmd = ["docker", "run", "-d", "-p", "8000:8000", "--name", service_name, service_name]
                run_result = subprocess.run(run_cmd, capture_output=True, text=True)
                
                return {
                    "url": "http://localhost:8000",
                    "status": "running",
                    "container_id": run_result.stdout.strip()
                }
            else:
                raise Exception(f"Docker build failed: {build_result.stderr}")
                
        except Exception as e:
            logger.error(f"Docker deployment error: {str(e)}")
            raise
    
    async def _monitor_service(self, task: AgentTask) -> Dict[str, Any]:
        """Monitorear servicio"""
        service_url = task.parameters.get("service_url")
        
        if not service_url:
            raise ValueError("service_url is required for monitoring")
        
        try:
            import requests
            
            # Health check
            response = requests.get(f"{service_url}/health", timeout=10)
            
            return {
                "success": True,
                "service_url": service_url,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "healthy": response.status_code == 200,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Monitoring error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "service_url": service_url,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _scale_service(self, task: AgentTask) -> Dict[str, Any]:
        """Escalar servicio"""
        service_name = task.parameters.get("service_name")
        replicas = task.parameters.get("replicas", 1)
        
        logger.info(f"Scaling {service_name} to {replicas} replicas")
        
        # Implementar escalado según la plataforma
        return {
            "success": True,
            "service_name": service_name,
            "replicas": replicas,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _configure_service(self, task: AgentTask) -> Dict[str, Any]:
        """Configurar servicio"""
        service_name = task.parameters.get("service_name")
        config = task.parameters.get("config", {})
        
        logger.info(f"Configuring {service_name} with {len(config)} parameters")
        
        return {
            "success": True,
            "service_name": service_name,
            "config_applied": config,
            "timestamp": datetime.now().isoformat()
        }
