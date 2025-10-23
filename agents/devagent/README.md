# DevAgent - Agente Constructor Automatizado

DevAgent es el agente constructor que convierte tareas del kanban en código productivo, generando endpoints, tests, documentación y PRs simulados.

## 🤖 Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CoreHub API   │    │    DevAgent     │    │   Git Workflow  │
│   (Task Source) │◄──►│   (Executor)    │◄──►│   (Simulated)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Kanban Tasks  │    │   Code Gen      │    │   PR Files      │
│   (JSON)        │    │   (Templates)   │    │   (Markdown)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Uso

### Comandos Básicos

```bash
# Ejecutar una tarea
poetry run python -m agents.devagent.app.main run_once

# Loop continuo (respeta system_paused)
poetry run python -m agents.devagent.app.main loop --interval 300

# Ejecutar tarea específica
poetry run python -m agents.devagent.app.main run --task-id T-101
```

### Workflow del Agente

1. **Verificar sistema**: Comprobar si `system_paused` está activo
2. **Obtener tarea**: Fetch de `/tasks/next` del CoreHub
3. **Generar plan**: Crear plan de implementación basado en acceptance criteria
4. **Ejecutar acciones**: Crear/editar archivos según el plan
5. **Quality checks**: Ejecutar tests, lint, type check
6. **Generar resultado**: Crear resumen y PR simulado
7. **Reportar**: Log evento a CoreHub y actualizar kanban

## 🛠️ Componentes

### CLI Principal (`app/main.py`)
```python
# Comandos disponibles
python -m agents.devagent.app.main run_once      # Una tarea
python -m agents.devagent.app.main loop          # Loop continuo
python -m agents.devagent.app.main run --task-id T-101  # Tarea específica
```

### Executor (`app/executor.py`)
```python
class DevAgentExecutor:
    """Orquesta la ejecución de tareas."""
    
    async def execute_task(self) -> Optional[Dict[str, Any]]:
        """Ejecuta una tarea del kanban."""
        
    async def execute_specific_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Ejecuta una tarea específica por ID."""
```

### Herramientas (`tools/`)

#### CoreHub Client (`tools/corehub_client.py`)
```python
class CoreHubClient:
    """Cliente HTTP para interactuar con CoreHub API."""
    
    async def get_next_task(self, agent: str) -> Optional[Dict[str, Any]]
    async def update_task_status(self, task_id: str, status: str) -> bool
    async def log_event(self, agent: str, event_type: str, payload: Dict[str, Any]) -> bool
```

#### Git Wrapper (`tools/git_wrapper.py`)
```python
class GitWrapper:
    """Operaciones Git para DevAgent."""
    
    async def create_branch(self, branch_name: str) -> bool
    async def commit(self, message: str, files: List[str]) -> bool
    async def generate_pr_file(self, task_id: str, pr_data: Dict[str, Any]) -> Dict[str, Any]
```

#### Code Runner (`tools/code_runner.py`)
```python
class CodeRunner:
    """Ejecución de tests y quality checks."""
    
    async def run_tests(self) -> Dict[str, Any]
    async def run_lint(self) -> Dict[str, Any]
    async def run_type_check(self) -> Dict[str, Any]
    async def run_all_quality_checks(self) -> Dict[str, Any]
```

#### Scaffold Generator (`tools/scaffold.py`)
```python
class ScaffoldGenerator:
    """Generación de templates y scaffolding."""
    
    async def generate_fastapi_endpoint(self, endpoint_name: str, task_data: Dict[str, Any]) -> str
    async def generate_test_file(self, test_name: str, task_data: Dict[str, Any]) -> str
    async def generate_service_class(self, service_name: str, task_data: Dict[str, Any]) -> str
```

## 📋 Prompt del Sistema

### Rol
Desarrollador backend automatizado que convierte tareas del kanban en código productivo.

### Workflow
1. **Fetch tarea** de CoreHub (`/tasks/next`)
2. **Analizar** acceptance criteria
3. **Generar PLAN** de implementación
4. **Ejecutar ACTIONS** (crear/editar archivos)
5. **Correr tests** y lint
6. **Generar RESULT** summary
7. **Reportar** a CoreHub (`/events/log`)

### Output Format
- **PLAN**: [pasos numerados]
- **ACTIONS**: [archivos modificados]
- **RESULT**: [resumen + rutas]
- **NEXT**: [siguiente micro-tarea o "DONE"]

### Definition of Done
- Tests pasan (pytest)
- Lint clean (ruff + black)
- Docs actualizadas
- PR creado (o simulado)

### Constraints
- Máximo 120 segundos por tarea
- Presupuesto: $0.50/hora
- Respetar `system_paused` flag

## 🧪 Testing

### Ejecutar Tests
```bash
# Todos los tests del DevAgent
poetry run pytest agents/devagent/tests/ -v

# Tests específicos
poetry run pytest agents/devagent/tests/test_executor.py -v

# Con coverage
poetry run pytest agents/devagent/tests/ --cov=agents --cov-report=html
```

### Estructura de Tests
```
agents/devagent/tests/
├── test_executor.py          # Tests del executor principal
├── test_corehub_client.py    # Tests del cliente CoreHub
├── test_git_wrapper.py       # Tests de operaciones Git
├── test_code_runner.py       # Tests de quality checks
└── test_scaffold.py          # Tests de generación de código
```

### Fixtures Disponibles
```python
@pytest.fixture
def mock_client():
    """Mock del cliente CoreHub."""
    client = AsyncMock(spec=CoreHubClient)
    client.is_system_paused.return_value = False
    client.get_next_task.return_value = {...}
    return client

@pytest.fixture
def executor(mock_client):
    """Executor con cliente mockeado."""
    return DevAgentExecutor(mock_client)
```

## 🔧 Configuración

### Variables de Entorno
```bash
# DevAgent específicas
DEVAGENT_MAX_RUNTIME_SECONDS=120
DEVAGENT_COST_PER_HOUR_USD=0.50
DEVAGENT_HEARTBEAT_MINUTES=5

# CoreHub API
COREHUB_BASE_URL=http://localhost:8000
```

### Configuración del Agente (`configs/agent_config.yaml`)
```yaml
name: DevAgent
role: "Desarrollador backend/automatizador"
mission: "Implementar tareas del CoreHub en código productivo"

scope:
  include: ["APIs internas", "tests", "docs", "scripts"]
  exclude: ["deploy prod", "acciones con costo"]

guardrails:
  cost_per_hour_usd_max: 0.50
  max_runtime_sec: 120
  max_concurrent_tasks: 1

quality_checks:
  run_tests: true
  run_lint: true
  check_coverage: true
  min_coverage: 70
```

## 📊 Monitoreo

### Eventos del Agente
```bash
# Ver eventos del DevAgent
curl http://localhost:8000/events/?agent=devagent

# Filtrar por tipo de evento
curl http://localhost:8000/events/?agent=devagent&event_type=task_start
```

### Métricas Disponibles
- **Tareas procesadas**: Total y por tipo
- **Tiempo de ejecución**: Promedio por tarea
- **Tasa de éxito**: Porcentaje de tareas completadas
- **Costos**: Estimación de costos de IA
- **Quality checks**: Resultados de tests y lint

### Logs
```bash
# Ver logs del DevAgent
grep "DevAgent" logs/corehub.log

# Logs específicos por comando
poetry run python -m agents.devagent.app.main run_once --log-level debug
```

## 🎯 Ejemplos de Uso

### Ejemplo 1: Endpoint FastAPI
```bash
# Tarea del kanban
{
  "id": "T-101",
  "title": "Implementar endpoint /classify para emails",
  "type": "dev",
  "acceptance": ["endpoint responde", "tests OK", "docs actualizadas"]
}

# DevAgent ejecuta:
# 1. Analiza requirements
# 2. Crea corehub/api/routes/classify.py
# 3. Crea corehub/tests/test_classify.py
# 4. Actualiza documentación
# 5. Ejecuta tests y lint
# 6. Genera PR simulado
```

### Ejemplo 2: Job de Scheduler
```bash
# Tarea del kanban
{
  "id": "T-102",
  "title": "Crear job de limpieza de logs antiguos",
  "type": "ops",
  "acceptance": ["job ejecuta", "logs eliminados", "tests OK"]
}

# DevAgent ejecuta:
# 1. Crea función de job en corehub/scheduler/jobs.py
# 2. Configura trigger en scheduler
# 3. Crea tests para el job
# 4. Documenta configuración
```

## 🔍 Troubleshooting

### Problemas Comunes

#### DevAgent no encuentra tareas
```bash
# Verificar CoreHub está corriendo
curl http://localhost:8000/health

# Verificar kanban
cat configs/kanban.json

# Verificar sistema no está pausado
curl http://localhost:8000/admin/pause
```

#### DevAgent falla al ejecutar tareas
```bash
# Ver logs detallados
poetry run python -m agents.devagent.app.main run_once --log-level debug

# Verificar conectividad con CoreHub
curl http://localhost:8000/tasks/next -X POST -H "Content-Type: application/json" -d '{"agent": "devagent"}'
```

#### Quality checks fallan
```bash
# Ejecutar tests manualmente
poetry run pytest corehub/tests/ -v

# Ejecutar lint manualmente
poetry run ruff corehub/ agents/

# Ejecutar type check manualmente
poetry run mypy corehub/ agents/
```

#### Git operations fallan
```bash
# Verificar repositorio Git
git status

# Verificar permisos
ls -la .git/

# Verificar configuración Git
git config --list
```

## 🚀 Desarrollo

### Agregar Nueva Herramienta
```python
# En agents/devagent/tools/
class MiNuevaHerramienta:
    """Mi nueva herramienta para DevAgent."""
    
    async def mi_funcion(self, param: str) -> Dict[str, Any]:
        """Implementar funcionalidad."""
        pass

# Integrar en executor.py
from agents.devagent.tools.mi_herramienta import MiNuevaHerramienta

class DevAgentExecutor:
    def __init__(self, client: CoreHubClient):
        self.mi_herramienta = MiNuevaHerramienta()
```

### Agregar Nuevo Template
```python
# En agents/devagent/tools/scaffold.py
def _get_mi_template(self) -> str:
    """Template para mi nuevo tipo de código."""
    return '''
# Mi template
def mi_funcion():
    """Mi función generada."""
    pass
'''

async def generate_mi_codigo(self, name: str, task_data: Dict[str, Any]) -> str:
    """Generar mi código."""
    template = self.templates["mi_template"]
    return template.replace("{{name}}", name)
```

## 📚 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)

---

**DevAgent** - El constructor que convierte ideas en código 🚀
