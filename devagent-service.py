#!/usr/bin/env python3
"""
DevAgent Service - 24/7 Execution Service
Configuración para ejecución continua del DevAgent en la nube
"""

import os
import sys
import time
import signal
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('devagent-service.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('DevAgentService')

class DevAgentService:
    """Servicio para ejecución 24/7 del DevAgent"""
    
    def __init__(self):
        self.running = False
        self.process = None
        self.restart_count = 0
        self.max_restarts = 10
        self.restart_delay = 30  # segundos
        
        # Configuración del DevAgent
        self.devagent_config = {
            'interval': int(os.getenv('DEVAGENT_INTERVAL', '300')),  # 5 minutos por defecto
            'max_tasks': int(os.getenv('DEVAGENT_MAX_TASKS', '100')),
            'priority': int(os.getenv('DEVAGENT_PRIORITY', '1')),
            'environment': os.getenv('ENVIRONMENT', 'production')
        }
        
        # Configuración de monitoreo
        self.health_check_interval = 60  # segundos
        self.last_health_check = None
        
    def setup_signal_handlers(self):
        """Configurar manejadores de señales para shutdown graceful"""
        def signal_handler(signum, frame):
            logger.info(f"Recibida señal {signum}. Iniciando shutdown graceful...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def start_devagent(self):
        """Iniciar proceso del DevAgent"""
        try:
            # Comando para ejecutar DevAgent
            cmd = [
                sys.executable, '-m', 'agents.devagent.app.main', 'loop',
                '--interval', str(self.devagent_config['interval']),
                '--max-tasks', str(self.devagent_config['max_tasks']),
                '--priority', str(self.devagent_config['priority'])
            ]
            
            logger.info(f"Iniciando DevAgent con comando: {' '.join(cmd)}")
            
            # Iniciar proceso
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.last_health_check = time.time()
            logger.info(f"DevAgent iniciado con PID: {self.process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando DevAgent: {e}")
            return False
    
    def stop_devagent(self):
        """Detener proceso del DevAgent"""
        if self.process:
            try:
                logger.info("Deteniendo DevAgent...")
                self.process.terminate()
                
                # Esperar hasta 30 segundos para shutdown graceful
                try:
                    self.process.wait(timeout=30)
                    logger.info("DevAgent detenido gracefulmente")
                except subprocess.TimeoutExpired:
                    logger.warning("DevAgent no respondió, forzando terminación...")
                    self.process.kill()
                    self.process.wait()
                    logger.info("DevAgent terminado forzosamente")
                
                self.process = None
                
            except Exception as e:
                logger.error(f"Error deteniendo DevAgent: {e}")
    
    def is_devagent_healthy(self):
        """Verificar si DevAgent está funcionando correctamente"""
        if not self.process:
            return False
        
        # Verificar si el proceso sigue ejecutándose
        if self.process.poll() is not None:
            logger.warning(f"DevAgent terminó inesperadamente con código: {self.process.returncode}")
            return False
        
        # Verificar si ha pasado mucho tiempo sin actividad
        if self.last_health_check:
            time_since_check = time.time() - self.last_health_check
            if time_since_check > self.health_check_interval * 2:
                logger.warning(f"DevAgent no ha reportado actividad en {time_since_check:.1f} segundos")
                return False
        
        return True
    
    def restart_devagent(self):
        """Reiniciar DevAgent"""
        logger.info("Reiniciando DevAgent...")
        
        # Detener proceso actual
        self.stop_devagent()
        
        # Incrementar contador de reinicios
        self.restart_count += 1
        
        # Verificar límite de reinicios
        if self.restart_count >= self.max_restarts:
            logger.error(f"Límite de reinicios alcanzado ({self.max_restarts}). Deteniendo servicio.")
            self.running = False
            return False
        
        # Esperar antes de reiniciar
        logger.info(f"Esperando {self.restart_delay} segundos antes de reiniciar...")
        time.sleep(self.restart_delay)
        
        # Reiniciar
        if self.start_devagent():
            logger.info("DevAgent reiniciado exitosamente")
            return True
        else:
            logger.error("Error reiniciando DevAgent")
            return False
    
    def monitor_devagent(self):
        """Monitorear estado del DevAgent"""
        if not self.is_devagent_healthy():
            logger.warning("DevAgent no está saludable, reiniciando...")
            if not self.restart_devagent():
                return False
        
        # Actualizar timestamp de health check
        self.last_health_check = time.time()
        return True
    
    def start(self):
        """Iniciar el servicio DevAgent"""
        logger.info("🚀 Iniciando DevAgent Service...")
        logger.info(f"Configuración: {self.devagent_config}")
        
        # Configurar manejadores de señales
        self.setup_signal_handlers()
        
        # Marcar como ejecutándose
        self.running = True
        
        # Iniciar DevAgent
        if not self.start_devagent():
            logger.error("No se pudo iniciar DevAgent")
            return False
        
        logger.info("✅ DevAgent Service iniciado correctamente")
        
        # Loop principal de monitoreo
        try:
            while self.running:
                # Monitorear DevAgent
                if not self.monitor_devagent():
                    logger.error("Error en monitoreo, deteniendo servicio")
                    break
                
                # Esperar antes del siguiente check
                time.sleep(self.health_check_interval)
                
        except KeyboardInterrupt:
            logger.info("Interrumpido por usuario")
        except Exception as e:
            logger.error(f"Error en loop principal: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Detener el servicio DevAgent"""
        logger.info("🛑 Deteniendo DevAgent Service...")
        self.running = False
        self.stop_devagent()
        logger.info("✅ DevAgent Service detenido")
    
    def get_status(self):
        """Obtener estado del servicio"""
        return {
            'running': self.running,
            'devagent_pid': self.process.pid if self.process else None,
            'restart_count': self.restart_count,
            'last_health_check': self.last_health_check,
            'config': self.devagent_config
        }

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DevAgent Service - 24/7 Execution')
    parser.add_argument('--status', action='store_true', help='Mostrar estado del servicio')
    parser.add_argument('--config', action='store_true', help='Mostrar configuración')
    
    args = parser.parse_args()
    
    service = DevAgentService()
    
    if args.status:
        status = service.get_status()
        print(f"Estado del servicio: {status}")
        return
    
    if args.config:
        print(f"Configuración: {service.devagent_config}")
        return
    
    # Iniciar servicio
    service.start()

if __name__ == "__main__":
    main()
