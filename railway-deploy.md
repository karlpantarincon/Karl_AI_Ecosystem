# 🚀 Deploy en Railway - Guía paso a paso

## 📋 **Pasos para deploy:**

### **1. 🌐 Ir a Railway:**
1. **Ve a** [railway.app](https://railway.app)
2. **Inicia sesión** con GitHub
3. **Haz clic en "New Project"**

### **2. 🔗 Conectar repositorio:**
- **Selecciona** "Deploy from GitHub repo"
- **Repositorio**: `karlpantarincon/Karl_AI_Ecosystem`
- **Branch**: `master`

### **3. ⚙️ Configuración del servicio:**

#### **Build Settings:**
- **Build Command**: `docker build -t karl-ai-ecosystem .`
- **Start Command**: `uvicorn corehub.api.main:app --host 0.0.0.0 --port $PORT`

#### **Variables de entorno:**
```
ENVIRONMENT=production
DATABASE_URL=postgresql://karl_ai_db_user:ezn3WjgVE1O7VE8OArBo81hjGRcyriKZ@dpg-d3tcmtf5r7bs73en3ed0-a/karl_ai_db
CORS_ORIGINS=https://karl-ai-dashboard.railway.app
PORT=8000
```

### **4. 🚀 Deploy:**
- **Haz clic en "Deploy"**
- **Espera** a que se construya (5-10 minutos)
- **Verifica** que esté funcionando

### **5. 🔍 Verificación:**
- **URL del servicio**: `https://[service-name].railway.app`
- **Health check**: `https://[service-name].railway.app/health`
- **API docs**: `https://[service-name].railway.app/docs`

## 🎯 **URLs esperadas:**
- **CoreHub API**: `https://karl-ai-corehub.railway.app`
- **Health Check**: `https://karl-ai-corehub.railway.app/health`
- **Dashboard API**: `https://karl-ai-corehub.railway.app/dashboard/overview`

## 🔧 **Troubleshooting:**
- **Build failed**: Verificar Dockerfile
- **Start failed**: Verificar variables de entorno
- **Database error**: Verificar DATABASE_URL
- **Port error**: Verificar que use $PORT

## 📊 **Monitoreo:**
- **Logs**: Disponibles en Railway dashboard
- **Métricas**: CPU, memoria, red
- **Deployments**: Historial de deploys
