# 🚀 Deploy en Railway - Karl AI Ecosystem

## 📋 Prerrequisitos

### 1. **Railway CLI**
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Verificar instalación
railway --version
```

### 2. **Login en Railway**
```bash
# Iniciar sesión
railway login

# Verificar login
railway whoami
```

### 3. **Git Configurado**
```bash
# Verificar estado
git status

# Si hay cambios, commitear
git add .
git commit -m "Deploy Railway"
git push origin master
```

## 🚀 Deploy Automático

### **Opción 1: Script PowerShell (Recomendado para Windows)**
```powershell
# Ejecutar script de deploy
.\railway-deploy.ps1

# Con opciones
.\railway-deploy.ps1 -SkipGit -Environment production
```

### **Opción 2: Script Bash (Linux/Mac)**
```bash
# Hacer ejecutable
chmod +x railway-deploy.sh

# Ejecutar
./railway-deploy.sh
```

### **Opción 3: Deploy Manual**
```bash
# 1. Inicializar proyecto
railway init

# 2. Configurar variables
railway variables set ENVIRONMENT=production
railway variables set LOG_LEVEL=INFO
railway variables set NOTIFICATION_LOG_ENABLED=true

# 3. Deploy
railway up

# 4. Obtener URL
railway domain
```

## 🔧 Configuración

### **Variables de Entorno Requeridas**
```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
NOTIFICATION_LOG_ENABLED=true
API_HOST=0.0.0.0
```

### **Variables Opcionales**
```bash
# Base de datos (Railway proporciona automáticamente)
DATABASE_URL=postgresql://...

# Notificaciones
NOTIFICATION_EMAIL_ENABLED=false
NOTIFICATION_WEBHOOK_ENABLED=false

# Cache
CACHE_TTL=300
```

## 📊 Verificación del Deploy

### **1. Health Check**
```bash
# Verificar salud del servicio
curl https://tu-proyecto.railway.app/health
```

### **2. API Documentation**
```bash
# Ver documentación
open https://tu-proyecto.railway.app/docs
```

### **3. Dashboard**
```bash
# Ver dashboard
open https://tu-proyecto.railway.app/dashboard/overview
```

## 🛠️ Comandos Útiles

### **Monitoreo**
```bash
# Ver logs en tiempo real
railway logs

# Ver logs con filtro
railway logs --filter "ERROR"

# Ver status del servicio
railway status
```

### **Gestión**
```bash
# Abrir servicio en navegador
railway open

# Conectar a base de datos
railway connect

# Ver variables de entorno
railway variables
```

### **Debugging**
```bash
# Ver logs detallados
railway logs --tail

# Reiniciar servicio
railway redeploy

# Ver métricas
railway metrics
```

## 🔍 Troubleshooting

### **Problema: Deploy falla**
```bash
# Verificar logs
railway logs

# Verificar variables
railway variables

# Reiniciar deploy
railway redeploy
```

### **Problema: Servicio no responde**
```bash
# Verificar health check
curl https://tu-proyecto.railway.app/health

# Verificar logs de error
railway logs --filter "ERROR"
```

### **Problema: Base de datos**
```bash
# Conectar a base de datos
railway connect

# Verificar conexión
railway variables | grep DATABASE_URL
```

## 📈 Monitoreo Post-Deploy

### **1. Health Monitoring**
- **Endpoint**: `/health`
- **Frecuencia**: Cada 5 minutos
- **Alertas**: Configurar en Railway dashboard

### **2. Performance Monitoring**
- **Métricas**: CPU, Memoria, Red
- **Logs**: Errores y warnings
- **Uptime**: Disponibilidad del servicio

### **3. Cost Monitoring**
- **Uso de recursos**: CPU y memoria
- **Tráfico**: Requests por minuto
- **Costos**: Monitorear en Railway dashboard

## 🎯 URLs del Servicio

Una vez desplegado, tendrás acceso a:

- **Servicio Principal**: `https://tu-proyecto.railway.app`
- **Health Check**: `https://tu-proyecto.railway.app/health`
- **API Docs**: `https://tu-proyecto.railway.app/docs`
- **Dashboard**: `https://tu-proyecto.railway.app/dashboard/overview`

## 🔄 Actualizaciones

### **Deploy de Cambios**
```bash
# 1. Commitear cambios
git add .
git commit -m "Update: descripción del cambio"
git push origin master

# 2. Deploy automático (Railway detecta cambios)
# O manualmente:
railway up
```

### **Rollback**
```bash
# Ver historial de deploys
railway logs --deployments

# Rollback a versión anterior
railway rollback <deployment-id>
```

## 📚 Recursos Adicionales

- **Railway Docs**: https://docs.railway.app
- **Railway Dashboard**: https://railway.app
- **Soporte**: https://railway.app/support

---

**¡Deploy exitoso! 🎉**

Tu ecosistema Karl AI está ahora ejecutándose en Railway con todas las funcionalidades disponibles.