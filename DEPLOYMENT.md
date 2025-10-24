# 🚀 Karl AI Ecosystem - Guía de Deployment

## 🐳 **Deployment con Docker**

### **1. Instalar Docker Desktop:**
1. **Descargar**: [Docker Desktop para Windows](https://www.docker.com/products/docker-desktop/)
2. **Instalar** y reiniciar el sistema
3. **Verificar instalación**:
   ```bash
   docker --version
   docker-compose --version
   ```

### **2. Construir y ejecutar:**
```bash
# Construir imagen
docker build -t karl-ai-ecosystem .

# Ejecutar con docker-compose
docker-compose up --build

# O ejecutar individualmente
docker run -p 8000:8000 -e DATABASE_URL="postgresql://karl_ai_db_user:ezn3WjgVE1O7VE8OArBo81hjGRcyriKZ@dpg-d3tcmtf5r7bs73en3ed0-a/karl_ai_db" karl-ai-ecosystem
```

### **3. Verificar deployment:**
- **CoreHub API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

## 🔧 **Deployment con MCP**

### **1. Instalar MCP:**
```bash
pip install mcp
```

### **2. Ejecutar servidor MCP:**
```bash
python mcp-server.py
```

### **3. Configurar cliente MCP:**
```json
{
  "mcpServers": {
    "karl-ai-ecosystem": {
      "command": "python",
      "args": ["mcp-server.py"],
      "env": {
        "ENVIRONMENT": "production"
      }
    }
  }
}
```

## ☁️ **Deployment en Cloud**

### **Railway (con Docker):**
1. **Conectar repositorio** a Railway
2. **Configurar build command**: `docker build -t karl-ai-ecosystem .`
3. **Configurar start command**: `docker run -p $PORT:8000 karl-ai-ecosystem`
4. **Variables de entorno**:
   - `DATABASE_URL`: `postgresql://karl_ai_db_user:ezn3WjgVE1O7VE8OArBo81hjGRcyriKZ@dpg-d3tcmtf5r7bs73en3ed0-a/karl_ai_db`
   - `ENVIRONMENT`: `production`

### **Heroku (con Docker):**
1. **Crear Procfile**:
   ```
   web: docker run -p $PORT:8000 karl-ai-ecosystem
   ```
2. **Deploy**:
   ```bash
   git push heroku main
   ```

## 🔍 **Verificación del Sistema**

### **Endpoints de verificación:**
- `GET /health` - Estado del sistema
- `GET /dashboard/overview` - Métricas del dashboard
- `GET /docs` - Documentación API

### **Logs del sistema:**
```bash
# Docker logs
docker logs karl-ai-ecosystem

# MCP logs
python mcp-server.py --verbose
```

## 🛠️ **Troubleshooting**

### **Problemas comunes:**
1. **Docker no encontrado**: Instalar Docker Desktop
2. **Puerto ocupado**: Cambiar puerto en docker-compose.yml
3. **Base de datos**: Verificar DATABASE_URL
4. **Dependencias**: Verificar requirements.txt

### **Comandos de diagnóstico:**
```bash
# Verificar contenedores
docker ps

# Ver logs
docker logs <container_id>

# Entrar al contenedor
docker exec -it <container_id> /bin/bash
```
