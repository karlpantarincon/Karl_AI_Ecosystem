# 🤖 DevAgent 24/7 - Configuración para Ejecución Continua

## 📋 Descripción

El DevAgent 24/7 es un servicio diseñado para ejecutar el agente constructor de manera continua en la nube, procesando tareas automáticamente sin intervención manual.

## 🚀 Características

- **Ejecución Continua**: Loop infinito con intervalos configurables
- **Circuit Breaker**: Protección contra fallos consecutivos
- **Auto-restart**: Reinicio automático en caso de fallos
- **Monitoreo**: Health checks y métricas de rendimiento
- **Logging**: Registros detallados de todas las operaciones
- **Configuración Flexible**: Variables de entorno para personalización

## 🛠️ Instalación

### **Opción 1: Servicio del Sistema (Linux/Unix)**

```bash
# 1. Instalar como servicio systemd
sudo ./scripts/install-devagent-service.sh

# 2. Iniciar servicio
sudo systemctl start devagent

# 3. Habilitar inicio automático
sudo systemctl enable devagent

# 4. Verificar estado
sudo systemctl status devagent
```

### **Opción 2: Docker (Recomendado para Cloud)**

```bash
# 1. Ejecutar con docker-compose
docker-compose -f docker-compose.devagent.yml up -d

# 2. Verificar contenedores
docker ps

# 3. Ver logs
docker logs karl-ai-devagent -f
```

### **Opción 3: Ejecución Manual**

```bash
# 1. Ejecutar servicio directamente
python devagent-service.py

# 2. Con configuración personalizada
DEVAGENT_INTERVAL=300 python devagent-service.py
```

## ⚙️ Configuración

### **Variables de Entorno**

```bash
# Configuración básica
ENVIRONMENT=production
COREHUB_URL=http://localhost:8000

# Configuración del DevAgent
DEVAGENT_INTERVAL=300          # Segundos entre tareas (default: 300)
DEVAGENT_MAX_TASKS=100         # Máximo de tareas por hora (default: 100)
DEVAGENT_PRIORITY=1            # Prioridad de tareas 1-5 (default: 1)

# Base de datos
DATABASE_URL=postgresql://user:pass@host:port/db

# Logging
LOG_LEVEL=INFO
```

### **Configuración del Servicio (systemd)**

```ini
[Unit]
Description=Karl AI DevAgent Service
After=network.target

[Service]
Type=simple
User=devagent
WorkingDirectory=/opt/karl-AI-ecosystem
ExecStart=/opt/karl-ai-ecosystem/venv/bin/python devagent-service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 📊 Monitoreo

### **Comandos de Monitoreo**

```bash
# Estado del servicio
sudo systemctl status devagent

# Logs en tiempo real
sudo journalctl -u devagent -f

# Métricas del servicio
./scripts/monitor-devagent.sh metrics

# Estado completo
./scripts/monitor-devagent.sh status

# Monitoreo continuo
./scripts/monitor-devagent.sh monitor
```

### **Health Checks**

```bash
# Verificar API de CoreHub
curl http://localhost:8000/health

# Verificar estado del DevAgent
curl http://localhost:8000/dashboard/agents

# Verificar logs recientes
tail -f /var/log/devagent-service.log
```

### **Métricas Disponibles**

- **Estado del Servicio**: Activo/Inactivo
- **Uptime**: Tiempo de ejecución
- **Memoria**: Uso de memoria en MB
- **CPU**: Porcentaje de uso de CPU
- **Tareas Completadas**: Contador de tareas
- **Errores**: Número de errores recientes
- **Reinicios**: Contador de reinicios automáticos

## 🔧 Gestión del Servicio

### **Comandos Básicos**

```bash
# Iniciar servicio
sudo systemctl start devagent

# Detener servicio
sudo systemctl stop devagent

# Reiniciar servicio
sudo systemctl restart devagent

# Ver estado
sudo systemctl status devagent

# Habilitar inicio automático
sudo systemctl enable devagent

# Deshabilitar inicio automático
sudo systemctl disable devagent
```

### **Comandos Docker**

```bash
# Iniciar contenedor
docker-compose -f docker-compose.devagent.yml up -d

# Detener contenedor
docker-compose -f docker-compose.devagent.yml down

# Ver logs
docker logs karl-ai-devagent -f

# Reiniciar contenedor
docker-compose -f docker-compose.devagent.yml restart devagent
```

## 🚨 Troubleshooting

### **Problemas Comunes**

#### **1. Servicio no inicia**
```bash
# Verificar logs
sudo journalctl -u devagent -n 50

# Verificar configuración
sudo systemctl cat devagent

# Verificar permisos
ls -la /opt/karl-ai-ecosystem/
```

#### **2. DevAgent no procesa tareas**
```bash
# Verificar conexión a CoreHub
curl http://localhost:8000/health

# Verificar base de datos
python -c "from corehub.db.database import engine; print('DB OK')"

# Verificar logs del DevAgent
tail -f /var/log/devagent-service.log
```

#### **3. Alto uso de memoria**
```bash
# Verificar uso de memoria
ps aux | grep devagent

# Reiniciar servicio
sudo systemctl restart devagent

# Ajustar límites en systemd
sudo systemctl edit devagent
```

### **Logs Importantes**

```bash
# Logs del sistema
sudo journalctl -u devagent

# Logs de la aplicación
tail -f /var/log/devagent-service.log

# Logs de Docker
docker logs karl-ai-devagent
```

## 📈 Optimización

### **Configuración de Rendimiento**

```bash
# Para servidores con pocos recursos
DEVAGENT_INTERVAL=600          # 10 minutos
DEVAGENT_MAX_TASKS=50          # Menos tareas por hora

# Para servidores potentes
DEVAGENT_INTERVAL=60           # 1 minuto
DEVAGENT_MAX_TASKS=200         # Más tareas por hora
```

### **Configuración de Recursos**

```ini
# En el archivo de servicio systemd
[Service]
LimitNOFILE=65536
LimitNPROC=4096
MemoryLimit=2G
CPUQuota=200%
```

## 🔄 Actualizaciones

### **Actualizar Servicio**

```bash
# 1. Detener servicio
sudo systemctl stop devagent

# 2. Actualizar código
git pull origin master

# 3. Actualizar dependencias
cd /opt/karl-ai-ecosystem
source venv/bin/activate
pip install -r requirements.txt

# 4. Reiniciar servicio
sudo systemctl start devagent
```

### **Actualizar Docker**

```bash
# 1. Detener contenedor
docker-compose -f docker-compose.devagent.yml down

# 2. Reconstruir imagen
docker-compose -f docker-compose.devagent.yml build

# 3. Iniciar contenedor
docker-compose -f docker-compose.devagent.yml up -d
```

## 📚 Recursos Adicionales

- **Logs**: `/var/log/devagent-service.log`
- **Configuración**: `/etc/systemd/system/devagent.service`
- **Código**: `/opt/karl-ai-ecosystem/`
- **Docker**: `docker-compose.devagent.yml`

## 🆘 Soporte

Para problemas o preguntas:

1. **Verificar logs**: `sudo journalctl -u devagent -f`
2. **Verificar estado**: `./scripts/monitor-devagent.sh status`
3. **Reiniciar servicio**: `sudo systemctl restart devagent`
4. **Contactar soporte**: [GitHub Issues](https://github.com/your-repo/issues)

---

**¡DevAgent 24/7 configurado y funcionando! 🎉**

El agente constructor ahora ejecutará tareas automáticamente de manera continua.
