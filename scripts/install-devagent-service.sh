#!/bin/bash

# 🚀 Karl AI DevAgent Service - Installation Script
# Script para instalar DevAgent como servicio del sistema

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
SERVICE_USER="devagent"
SERVICE_GROUP="devagent"
INSTALL_DIR="/opt/karl-ai-ecosystem"
VENV_DIR="$INSTALL_DIR/venv"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

print_status "🚀 Instalando DevAgent Service..."
print_status "========================================"

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    print_error "Este script debe ejecutarse como root (sudo)"
    exit 1
fi

# Verificar que estamos en el directorio correcto
if [ ! -f "devagent-service.py" ]; then
    print_error "No se encontró devagent-service.py. Ejecuta desde el directorio raíz del proyecto."
    exit 1
fi

# Crear usuario del servicio
print_status "Creando usuario del servicio..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd --system --shell /bin/false --home-dir "$INSTALL_DIR" --create-home "$SERVICE_USER"
    print_success "Usuario $SERVICE_USER creado"
else
    print_warning "Usuario $SERVICE_USER ya existe"
fi

# Crear directorio de instalación
print_status "Creando directorio de instalación..."
mkdir -p "$INSTALL_DIR"
chown "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR"

# Copiar archivos del proyecto
print_status "Copiando archivos del proyecto..."
cp -r . "$INSTALL_DIR/"
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR"

# Crear entorno virtual
print_status "Creando entorno virtual..."
cd "$INSTALL_DIR"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    print_success "Entorno virtual creado"
else
    print_warning "Entorno virtual ya existe"
fi

# Activar entorno virtual e instalar dependencias
print_status "Instalando dependencias..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt
print_success "Dependencias instaladas"

# Copiar archivo de servicio systemd
print_status "Configurando servicio systemd..."
cp "scripts/devagent-systemd.service" "$SERVICE_FILE"
print_success "Archivo de servicio copiado"

# Recargar systemd
print_status "Recargando systemd..."
systemctl daemon-reload
print_success "Systemd recargado"

# Habilitar servicio
print_status "Habilitando servicio..."
systemctl enable "$SERVICE_NAME"
print_success "Servicio habilitado"

# Mostrar estado
print_status "Estado del servicio:"
systemctl status "$SERVICE_NAME" --no-pager

print_success "🎉 DevAgent Service instalado correctamente!"
print_status ""
print_status "Comandos útiles:"
print_status "  - Iniciar servicio: sudo systemctl start $SERVICE_NAME"
print_status "  - Detener servicio: sudo systemctl stop $SERVICE_NAME"
print_status "  - Reiniciar servicio: sudo systemctl restart $SERVICE_NAME"
print_status "  - Ver estado: sudo systemctl status $SERVICE_NAME"
print_status "  - Ver logs: sudo journalctl -u $SERVICE_NAME -f"
print_status "  - Deshabilitar servicio: sudo systemctl disable $SERVICE_NAME"
print_status ""
print_status "Archivos importantes:"
print_status "  - Directorio: $INSTALL_DIR"
print_status "  - Logs: sudo journalctl -u $SERVICE_NAME"
print_status "  - Configuración: $SERVICE_FILE"
