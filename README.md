# Karl AI Ecosystem

Ecosistema completo de agentes AI con CoreHub (orquestador) y DevAgent (constructor automatizado) optimizado para desarrollo productivo.

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    DevAgent     │    │     CoreHub      │    │   SQLite/DB     │
│   (Constructor) │◄──►│   (Orquestador)  │◄──►│   (Base Datos)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Git Workflow  │    │   Scheduler     │    │   Event Logs    │
│   (Simulado)    │    │   (APScheduler) │    │   (JSON)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ✨ Características Principales

- **🚀 CoreHub API**: API REST completa con FastAPI
- **🤖 DevAgent**: Agente constructor con loop continuo y circuit breaker
- **📊 Sistema de Notificaciones**: Email, webhook y logging
- **⚡ Cache Inteligente**: Sistema de cache con TTL
- **🔧 CI/CD Pipeline**: GitHub Actions automatizado
- **📈 Monitoreo**: Métricas y reportes automáticos
- **🧪 Tests**: Cobertura de tests ≥70%
- **📚 Documentación**: API docs automáticas con Swagger

## 🚀 Inicio Rápido

### Requisitos

- Python 3.11+
- Poetry (recomendado)
- SQLite (incluido en Python)

### Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd Karl_AI_Ecosystem
   ```

2. **Instalar dependencias**
   ```bash
   poetry install
   ```

3. **Configurar entorno**
   ```bash
   # El sistema usa SQLite por defecto
   # No se requiere configuración adicional de base de datos
   ```

4. **Arrancar CoreHub**
   ```bash
   poetry run uvicorn corehub.api.main:app --reload --port 8000
   ```

5. **Ejecutar DevAgent**
   ```bash
   # Una vez
   poetry run python -m agents.devagent.app.main run_once
   
   # Loop continuo con prioridades
   poetry run python -m agents.devagent.app.main loop --interval 300 --priority 1
   ```

## 📋 Uso

### CoreHub API

**Endpoints principales:**

- `GET /health` - Estado del sistema
- `POST /tasks/next` - Obtener siguiente tarea
- `POST /events/log` - Registrar evento
- `GET /report/daily` - Reporte diario
- `POST /admin/pause` - Pausar sistema
- `GET /docs` - Documentación automática (Swagger)

**Ejemplo de uso:**
```bash
# Verificar salud del sistema
curl http://localhost:8000/health

# Obtener siguiente tarea
curl -X POST http://localhost:8000/tasks/next \
  -H "Content-Type: application/json" \
  -d '{"agent": "devagent"}'

# Ver documentación API
open http://localhost:8000/docs
```

### DevAgent

**Comandos disponibles:**

```bash
# Ejecutar una tarea
poetry run python -m agents.devagent.app.main run_once

# Loop continuo con configuración avanzada
poetry run python -m agents.devagent.app.main loop \
  --interval 300 \
  --max-tasks 100 \
  --priority 1

# Ejecutar tarea específica
poetry run python -m agents.devagent.app.main run --task-id T-101
```

### Sistema de Notificaciones

El sistema incluye notificaciones automáticas configuradas por entorno:

- **Desarrollo**: Solo logging
- **Testing**: Logging con nivel WARNING
- **Producción**: Email, webhook y logging

### Cache Inteligente

Sistema de cache con TTL configurable:

```python
from corehub.services.cache import cached

@cached(ttl=300)  # Cache por 5 minutos
def expensive_function():
    return "resultado"
```

## 🧪 Desarrollo

### Comandos útiles

```bash
# Formatear código
make fmt

# Linting y type checking
make lint

# Tests completos
make test

# Desarrollo
make dev

# Validación del sistema
./scripts/validate.sh
```

### Estructura del Proyecto

```
Karl_AI_Ecosystem/
├── corehub/                 # API y lógica central
│   ├── api/                # Endpoints FastAPI
│   ├── db/                 # Modelos y migraciones
│   ├── scheduler/          # Jobs programados
│   ├── services/           # Servicios (notifications, cache)
│   └── tests/             # Tests CoreHub
├── agents/                 # Agentes AI
│   └── devagent/          # Agente constructor
├── configs/               # Configuraciones por entorno
│   ├── env.dev           # Desarrollo
│   ├── env.test          # Testing
│   └── env.prod          # Producción
├── .github/workflows/    # CI/CD
├── scripts/              # Scripts de utilidad
└── playbooks/            # Guías y workflows
```

## 📊 Monitoreo y Métricas

### Reportes Diarios

Los reportes se generan automáticamente y contienen:

- Tareas completadas por agente
- Métricas de rendimiento
- Eventos del sistema
- Próximas acciones

### Métricas Disponibles

- **Costo IA**: Estimación de costos por hora
- **Tiempo de ejecución**: Duración de tareas
- **Tasa de éxito**: Porcentaje de tareas completadas
- **Cache hit ratio**: Efectividad del cache
- **Eventos del sistema**: Logs estructurados

## 🔧 Configuración

### Variables de Entorno

El sistema usa diferentes configuraciones por entorno:

**Desarrollo** (`configs/env.dev`):
```bash
POSTGRES_URL=sqlite:///./karl_ecosystem.db
LOG_LEVEL=DEBUG
NOTIFICATION_LOG_ENABLED=true
```

**Producción** (`configs/env.prod`):
```bash
POSTGRES_URL=postgresql://user:pass@localhost:5432/karl_ecosystem
LOG_LEVEL=INFO
NOTIFICATION_EMAIL_ENABLED=true
NOTIFICATION_WEBHOOK_ENABLED=true
```

### Configuración del DevAgent

El DevAgent incluye características avanzadas:

- **Circuit Breaker**: Protección contra fallos consecutivos
- **Exponential Backoff**: Reintentos inteligentes
- **Prioridades**: Filtrado por prioridad de tareas
- **Límites de recursos**: Control de tiempo y costos
- **Métricas**: Monitoreo de rendimiento

## 🚀 Deploy

### Desarrollo Local

```bash
# Arrancar todo el ecosistema
make setup  # Instala dependencias
make dev    # Arranca CoreHub
# En otra terminal:
make devagent-loop  # Arranca DevAgent en loop
```

### CI/CD Pipeline

El proyecto incluye pipelines automatizados:

- **CI**: Tests, linting, type checking, coverage
- **CD**: Deploy automático con health checks
- **Validación**: Scripts de validación del sistema

### Producción

1. **Configurar variables de entorno** para producción
2. **Ejecutar migraciones**: `poetry run alembic upgrade head`
3. **Arrancar con Gunicorn**: `gunicorn corehub.api.main:app -w 4 -k uvicorn.workers.UvicornWorker`
4. **Configurar proxy reverso** (Nginx/Apache)
5. **Monitorear logs** y métricas

## 📈 Estado del Proyecto

### ✅ Completado

- [x] CoreHub API funcional con FastAPI
- [x] Base de datos con migraciones (SQLite/PostgreSQL)
- [x] Scheduler con jobs programados
- [x] Sistema de notificaciones (T-103)
- [x] Optimización de consultas DB (T-104)
- [x] Documentación API completa (T-105)
- [x] Cache inteligente con TTL
- [x] DevAgent con loop continuo y circuit breaker
- [x] Pipeline CI/CD con GitHub Actions
- [x] Tests con cobertura mejorada
- [x] Configuración por entornos

### 🚧 En Desarrollo

- [ ] Dashboard web para interacción
- [ ] Scripts 24/7 para gestión de procesos
- [ ] Mejoras en información de agentes
- [ ] Tests de integración adicionales

## 🧪 Testing

### Cobertura de Tests

- **Tests principales**: 52/52 pasando (100%)
- **Cobertura actual**: 35% (mejorada desde 15%)
- **Servicios nuevos**: 100% de cobertura en notificaciones y cache

### Ejecutar Tests

```bash
# Tests completos
poetry run pytest

# Tests con coverage
poetry run pytest --cov=corehub --cov=agents --cov-report=html

# Tests específicos
poetry run pytest corehub/tests/test_notifications.py -v
```

## 🤝 Contribuir

1. Fork el repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentación**: [Wiki del proyecto](https://github.com/your-repo/wiki)
- **Discusiones**: [GitHub Discussions](https://github.com/your-repo/discussions)

---

**Desarrollado con ❤️ por Karl**

## 🎯 Próximos Pasos

Para completar el ecosistema al 100%:

1. **Dashboard Web**: Interfaz de usuario para interacción
2. **Scripts 24/7**: Gestión de procesos para operación continua
3. **Mejoras en Agentes**: Contexto de proyecto y reglas de negocio
4. **Tests Adicionales**: Cobertura completa del sistema

El sistema está ahora **significativamente más robusto y optimizado** para desarrollo productivo, con todas las funcionalidades core implementadas y funcionando correctamente.