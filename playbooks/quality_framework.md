# Framework de Calidad - Karl AI Ecosystem

## Checklist Universal de Calidad

### ✅ Código
- [ ] **Tests pasan**: `make test` ejecuta sin errores
- [ ] **Coverage ≥ 70%**: `poetry run pytest --cov=corehub --cov=agents --cov-fail-under=70`
- [ ] **Lint clean**: `make lint` sin errores
- [ ] **Type hints**: mypy sin errores en código crítico
- [ ] **Documentación**: docstrings en funciones públicas
- [ ] **Sin secretos**: no hardcoded secrets en el código

### ✅ Arquitectura
- [ ] **Separación de responsabilidades**: cada módulo tiene un propósito claro
- [ ] **Dependencias mínimas**: solo las librerías necesarias
- [ ] **Configuración externa**: variables de entorno para configuración
- [ ] **Logs estructurados**: formato JSON para logs
- [ ] **Manejo de errores**: excepciones capturadas y logeadas

### ✅ Seguridad
- [ ] **Sin secretos en repo**: usar `.env.example` como template
- [ ] **Validación de inputs**: todos los endpoints validan entrada
- [ ] **Autenticación**: endpoints protegidos cuando sea necesario
- [ ] **Rate limiting**: protección contra abuso
- [ ] **Sanitización**: inputs sanitizados antes de procesar

### ✅ Performance
- [ ] **Queries optimizadas**: consultas DB eficientes
- [ ] **Caching**: cache apropiado para datos frecuentes
- [ ] **Timeouts**: timeouts configurados para operaciones externas
- [ ] **Resource limits**: límites de memoria y CPU
- [ ] **Monitoring**: métricas de performance

## Standards de Código

### Python Style Guide
```python
# ✅ Bueno
def process_task(task_id: str, priority: int) -> Dict[str, Any]:
    """
    Process a task with given priority.
    
    Args:
        task_id: Unique task identifier
        priority: Task priority (1-5)
        
    Returns:
        Dict containing processing result
        
    Raises:
        ValueError: If priority is invalid
    """
    if not 1 <= priority <= 5:
        raise ValueError("Priority must be between 1 and 5")
    
    # Implementation here
    return {"status": "processed", "task_id": task_id}

# ❌ Malo
def process_task(task_id, priority):
    # No type hints, no docstring, no validation
    return {"status": "processed"}
```

### Error Handling
```python
# ✅ Bueno
try:
    result = await process_task(task_id)
    logger.info(f"Task {task_id} processed successfully")
    return result
except ValidationError as e:
    logger.error(f"Validation error for task {task_id}: {e}")
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error(f"Unexpected error processing task {task_id}: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")

# ❌ Malo
result = process_task(task_id)  # No error handling
return result
```

### Logging
```python
# ✅ Bueno
from loguru import logger

logger.info("Starting task processing", task_id=task_id, priority=priority)
logger.error("Task processing failed", task_id=task_id, error=str(e))

# ❌ Malo
print(f"Processing task {task_id}")  # No structured logging
```

## Proceso de Revisión

### 1. Pre-commit Checks
```bash
# Ejecutar antes de cada commit
make fmt      # Formatear código
make lint     # Verificar linting
make test     # Ejecutar tests
```

### 2. Code Review Checklist
- [ ] **Funcionalidad**: ¿El código hace lo que se supone que hace?
- [ ] **Tests**: ¿Hay tests adecuados para la nueva funcionalidad?
- [ ] **Documentación**: ¿Está documentado apropiadamente?
- [ ] **Performance**: ¿Hay problemas de performance obvios?
- [ ] **Seguridad**: ¿Hay vulnerabilidades de seguridad?
- [ ] **Mantenibilidad**: ¿Es fácil de mantener y extender?

### 3. Testing Strategy
```python
# Unit Tests - Funciones individuales
def test_process_task_success():
    result = process_task("T-101", 1)
    assert result["status"] == "processed"

# Integration Tests - Componentes trabajando juntos
def test_api_endpoint_integration():
    response = client.post("/tasks/next", json={"agent": "devagent"})
    assert response.status_code == 200

# End-to-End Tests - Flujo completo
def test_devagent_workflow():
    # Test complete DevAgent workflow
    pass
```

### 4. Performance Testing
```python
# Load testing
def test_api_performance():
    start_time = time.time()
    for _ in range(100):
        response = client.get("/health")
        assert response.status_code == 200
    duration = time.time() - start_time
    assert duration < 5.0  # Should complete in under 5 seconds
```

## Métricas de Calidad

### Coverage Targets
- **CoreHub**: ≥ 80% (crítico para producción)
- **DevAgent**: ≥ 70% (funcionalidad compleja)
- **Tools**: ≥ 60% (utilidades)

### Performance Targets
- **API Response**: < 200ms para endpoints básicos
- **Database Queries**: < 100ms para consultas simples
- **DevAgent Execution**: < 120s por tarea
- **Memory Usage**: < 512MB por proceso

### Reliability Targets
- **Uptime**: 99.9% para CoreHub
- **Error Rate**: < 0.1% para operaciones críticas
- **Recovery Time**: < 5 minutos para fallos

## Herramientas de Calidad

### Linting
```bash
# Ruff - Fast Python linter
poetry run ruff corehub/ agents/

# MyPy - Type checking
poetry run mypy corehub/ agents/
```

### Testing
```bash
# Pytest - Test runner
poetry run pytest --cov=corehub --cov=agents

# Coverage report
poetry run pytest --cov=corehub --cov=agents --cov-report=html
```

### Security
```bash
# Safety - Check for known vulnerabilities
poetry run pip install safety
poetry run safety check

# Bandit - Security linter
poetry run pip install bandit
poetry run bandit -r corehub/ agents/
```

### Performance
```bash
# Profiling
poetry run python -m cProfile -o profile.stats corehub/api/main.py

# Memory profiling
poetry run pip install memory-profiler
poetry run python -m memory_profiler corehub/api/main.py
```

## Continuous Improvement

### 1. Code Quality Metrics
- Monitorear coverage trends
- Track linting errors over time
- Measure performance regressions

### 2. Automated Quality Gates
- CI/CD pipeline debe pasar todos los checks
- Coverage no puede bajar
- Performance no puede degradar

### 3. Regular Reviews
- Weekly code quality review
- Monthly architecture review
- Quarterly security audit

## Troubleshooting Común

### Coverage Issues
```bash
# Verificar coverage por archivo
poetry run pytest --cov=corehub --cov-report=term-missing

# Excluir archivos de coverage
# En pyproject.toml:
[tool.coverage.run]
omit = ["*/tests/*", "*/migrations/*"]
```

### Linting Issues
```bash
# Auto-fix issues
poetry run ruff --fix corehub/ agents/

# Ignorar reglas específicas
# En pyproject.toml:
[tool.ruff]
ignore = ["E501", "W503"]
```

### Performance Issues
```bash
# Profile específico
poetry run python -m cProfile -s cumtime corehub/api/main.py

# Memory profiling
poetry run python -m memory_profiler corehub/api/main.py
```

---

**Recuerda**: La calidad no es un destino, es un viaje continuo. 🚀
