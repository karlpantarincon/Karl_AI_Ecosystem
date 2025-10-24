#!/usr/bin/env python3
"""
Script principal para ejecutar el ecosistema Karl AI completo
"""

import subprocess
import time
import json
import requests
from datetime import datetime

class KarlAIEcosystem:
    """Gestor principal del ecosistema Karl AI"""
    
    def __init__(self):
        self.corehub_url = "http://localhost:8000"
        self.mcp_server = None
    
    def check_docker_status(self):
        """Verifica el estado de Docker"""
        try:
            result = subprocess.run([
                "C:\\Program Files\\Docker\\Docker\\resources\\bin\\docker.exe", "ps"
            ], capture_output=True, text=True)
            return "karl-ai-corehub" in result.stdout
        except:
            return False
    
    def check_corehub_status(self):
        """Verifica el estado de CoreHub API"""
        try:
            response = requests.get(f"{self.corehub_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_mcp_server(self):
        """Inicia el servidor MCP"""
        try:
            self.mcp_server = subprocess.Popen([
                "python", "mcp-simple.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            return False
    
    def get_system_status(self):
        """Obtiene el estado completo del sistema"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "components": {
                "docker": {
                    "status": "running" if self.check_docker_status() else "stopped",
                    "container": "karl-ai-corehub"
                },
                "corehub_api": {
                    "status": "healthy" if self.check_corehub_status() else "unhealthy",
                    "url": self.corehub_url,
                    "endpoints": ["/health", "/dashboard/overview", "/docs"]
                },
                "mcp_server": {
                    "status": "running" if self.mcp_server else "stopped",
                    "tools": ["deploy_service", "get_system_status", "restart_service"],
                    "resources": ["corehub/status", "devagent/status", "dashboard/metrics", "system/health"]
                }
            },
            "overall_status": "healthy" if (
                self.check_docker_status() and 
                self.check_corehub_status() and 
                self.mcp_server
            ) else "degraded"
        }
        return status
    
    def run(self):
        """Ejecuta el ecosistema completo"""
        print("🚀 Karl AI Ecosystem - Iniciando sistema completo...")
        print("=" * 60)
        
        # Verificar Docker
        print("🐳 Verificando Docker...")
        if self.check_docker_status():
            print("✅ Docker: CoreHub contenedor ejecutándose")
        else:
            print("❌ Docker: CoreHub contenedor no encontrado")
            return
        
        # Verificar CoreHub API
        print("🔧 Verificando CoreHub API...")
        if self.check_corehub_status():
            print("✅ CoreHub API: Funcionando correctamente")
        else:
            print("❌ CoreHub API: No responde")
            return
        
        # Iniciar MCP Server
        print("🤖 Iniciando servidor MCP...")
        if self.start_mcp_server():
            print("✅ MCP Server: Iniciado correctamente")
        else:
            print("❌ MCP Server: Error al iniciar")
        
        print("\n" + "=" * 60)
        print("🎉 Ecosistema Karl AI completamente operativo!")
        print("\n📊 URLs disponibles:")
        print(f"  - CoreHub API: {self.corehub_url}")
        print(f"  - Health Check: {self.corehub_url}/health")
        print(f"  - API Docs: {self.corehub_url}/docs")
        print(f"  - Dashboard: {self.corehub_url}/dashboard/overview")
        
        print("\n🔧 Herramientas MCP disponibles:")
        print("  - deploy_service: Despliega servicios")
        print("  - get_system_status: Estado del sistema")
        print("  - restart_service: Reinicia servicios")
        
        print("\n💡 Para verificar el estado:")
        print("  python run-ecosystem.py --status")
        
        # Mostrar estado actual
        print("\n📈 Estado actual del sistema:")
        status = self.get_system_status()
        print(json.dumps(status, indent=2))
        
        return True

def main():
    """Función principal"""
    import sys
    
    ecosystem = KarlAIEcosystem()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        # Solo mostrar estado
        status = ecosystem.get_system_status()
        print(json.dumps(status, indent=2))
        return
    
    # Ejecutar ecosistema completo
    ecosystem.run()

if __name__ == "__main__":
    main()
