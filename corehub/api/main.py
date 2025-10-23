"""
CoreHub FastAPI application.

This is the main FastAPI application that provides:
- Health checks
- Task management
- Event logging
- Daily reports
- Admin controls
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from loguru import logger

# Cargar variables de entorno según el entorno
env = os.getenv("ENVIRONMENT", "development")
env_file = f"configs/env.{env}"
if Path(env_file).exists():
    load_dotenv(env_file)
else:
    load_dotenv()  # Fallback to .env

from corehub.db.database import create_tables, check_db_connection
from corehub.scheduler.jobs import start_scheduler, stop_scheduler
from corehub.api.routes import health, tasks, events, report, admin


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


# Create FastAPI application
app = FastAPI(
    title="CoreHub API",
    description="""
    ## CoreHub API
    
    Sistema de gestión de tareas y agentes para el ecosistema Karl AI.
    
    ### Características principales:
    - **Gestión de tareas**: Crear, actualizar y monitorear tareas del kanban
    - **Ejecución de agentes**: Controlar y monitorear la ejecución de agentes
    - **Eventos del sistema**: Registrar y consultar eventos del sistema
    - **Reportes**: Generar reportes de actividad y métricas
    - **Administración**: Controlar el estado del sistema
    
    ### Autenticación
    Actualmente no se requiere autenticación para el desarrollo.
    
    ### Límites de tasa
    - Máximo 1000 requests por hora por IP
    - Timeout de 30 segundos por request
    
    ### Códigos de estado
    - `200`: Operación exitosa
    - `400`: Error en la petición
    - `404`: Recurso no encontrado
    - `422`: Error de validación
    - `500`: Error interno del servidor
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "Karl AI Ecosystem",
        "url": "https://github.com/karl-ai/ecosystem",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(report.router, prefix="/report", tags=["reports"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "CoreHub API",
        "version": "0.1.0",
        "description": "El cerebro del ecosistema Karl AI",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/health",
            "tasks": "/tasks",
            "events": "/events", 
            "reports": "/report",
            "admin": "/admin",
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
