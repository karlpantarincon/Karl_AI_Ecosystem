#!/usr/bin/env python3
"""
Script para deploy automático en Railway
"""

import subprocess
import json
import time
import requests
from datetime import datetime

class RailwayDeployer:
    """Deployer automático para Railway"""
    
    def __init__(self):
        self.project_name = "karl-ai-ecosystem"
        self.service_name = "karl-ai-corehub"
    
    def check_git_status(self):
        """Verifica el estado de Git"""
        try:
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                print("⚠️ Hay cambios sin commitear:")
                print(result.stdout)
                return False
            return True
        except:
            print("❌ Error verificando Git")
            return False
    
    def commit_and_push(self):
        """Commit y push de cambios"""
        try:
            # Add todos los archivos
            subprocess.run(["git", "add", "."], check=True)
            
            # Commit
            commit_message = f"Deploy Railway - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            
            # Push
            subprocess.run(["git", "push", "origin", "master"], check=True)
            
            print("✅ Cambios commiteados y pusheados")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error en Git: {e}")
            return False
    
    def wait_for_deploy(self, url, timeout=300):
        """Espera a que el deploy esté listo"""
        print(f"⏳ Esperando deploy en {url}...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{url}/health", timeout=10)
                if response.status_code == 200:
                    print("✅ Deploy completado exitosamente!")
                    return True
            except:
                pass
            
            print(".", end="", flush=True)
            time.sleep(10)
        
        print(f"\n⏰ Timeout después de {timeout} segundos")
        return False
    
    def test_endpoints(self, base_url):
        """Prueba todos los endpoints"""
        endpoints = [
            "/health",
            "/",
            "/dashboard/overview",
            "/docs"
        ]
        
        print("\n🔍 Probando endpoints...")
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                status = "✅" if response.status_code == 200 else "❌"
                print(f"  {status} {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"  ❌ {endpoint}: Error - {e}")
    
    def deploy(self):
        """Ejecuta el deploy completo"""
        print("🚀 Iniciando deploy en Railway...")
        print("=" * 50)
        
        # Verificar Git
        print("1️⃣ Verificando Git...")
        if not self.check_git_status():
            print("❌ Hay cambios sin commitear. Abortando deploy.")
            return False
        
        # Commit y push
        print("2️⃣ Commiteando y pusheando cambios...")
        if not self.commit_and_push():
            print("❌ Error en Git. Abortando deploy.")
            return False
        
        print("3️⃣ Deploy iniciado en Railway...")
        print("💡 Ve a railway.app para monitorear el deploy")
        print("🌐 URL esperada: https://karl-ai-corehub.railway.app")
        
        print("\n📋 Pasos manuales:")
        print("1. Ve a railway.app")
        print("2. Selecciona tu proyecto")
        print("3. Monitorea el deploy")
        print("4. Verifica las variables de entorno")
        print("5. Prueba la URL del servicio")
        
        return True

def main():
    """Función principal"""
    deployer = RailwayDeployer()
    deployer.deploy()

if __name__ == "__main__":
    main()
