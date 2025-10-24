#!/bin/bash

# 🚀 Karl AI Ecosystem - Deploy en Railway
# Script automatizado para deploy en Railway

set -e

echo "🚀 Karl AI Ecosystem - Deploy en Railway"
echo "========================================"

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

# Verificar que estamos en el directorio correcto
if [ ! -f "pyproject.toml" ]; then
    print_error "No se encontró pyproject.toml. Ejecuta desde el directorio raíz del proyecto."
    exit 1
fi

# Verificar Git
print_status "Verificando estado de Git..."
if [ -n "$(git status --porcelain)" ]; then
    print_warning "Hay cambios sin commitear:"
    git status --short
    echo ""
    read -p "¿Deseas commitear y pushear los cambios? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Commiteando cambios..."
        git add .
        git commit -m "Deploy Railway - $(date '+%Y-%m-%d %H:%M:%S')"
        git push origin master
        print_success "Cambios commiteados y pusheados"
    else
        print_error "Abortando deploy. Commitea los cambios primero."
        exit 1
    fi
else
    print_success "Git está limpio"
fi

# Verificar Railway CLI
print_status "Verificando Railway CLI..."
if ! command -v railway &> /dev/null; then
    print_warning "Railway CLI no está instalado"
    print_status "Instalando Railway CLI..."
    npm install -g @railway/cli
    print_success "Railway CLI instalado"
else
    print_success "Railway CLI encontrado"
fi

# Login en Railway
print_status "Verificando login en Railway..."
if ! railway whoami &> /dev/null; then
    print_status "Iniciando sesión en Railway..."
    railway login
    print_success "Login exitoso"
else
    print_success "Ya estás logueado en Railway"
fi

# Crear proyecto si no existe
print_status "Verificando proyecto en Railway..."
if ! railway status &> /dev/null; then
    print_status "Creando nuevo proyecto en Railway..."
    railway init
    print_success "Proyecto creado"
else
    print_success "Proyecto ya existe"
fi

# Configurar variables de entorno
print_status "Configurando variables de entorno..."
railway variables set ENVIRONMENT=production
railway variables set LOG_LEVEL=INFO
railway variables set NOTIFICATION_LOG_ENABLED=true
print_success "Variables de entorno configuradas"

# Deploy
print_status "Iniciando deploy..."
railway up
print_success "Deploy iniciado"

# Obtener URL del servicio
print_status "Obteniendo URL del servicio..."
SERVICE_URL=$(railway domain)
if [ -n "$SERVICE_URL" ]; then
    print_success "Servicio desplegado en: https://$SERVICE_URL"
    
    # Probar endpoints
    print_status "Probando endpoints..."
    sleep 10  # Esperar a que el servicio esté listo
    
    # Health check
    if curl -f -s "https://$SERVICE_URL/health" > /dev/null; then
        print_success "✅ Health check: OK"
    else
        print_warning "⚠️ Health check: No responde aún"
    fi
    
    # API Docs
    if curl -f -s "https://$SERVICE_URL/docs" > /dev/null; then
        print_success "✅ API Docs: OK"
    else
        print_warning "⚠️ API Docs: No responde aún"
    fi
    
    echo ""
    print_success "🎉 Deploy completado exitosamente!"
    echo ""
    echo "📊 URLs disponibles:"
    echo "  - Servicio: https://$SERVICE_URL"
    echo "  - Health: https://$SERVICE_URL/health"
    echo "  - API Docs: https://$SERVICE_URL/docs"
    echo "  - Dashboard: https://$SERVICE_URL/dashboard/overview"
    echo ""
    echo "🔧 Comandos útiles:"
    echo "  - Ver logs: railway logs"
    echo "  - Ver status: railway status"
    echo "  - Abrir servicio: railway open"
    
else
    print_warning "No se pudo obtener la URL del servicio"
    print_status "Verifica el deploy en railway.app"
fi

print_success "Deploy completado!"
