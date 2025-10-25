#!/usr/bin/env python3
"""
Test simple del sistema Karl AI
"""

import os
import sys

# Configurar variables de entorno
os.environ["ENVIRONMENT"] = "development"
os.environ["LOG_LEVEL"] = "INFO"
os.environ["DATABASE_URL"] = "sqlite:///./karl_ecosystem.db"

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_system():
    """Probar el sistema"""
    print("="*50)
    print("KARL AI ECOSYSTEM - TEST")
    print("="*50)
    
    try:
        # Test 1: CoreHub
        from corehub.api.main import app
        print("[OK] CoreHub API")
        
        # Test 2: DevAgent
        from agents.devagent.app.main import DevAgent
        print("[OK] DevAgent")
        
        # Test 3: Base de datos
        from corehub.db.database import check_db_connection
        db_ok = check_db_connection()
        print(f"[OK] Base de datos: {'Conectada' if db_ok else 'Error'}")
        
        # Test 4: API con TestClient
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get("/")
        print(f"[OK] API: Status {response.status_code}")
        
        print("\n[SUCCESS] Sistema funcionando correctamente")
        print("\nPara iniciar: python start.py")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        print("\n[SOLUCION] Ejecuta:")
        print("1. .\\venv\\Scripts\\activate")
        print("2. pip install -r requirements.txt")
        print("3. python test.py")
        return False

if __name__ == "__main__":
    test_system()
