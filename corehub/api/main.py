"""
CoreHub FastAPI application optimized for v0.dev integration.

This is the main FastAPI application that provides:
- Health checks
- Task management
- Event logging
- Daily reports
- Admin controls
- Dashboard APIs for React frontend
- WebSocket real-time updates
- Comprehensive API documentation
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from dotenv import load_dotenv
from loguru import logger

# Cargar variables de entorno según el entorno
env = os.getenv("ENVIRONMENT", "development")
env_file = f"configs/env.{env}"
if Path(env_file).exists():
    load_dotenv(env_file)
else:
    load_dotenv()  # Fallback to .env

# Configuración específica para Render
if os.getenv("RENDER"):
    # En Render, usar variables de entorno directamente
    logger.info("Running on Render.com - using environment variables")

from corehub.db.database import create_tables, check_db_connection
from corehub.scheduler.jobs import start_scheduler, stop_scheduler
from corehub.api.routes import health, tasks, events, report, admin
from corehub.api.routes.dashboard import router as dashboard_router
from corehub.api.websocket import router as websocket_router
from corehub.api.middleware import setup_all_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting CoreHub...")
    
    # Create database tables
    create_tables()
    logger.info("Database tables created")
    
    # Check database connection
    if not check_db_connection():
        logger.error("Database connection failed")
        raise RuntimeError("Database connection failed")
    logger.info("Database connection healthy")
    
    # Start scheduler
    start_scheduler()
    logger.info("Scheduler started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CoreHub...")
    stop_scheduler()
    logger.info("Scheduler stopped")


# Create FastAPI application optimized for v0.dev
app = FastAPI(
    title="CoreHub API - v0.dev Ready",
    description="""
    ## CoreHub API - Optimized for React/v0.dev Integration
    
    Sistema de gestión de tareas y agentes para el ecosistema Karl AI con APIs optimizadas para frontend moderno.
    
    ### 🚀 Características principales:
    - **Dashboard APIs**: Endpoints específicos para componentes React
    - **WebSockets**: Datos en tiempo real para dashboards
    - **Gestión de tareas**: CRUD completo con validaciones Pydantic
    - **Ejecución de agentes**: Control y monitoreo en tiempo real
    - **Eventos del sistema**: Logging estructurado y consultas
    - **Reportes**: Métricas y analytics para dashboards
    - **Administración**: Control completo del sistema
    
    ### 🔌 Integración v0.dev:
    - **CORS configurado**: Para desarrollo local y producción
    - **Schemas optimizados**: Para componentes React
    - **WebSockets**: Para actualizaciones en tiempo real
    - **Documentación OpenAPI**: Para generación automática de clientes
    
    ### 🔒 Seguridad:
    - Rate limiting: 1000 requests/minuto por IP
    - Security headers: HSTS, CSP, XSS protection
    - Request validation: Tamaño y formato
    - Error handling: Respuestas consistentes
    
    ### 📊 Endpoints Dashboard:
    - `GET /dashboard/overview` - Vista general del sistema
    - `GET /dashboard/tasks` - Lista de tareas con filtros
    - `GET /dashboard/metrics` - Métricas para gráficos
    - `GET /dashboard/logs` - Logs del sistema
    - `GET /dashboard/agents` - Estado de agentes
    - `POST /dashboard/tasks/{id}/status` - Actualizar estado
    - `POST /dashboard/agents/{name}/control` - Control de agentes
    
    ### 🌐 WebSockets:
    - `WS /ws/dashboard` - Updates del dashboard
    - `WS /ws/logs` - Stream de logs en tiempo real
    - `WS /ws/metrics` - Métricas en tiempo real
    
    ### 📝 Autenticación:
    Actualmente no se requiere autenticación para desarrollo.
    Para producción, configurar JWT o API keys.
    
    ### 🎯 Uso con v0.dev:
    1. Clona este repositorio
    2. Ejecuta `poetry install && poetry run uvicorn corehub.api.main:app --reload`
    3. Accede a `/docs` para ver la documentación interactiva
    4. Usa los endpoints dashboard para tu frontend React
    5. Conecta WebSockets para datos en tiempo real
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "Karl AI Ecosystem",
        "url": "https://github.com/karlpantarincon/Karl_AI_Ecosystem",
        "email": "karl@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.karl-ai.com",
            "description": "Production server"
        }
    ]
)

# Setup all middleware for production-ready API
setup_all_middleware(app)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(report.router, prefix="/report", tags=["reports"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

# Include new dashboard and WebSocket routers
app.include_router(dashboard_router, tags=["dashboard"])
app.include_router(websocket_router, tags=["websockets"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with comprehensive API information."""
    return {
        "name": "CoreHub API - v0.dev Ready",
        "version": "2.0.0",
        "description": "El cerebro del ecosistema Karl AI - Optimizado para React/v0.dev",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "healthy",
        "features": [
            "Dashboard APIs para React",
            "WebSockets en tiempo real",
            "Documentación OpenAPI completa",
            "Middleware de seguridad",
            "Validaciones Pydantic",
            "Rate limiting",
            "CORS configurado para v0.dev"
        ],
        "endpoints": {
            "health": "/health",
            "tasks": "/tasks",
            "events": "/events", 
            "reports": "/report",
            "admin": "/admin",
            "dashboard": "/dashboard",
            "websockets": "/ws",
            "docs": "/docs",
            "openapi": "/openapi.json"
        },
        "websockets": {
            "dashboard": "/ws/dashboard",
            "logs": "/ws/logs",
            "metrics": "/ws/metrics"
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_spec": "/openapi.json"
        },
        "integration": {
            "v0_dev_ready": True,
            "react_optimized": True,
            "cors_enabled": True,
            "realtime_updates": True
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    uvicorn.run(
        "corehub.api.main:app",
        host=host,
        port=port,
        reload=True,
    )
