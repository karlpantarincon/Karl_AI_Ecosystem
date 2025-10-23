# Resumen Diario - {{fecha}}

## Tareas Completadas ({{count_completed}})
{{#completed_tasks}}
- [{{id}}] {{title}} - {{duration}}s - ${{cost}}
{{/completed_tasks}}

## Tareas Pendientes con Bloqueo
{{#blocked_tasks}}
- [{{id}}] {{title}} - Bloqueador: {{blocker}}
{{/blocked_tasks}}

## Incidencias
{{#incidents}}
- {{timestamp}}: {{description}}
{{/incidents}}

## Métricas
- Costo IA estimado: ${{total_cost}}
- Tiempo total: {{total_time}}
- Tasa de éxito: {{success_rate}}%

## Próximas Acciones
{{#next_actions}}
- {{action}}
{{/next_actions}}

## Enlaces
{{#prs}}
- PR: [{{title}}]({{url}})
{{/prs}}

---
*Reporte generado automáticamente por CoreHub*
