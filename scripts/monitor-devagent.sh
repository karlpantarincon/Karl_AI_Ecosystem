#!/bin/bash

# 🔍 Karl AI DevAgent - Monitoring Script
# Script para monitorear el estado del DevAgent

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuración
SERVICE_NAME="devagent"
COREHUB_URL="http://localhost:8000"
LOG_FILE="/var/log/devagent-service.log"

# Función para verificar estado del servicio
check_service_status() {
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "✅ Servicio $SERVICE_NAME está activo"
        return 0
    else
        print_error "❌ Servicio $SERVICE_NAME no está activo"
        return 1
    fi
}

# Función para verificar CoreHub API
check_corehub_api() {
    if curl -f -s "$COREHUB_URL/health" > /dev/null 2>&1; then
        print_success "✅ CoreHub API está respondiendo"
        return 0
    else
        print_error "❌ CoreHub API no responde"
        return 1
    fi
}

# Función para verificar logs recientes
check_recent_logs() {
    if [ -f "$LOG_FILE" ]; then
        # Buscar errores en los últimos 5 minutos
        recent_errors=$(tail -n 100 "$LOG_FILE" | grep -i "error\|failed\|exception" | wc -l)
        if [ "$recent_errors" -gt 0 ]; then
            print_warning "⚠️ Se encontraron $recent_errors errores recientes en los logs"
            return 1
        else
            print_success "✅ No se encontraron errores recientes en los logs"
            return 0
        fi
    else
        print_warning "⚠️ Archivo de log no encontrado: $LOG_FILE"
        return 1
    fi
}

# Función para mostrar métricas del servicio
show_service_metrics() {
    print_status "📊 Métricas del servicio:"
    
    # Estado del servicio
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "Estado: Activo"
    else
        print_error "Estado: Inactivo"
    fi
    
    # Uptime del servicio
    uptime=$(systemctl show "$SERVICE_NAME" --property=ActiveEnterTimestamp --value 2>/dev/null || echo "N/A")
    if [ "$uptime" != "N/A" ]; then
        print_status "Iniciado: $uptime"
    fi
    
    # Uso de memoria
    memory_usage=$(systemctl show "$SERVICE_NAME" --property=MemoryCurrent --value 2>/dev/null || echo "N/A")
    if [ "$memory_usage" != "N/A" ]; then
        memory_mb=$((memory_usage / 1024 / 1024))
        print_status "Memoria: ${memory_mb}MB"
    fi
    
    # CPU usage (aproximado)
    cpu_usage=$(ps -o pcpu= -p $(systemctl show "$SERVICE_NAME" --property=MainPID --value 2>/dev/null) 2>/dev/null || echo "N/A")
    if [ "$cpu_usage" != "N/A" ]; then
        print_status "CPU: ${cpu_usage}%"
    fi
}

# Función para mostrar logs recientes
show_recent_logs() {
    print_status "📋 Logs recientes (últimas 10 líneas):"
    if [ -f "$LOG_FILE" ]; then
        tail -n 10 "$LOG_FILE"
    else
        print_warning "Archivo de log no encontrado"
    fi
}

# Función para mostrar estado completo
show_full_status() {
    print_status "🔍 Estado completo del DevAgent:"
    print_status "========================================"
    
    # Verificar servicio
    check_service_status
    service_status=$?
    
    # Verificar API
    check_corehub_api
    api_status=$?
    
    # Verificar logs
    check_recent_logs
    logs_status=$?
    
    # Mostrar métricas
    show_service_metrics
    
    # Mostrar logs recientes
    show_recent_logs
    
    # Estado general
    print_status "========================================"
    if [ $service_status -eq 0 ] && [ $api_status -eq 0 ] && [ $logs_status -eq 0 ]; then
        print_success "🎉 DevAgent está funcionando correctamente"
        exit 0
    else
        print_error "⚠️ DevAgent tiene problemas que requieren atención"
        exit 1
    fi
}

# Función para monitoreo continuo
monitor_continuous() {
    print_status "🔄 Iniciando monitoreo continuo (Ctrl+C para detener)..."
    
    while true; do
        clear
        print_status "🕐 $(date) - Monitoreo DevAgent"
        print_status "========================================"
        
        show_full_status
        
        print_status ""
        print_status "Próxima verificación en 30 segundos..."
        sleep 30
    done
}

# Función para reiniciar servicio
restart_service() {
    print_status "🔄 Reiniciando servicio DevAgent..."
    
    if systemctl restart "$SERVICE_NAME"; then
        print_success "✅ Servicio reiniciado correctamente"
        sleep 5
        check_service_status
    else
        print_error "❌ Error reiniciando servicio"
        exit 1
    fi
}

# Función para mostrar ayuda
show_help() {
    echo "🔍 Karl AI DevAgent - Monitor"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos:"
    echo "  status     - Mostrar estado completo (por defecto)"
    echo "  monitor    - Monitoreo continuo"
    echo "  restart    - Reiniciar servicio"
    echo "  logs       - Mostrar logs recientes"
    echo "  metrics    - Mostrar métricas del servicio"
    echo "  help       - Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 status"
    echo "  $0 monitor"
    echo "  $0 restart"
}

# Función principal
main() {
    case "${1:-status}" in
        "status")
            show_full_status
            ;;
        "monitor")
            monitor_continuous
            ;;
        "restart")
            restart_service
            ;;
        "logs")
            show_recent_logs
            ;;
        "metrics")
            show_service_metrics
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Comando desconocido: $1"
            show_help
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@"
