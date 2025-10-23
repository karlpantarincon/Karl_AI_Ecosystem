# CoreHub - El Cerebro del Ecosistema

CoreHub es el orquestador central del ecosistema Karl AI que gestiona tareas, eventos, reportes y control del sistema.

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI API   │    │   PostgreSQL    │    │   APScheduler   │
│   (Endpoints)   │◄──►│   (Database)    │◄──►│   (Jobs)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Event Logs    │    │   Task Queue    │    │   Daily Reports │
│   (JSON)        │    │   (Kanban)      │    │   (Markdown)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Inicio Rápido

### Requisitos
- Python 3.11+
- PostgreSQL 12+
- Poetry

### Instalación
```bash
# Instalar dependencias
poetry install

# Configurar variables de entorno
cp configs/env.example .env
# Editar .env con tu configuración de PostgreSQL

# Ejecutar migraciones
poetry run alembic upgrade head

# Arrancar CoreHub
poetry run uvicorn corehub.api.main:app --reload --port 8000
```

## 📡 API Endpoints

### Health Check
```bash
# Verificar estado del sistema
curl http://localhost:8000/health

# Health check detallado
curl http://localhost:8000/health/detailed

# Verificar si está listo
curl http://localhost:8000/health/ready
```

### Gestión de Tareas
```bash
# Obtener siguiente tarea
curl -X POST http://localhost:8000/tasks/next \
  -H "Content-Type: application/json" \
  -d '{"agent": "devagent"}'

# Listar todas las tareas
curl http://localhost:8000/tasks/

# Obtener tarea específica
curl http://localhost:8000/tasks/T-101

# Actualizar estado de tarea
curl -X PUT http://localhost:8000/tasks/T-101/status \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

### Logging de Eventos
```bash
# Registrar evento
curl -X POST http://localhost:8000/events/log \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "devagent",
    "type": "task_start",
    "payload": {"task_id": "T-101"}
  }'

# Listar eventos
curl http://localhost:8000/events/

# Filtrar eventos por agente
curl http://localhost:8000/events/?agent=devagent
```

### Reportes
```bash
# Generar reporte diario
curl http://localhost:8000/report/daily

# Reporte de fecha específica
curl http://localhost:8000/report/daily?report_date=2025-10-22

# Obtener archivo de reporte
curl http://localhost:8000/report/daily/2025-10-22
```

### Administración
```bash
# Pausar sistema
curl -X POST http://localhost:8000/admin/pause \
  -H "Content-Type: application/json" \
  -d '{"paused": true}'

# Verificar estado de pausa
curl http://localhost:8000/admin/pause

# Listar flags del sistema
curl http://localhost:8000/admin/flags
```

## 🗄️ Base de Datos

### Modelos

#### Task
```python
class Task(Base):
    id = Column(String(50), primary_key=True)  # T-101, T-102, etc.
    title = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # dev, ops, test
    prio = Column(Integer, nullable=False)     # 1=highest, 5=lowest
    status = Column(String(50), nullable=False)  # todo, in_progress, done, blocked
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### Run
```python
class Run(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent = Column(String(100), nullable=False)  # devagent, testagent
    task_id = Column(String(50), nullable=True)  # FK to Task.id
    status = Column(String(50), nullable=False)  # started, completed, failed
    cost_usd = Column(Float, default=0.0)
    duration_sec = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### Event
```python
class Event(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent = Column(String(100), nullable=True)  # null for system events
    type = Column(String(100), nullable=False)  # task_start, health_check, etc.
    payload = Column(JSON, nullable=True)  # Additional event data
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### Flag
```python
class Flag(Base):
    key = Column(String(100), primary_key=True)  # system_paused, maintenance_mode
    value = Column(String(255), nullable=False)  # true, false, or other values
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Migraciones
```bash
# Crear nueva migración
poetry run alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
poetry run alembic upgrade head

# Revertir migración
poetry run alembic downgrade -1
```

## ⏰ Scheduler

### Jobs Configurados

#### Daily Report Job
- **Cron**: `09:00 America/Lima`
- **Función**: Genera reporte diario con métricas del día anterior
- **Output**: Archivo en `reports/daily/YYYY-MM-DD.md`

#### Health Check Job
- **Intervalo**: Cada 5 minutos
- **Función**: Verifica salud del sistema
- **Checks**: Conexión DB, tareas pendientes, flags del sistema

### Agregar Nuevo Job
```python
# En corehub/scheduler/jobs.py
async def mi_nuevo_job():
    """Mi nuevo job programado."""
    logger.info("🔄 Ejecutando mi nuevo job...")
    # Lógica del job aquí
    logger.info("✅ Mi nuevo job completado")

# Configurar en start_scheduler()
scheduler.add_job(
    mi_nuevo_job,
    CronTrigger(hour=2, minute=0),  # 2:00 AM
    id="mi_nuevo_job",
    name="Mi Nuevo Job",
    replace_existing=True
)
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Todos los tests
make test

# Solo tests de CoreHub
make test-corehub

# Tests con coverage
poetry run pytest --cov=corehub --cov-report=html
```

### Estructura de Tests
```
corehub/tests/
├── test_api_health.py      # Tests de health endpoints
├── test_api_tasks.py       # Tests de task management
├── test_api_events.py      # Tests de event logging
├── test_api_report.py      # Tests de report generation
├── test_api_admin.py       # Tests de admin controls
├── test_models.py          # Tests de database models
└── test_scheduler.py       # Tests de scheduled jobs
```

### Fixtures Disponibles
```python
@pytest.fixture
def client():
    """TestClient de FastAPI."""
    return TestClient(app)

@pytest.fixture
def db_session():
    """Sesión de base de datos para tests."""
    # Setup test database
    pass

@pytest.fixture
def mock_kanban():
    """Datos de kanban para tests."""
    return {
        "v": 1,
        "sprint": "2025-10-23",
        "tasks": [...]
    }
```

## 🔧 Configuración

### Variables de Entorno
```bash
# Base de datos
POSTGRES_URL=postgresql://user:pass@localhost:5432/karl_ecosystem

# Sistema
SYSTEM_TIMEZONE=America/Lima
BUDGET_HOURLY_USD=0.50
MAX_TASK_SECONDS=120

# API
API_HOST=0.0.0.0
API_PORT=8000

# Scheduler
DAILY_REPORT_HOUR=9
HEALTH_CHECK_INTERVAL_MINUTES=5
```

### Configuración de Logging
```python
# En corehub/api/main.py
from loguru import logger

# Configurar logging
logger.add(
    "logs/corehub.log",
    rotation="1 day",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
)
```

## 📊 Monitoreo

### Métricas Disponibles
- **Tareas**: Completadas, pendientes, bloqueadas
- **Runs**: Exitosos, fallidos, tiempo promedio
- **Eventos**: Por tipo, por agente, por día
- **Costos**: Estimación de costos de IA
- **Performance**: Tiempo de respuesta de endpoints

### Health Checks
```bash
# Health básico
curl http://localhost:8000/health

# Health detallado con métricas
curl http://localhost:8000/health/detailed

# Verificar readiness
curl http://localhost:8000/health/ready
```

### Logs
```bash
# Ver logs en tiempo real
tail -f logs/corehub.log

# Filtrar por nivel
grep "ERROR" logs/corehub.log

# Filtrar por componente
grep "scheduler" logs/corehub.log
```

## 🚀 Deploy

### Desarrollo
```bash
# Arrancar en modo desarrollo
make dev

# Con logs detallados
poetry run uvicorn corehub.api.main:app --reload --log-level debug
```

### Producción
```bash
# Con Gunicorn
poetry run gunicorn corehub.api.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Con variables de entorno
export POSTGRES_URL="postgresql://user:pass@localhost:5432/karl_prod"
export API_HOST="0.0.0.0"
export API_PORT="8000"
poetry run uvicorn corehub.api.main:app --host $API_HOST --port $API_PORT
```

### Docker
```bash
# Build imagen
docker build -t karl-corehub .

# Run container
docker run -p 8000:8000 \
  -e POSTGRES_URL="postgresql://user:pass@host:5432/karl" \
  karl-corehub
```

## 🔍 Troubleshooting

### Problemas Comunes

#### CoreHub no arranca
```bash
# Verificar dependencias
poetry install

# Verificar base de datos
poetry run alembic upgrade head

# Verificar variables de entorno
cat .env
```

#### Base de datos no conecta
```bash
# Verificar URL de conexión
echo $POSTGRES_URL

# Test de conexión
poetry run python -c "
from corehub.db.database import check_db_connection
print('DB connected:', check_db_connection())
"
```

#### Scheduler no ejecuta jobs
```bash
# Verificar logs del scheduler
grep "scheduler" logs/corehub.log

# Verificar timezone
echo $SYSTEM_TIMEZONE
```

#### Tests fallan
```bash
# Limpiar cache
make clean

# Reinstalar dependencias
poetry install --sync

# Ejecutar tests específicos
poetry run pytest corehub/tests/test_api_health.py -v
```

## 📚 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

---

**CoreHub** - El cerebro que orquesta todo el ecosistema Karl AI 🧠
