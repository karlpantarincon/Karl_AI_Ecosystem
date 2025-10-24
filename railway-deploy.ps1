# 🚀 Karl AI Ecosystem - Deploy en Railway (PowerShell)
# Script automatizado para deploy en Railway

param(
    [switch]$SkipGit,
    [switch]$SkipTests,
    [string]$Environment = "production"
)

# Configuración
$ErrorActionPreference = "Stop"

# Colores para output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Info { Write-ColorOutput "[INFO] $args" "Cyan" }
function Write-Success { Write-ColorOutput "[SUCCESS] $args" "Green" }
function Write-Warning { Write-ColorOutput "[WARNING] $args" "Yellow" }
function Write-Error { Write-ColorOutput "[ERROR] $args" "Red" }

Write-Info "🚀 Karl AI Ecosystem - Deploy en Railway"
Write-Info "========================================"

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "pyproject.toml")) {
    Write-Error "No se encontró pyproject.toml. Ejecuta desde el directorio raíz del proyecto."
    exit 1
}

# Verificar Git
if (-not $SkipGit) {
    Write-Info "Verificando estado de Git..."
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        Write-Warning "Hay cambios sin commitear:"
        Write-Host $gitStatus
        Write-Host ""
        $response = Read-Host "¿Deseas commitear y pushear los cambios? (y/N)"
        if ($response -match "^[Yy]$") {
            Write-Info "Commiteando cambios..."
            git add .
            git commit -m "Deploy Railway - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
            git push origin master
            Write-Success "Cambios commiteados y pusheados"
        } else {
            Write-Error "Abortando deploy. Commitea los cambios primero."
            exit 1
        }
    } else {
        Write-Success "Git está limpio"
    }
}

# Verificar Railway CLI
Write-Info "Verificando Railway CLI..."
try {
    $railwayVersion = railway --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Railway CLI no encontrado"
    }
    Write-Success "Railway CLI encontrado: $railwayVersion"
} catch {
    Write-Warning "Railway CLI no está instalado"
    Write-Info "Instalando Railway CLI..."
    try {
        npm install -g @railway/cli
        Write-Success "Railway CLI instalado"
    } catch {
        Write-Error "Error instalando Railway CLI. Instálalo manualmente: npm install -g @railway/cli"
        exit 1
    }
}

# Login en Railway
Write-Info "Verificando login en Railway..."
try {
    railway whoami 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "No logueado"
    }
    Write-Success "Ya estás logueado en Railway"
} catch {
    Write-Info "Iniciando sesión en Railway..."
    railway login
    Write-Success "Login exitoso"
}

# Crear proyecto si no existe
Write-Info "Verificando proyecto en Railway..."
try {
    railway status 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Proyecto no existe"
    }
    Write-Success "Proyecto ya existe"
} catch {
    Write-Info "Creando nuevo proyecto en Railway..."
    railway init
    Write-Success "Proyecto creado"
}

# Configurar variables de entorno
Write-Info "Configurando variables de entorno..."
railway variables set ENVIRONMENT=$Environment
railway variables set LOG_LEVEL=INFO
railway variables set NOTIFICATION_LOG_ENABLED=true
railway variables set API_HOST=0.0.0.0
Write-Success "Variables de entorno configuradas"

# Deploy
Write-Info "Iniciando deploy..."
railway up
Write-Success "Deploy iniciado"

# Obtener URL del servicio
Write-Info "Obteniendo URL del servicio..."
Start-Sleep -Seconds 5
$serviceUrl = railway domain 2>$null
if ($serviceUrl) {
    Write-Success "Servicio desplegado en: https://$serviceUrl"
    
    # Probar endpoints
    Write-Info "Probando endpoints..."
    Start-Sleep -Seconds 15  # Esperar a que el servicio esté listo
    
    # Health check
    try {
        $healthResponse = Invoke-WebRequest -Uri "https://$serviceUrl/health" -TimeoutSec 10 -UseBasicParsing
        if ($healthResponse.StatusCode -eq 200) {
            Write-Success "✅ Health check: OK"
        } else {
            Write-Warning "⚠️ Health check: Status $($healthResponse.StatusCode)"
        }
    } catch {
        Write-Warning "⚠️ Health check: No responde aún"
    }
    
    # API Docs
    try {
        $docsResponse = Invoke-WebRequest -Uri "https://$serviceUrl/docs" -TimeoutSec 10 -UseBasicParsing
        if ($docsResponse.StatusCode -eq 200) {
            Write-Success "✅ API Docs: OK"
        } else {
            Write-Warning "⚠️ API Docs: Status $($docsResponse.StatusCode)"
        }
    } catch {
        Write-Warning "⚠️ API Docs: No responde aún"
    }
    
    Write-Host ""
    Write-Success "🎉 Deploy completado exitosamente!"
    Write-Host ""
    Write-Info "📊 URLs disponibles:"
    Write-Host "  - Servicio: https://$serviceUrl"
    Write-Host "  - Health: https://$serviceUrl/health"
    Write-Host "  - API Docs: https://$serviceUrl/docs"
    Write-Host "  - Dashboard: https://$serviceUrl/dashboard/overview"
    Write-Host ""
    Write-Info "🔧 Comandos útiles:"
    Write-Host "  - Ver logs: railway logs"
    Write-Host "  - Ver status: railway status"
    Write-Host "  - Abrir servicio: railway open"
    
} else {
    Write-Warning "No se pudo obtener la URL del servicio"
    Write-Info "Verifica el deploy en railway.app"
}

Write-Success "Deploy completado!"
