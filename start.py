#!/usr/bin/env python3
"""
Karl AI Ecosystem - Script de inicio único
"""

import os
import sys
import uvicorn

# Configurar variables de entorno
os.environ["ENVIRONMENT"] = "development"
os.environ["LOG_LEVEL"] = "INFO"
os.environ["DATABASE_URL"] = "sqlite:///./karl_ecosystem.db"

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Función principal"""
    print("="*60)
    print("KARL AI ECOSYSTEM")
    print("="*60)
    print("Iniciando sistema...")
    print("")
    print("URLs disponibles:")
    print("- API: http://localhost:8000")
    print("- Dashboard: http://localhost:8000/dashboard/overview")
    print("- Docs: http://localhost:8000/docs")
    print("")
    print("Agentes disponibles:")
    print("- DevAgent (Constructor)")
    print("- CloudAgent (Servicios en la nube)")
    print("- DataAgent (Procesamiento de datos)")
    print("- SecurityAgent (Seguridad)")
    print("- IntegrationAgent (APIs externas)")
    print("")
    print("Presiona Ctrl+C para detener")
    print("="*60)
    
    try:
        from corehub.api.main import app
        
        # Iniciar servidor
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"[ERROR] Dependencia faltante: {e}")
        print("[SOLUCION] Ejecuta:")
        print("1. .\\venv\\Scripts\\activate")
        print("2. pip install -r requirements.txt")
        print("3. python start.py")
    except KeyboardInterrupt:
        print("\n[INFO] Sistema detenido")
    except Exception as e:
        print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
    main()
