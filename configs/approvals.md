# Matriz de Aprobaciones

## Requiere aprobación humana
- Deploy a producción
- Gastos o llamadas externas con costo
- Publicar contenido fuera de entorno de prueba
- Modificar configuraciones críticas del sistema
- Acceso a datos sensibles

## Límites automáticos
- MAX_TASK_SECONDS = 120
- BUDGET_HOURLY_USD = 0.50
- MAX_CONCURRENT_TASKS = 3
- MAX_DAILY_COST_USD = 5.00

## Kill-switch
POST /admin/pause para detener todo el sistema

## Escalación
- Problemas críticos: Notificar inmediatamente
- Errores de sistema: Log y retry automático
- Fallos de conectividad: Reintentar con backoff exponencial

## Auditoría
- Todos los cambios se registran en eventos
- Logs estructurados en formato JSON
- Métricas de rendimiento y costos
