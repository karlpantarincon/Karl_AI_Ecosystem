"""
Sistema de Alertas Avanzadas para Karl AI Ecosystem
"""

import asyncio
import smtplib
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import requests
try:
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
except ImportError:
    # Fallback para versiones de Python
    from email.MIMEText import MIMEText
    from email.MIMEMultipart import MIMEMultipart

from loguru import logger


class AlertSeverity(Enum):
    """Niveles de severidad de alertas"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(Enum):
    """Estados de alertas"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class Alert:
    """Estructura de una alerta"""
    id: str
    type: str
    severity: AlertSeverity
    status: AlertStatus
    title: str
    message: str
    timestamp: str
    source: str
    metadata: Dict[str, Any]
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[str] = None
    resolved_at: Optional[str] = None


@dataclass
class AlertRule:
    """Regla de alerta"""
    id: str
    name: str
    condition: str
    severity: AlertSeverity
    enabled: bool
    cooldown_minutes: int
    notification_channels: List[str]
    metadata: Dict[str, Any]


class NotificationChannel:
    """Canal de notificación base"""
    
    async def send(self, alert: Alert) -> bool:
        """Enviar notificación"""
        raise NotImplementedError


class EmailNotificationChannel(NotificationChannel):
    """Canal de notificación por email"""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, 
                 from_email: str, to_emails: List[str]):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails
    
    async def send(self, alert: Alert) -> bool:
        """Enviar alerta por email"""
        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
            
            # Contenido del email
            body = f"""
            <h2>🚨 Alerta del Sistema Karl AI</h2>
            
            <p><strong>Severidad:</strong> {alert.severity.value.upper()}</p>
            <p><strong>Origen:</strong> {alert.source}</p>
            <p><strong>Timestamp:</strong> {alert.timestamp}</p>
            
            <h3>Descripción:</h3>
            <p>{alert.message}</p>
            
            <h3>Metadatos:</h3>
            <pre>{json.dumps(alert.metadata, indent=2)}</pre>
            
            <hr>
            <p><em>Esta alerta fue generada automáticamente por el sistema Karl AI Ecosystem.</em></p>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email alert sent for {alert.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
            return False


class WebhookNotificationChannel(NotificationChannel):
    """Canal de notificación por webhook"""
    
    def __init__(self, webhook_url: str, headers: Optional[Dict[str, str]] = None):
        self.webhook_url = webhook_url
        self.headers = headers or {"Content-Type": "application/json"}
    
    async def send(self, alert: Alert) -> bool:
        """Enviar alerta por webhook"""
        try:
            payload = {
                "alert": asdict(alert),
                "timestamp": datetime.utcnow().isoformat(),
                "source": "karl-ai-ecosystem"
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Webhook alert sent for {alert.id}")
                return True
            else:
                logger.error(f"Webhook failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending webhook alert: {e}")
            return False


class SlackNotificationChannel(NotificationChannel):
    """Canal de notificación para Slack"""
    
    def __init__(self, webhook_url: str, channel: Optional[str] = None):
        self.webhook_url = webhook_url
        self.channel = channel
    
    async def send(self, alert: Alert) -> bool:
        """Enviar alerta a Slack"""
        try:
            # Colores según severidad
            color_map = {
                AlertSeverity.INFO: "#36a64f",
                AlertSeverity.WARNING: "#ff9500",
                AlertSeverity.CRITICAL: "#ff0000",
                AlertSeverity.EMERGENCY: "#8b0000"
            }
            
            # Emojis según severidad
            emoji_map = {
                AlertSeverity.INFO: "ℹ️",
                AlertSeverity.WARNING: "⚠️",
                AlertSeverity.CRITICAL: "🚨",
                AlertSeverity.EMERGENCY: "🔥"
            }
            
            payload = {
                "channel": self.channel,
                "username": "Karl AI Monitor",
                "icon_emoji": ":robot_face:",
                "attachments": [{
                    "color": color_map.get(alert.severity, "#36a64f"),
                    "title": f"{emoji_map.get(alert.severity, 'ℹ️')} {alert.title}",
                    "text": alert.message,
                    "fields": [
                        {"title": "Severidad", "value": alert.severity.value.upper(), "short": True},
                        {"title": "Origen", "value": alert.source, "short": True},
                        {"title": "Timestamp", "value": alert.timestamp, "short": False}
                    ],
                    "footer": "Karl AI Ecosystem",
                    "ts": int(datetime.utcnow().timestamp())
                }]
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Slack alert sent for {alert.id}")
                return True
            else:
                logger.error(f"Slack webhook failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")
            return False


class AlertManager:
    """Gestor de alertas del sistema"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.notification_channels: Dict[str, NotificationChannel] = {}
        self.alert_history: List[Alert] = []
        self.cooldowns: Dict[str, datetime] = {}
        
        # Configurar canales por defecto
        self._setup_default_channels()
    
    def _setup_default_channels(self):
        """Configurar canales de notificación por defecto"""
        # Email (si está configurado)
        if self._is_email_configured():
            email_channel = EmailNotificationChannel(
                smtp_server=os.getenv('SMTP_SERVER', ''),
                smtp_port=int(os.getenv('SMTP_PORT', '587')),
                username=os.getenv('SMTP_USERNAME', ''),
                password=os.getenv('SMTP_PASSWORD', ''),
                from_email=os.getenv('SMTP_FROM_EMAIL', ''),
                to_emails=os.getenv('SMTP_TO_EMAILS', '').split(',')
            )
            self.notification_channels['email'] = email_channel
        
        # Webhook (si está configurado)
        webhook_url = os.getenv('WEBHOOK_URL')
        if webhook_url:
            webhook_channel = WebhookNotificationChannel(webhook_url)
            self.notification_channels['webhook'] = webhook_channel
        
        # Slack (si está configurado)
        slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        if slack_webhook:
            slack_channel = SlackNotificationChannel(
                webhook_url=slack_webhook,
                channel=os.getenv('SLACK_CHANNEL')
            )
            self.notification_channels['slack'] = slack_channel
    
    def _is_email_configured(self) -> bool:
        """Verificar si email está configurado"""
        return all([
            os.getenv('SMTP_SERVER'),
            os.getenv('SMTP_USERNAME'),
            os.getenv('SMTP_PASSWORD'),
            os.getenv('SMTP_FROM_EMAIL'),
            os.getenv('SMTP_TO_EMAILS')
        ])
    
    async def create_alert(self, alert_type: str, severity: AlertSeverity, 
                          title: str, message: str, source: str, 
                          metadata: Dict[str, Any] = None) -> Alert:
        """Crear una nueva alerta"""
        alert_id = f"{alert_type}_{int(datetime.utcnow().timestamp())}"
        
        alert = Alert(
            id=alert_id,
            type=alert_type,
            severity=severity,
            status=AlertStatus.ACTIVE,
            title=title,
            message=message,
            timestamp=datetime.utcnow().isoformat(),
            source=source,
            metadata=metadata or {}
        )
        
        # Verificar cooldown
        if self._is_in_cooldown(alert_type):
            logger.info(f"Alert {alert_type} is in cooldown, skipping")
            return alert
        
        # Agregar a la lista de alertas
        self.alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Enviar notificaciones
        await self._send_notifications(alert)
        
        # Configurar cooldown
        self._set_cooldown(alert_type)
        
        logger.info(f"Alert created: {alert_id} - {title}")
        return alert
    
    def _is_in_cooldown(self, alert_type: str) -> bool:
        """Verificar si una alerta está en cooldown"""
        if alert_type not in self.cooldowns:
            return False
        
        cooldown_time = self.cooldowns[alert_type]
        return datetime.utcnow() < cooldown_time
    
    def _set_cooldown(self, alert_type: str):
        """Configurar cooldown para un tipo de alerta"""
        # Obtener regla de alerta
        rule = self.alert_rules.get(alert_type)
        if rule:
            cooldown_minutes = rule.cooldown_minutes
        else:
            cooldown_minutes = 5  # Default 5 minutes
        
        self.cooldowns[alert_type] = datetime.utcnow() + timedelta(minutes=cooldown_minutes)
    
    async def _send_notifications(self, alert: Alert):
        """Enviar notificaciones para una alerta"""
        # Obtener canales de notificación
        rule = self.alert_rules.get(alert.type)
        if rule:
            channels = rule.notification_channels
        else:
            channels = list(self.notification_channels.keys())
        
        # Enviar a cada canal
        for channel_name in channels:
            if channel_name in self.notification_channels:
                channel = self.notification_channels[channel_name]
                try:
                    success = await channel.send(alert)
                    if success:
                        logger.info(f"Notification sent via {channel_name}")
                    else:
                        logger.warning(f"Failed to send notification via {channel_name}")
                except Exception as e:
                    logger.error(f"Error sending notification via {channel_name}: {e}")
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Reconocer una alerta"""
        if alert_id not in self.alerts:
            return False
        
        alert = self.alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_by = acknowledged_by
        alert.acknowledged_at = datetime.utcnow().isoformat()
        
        logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
        return True
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolver una alerta"""
        if alert_id not in self.alerts:
            return False
        
        alert = self.alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow().isoformat()
        
        logger.info(f"Alert {alert_id} resolved")
        return True
    
    def add_alert_rule(self, rule: AlertRule):
        """Agregar regla de alerta"""
        self.alert_rules[rule.id] = rule
        logger.info(f"Alert rule added: {rule.id}")
    
    def add_notification_channel(self, name: str, channel: NotificationChannel):
        """Agregar canal de notificación"""
        self.notification_channels[name] = channel
        logger.info(f"Notification channel added: {name}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Obtener alertas activas"""
        return [alert for alert in self.alerts.values() 
                if alert.status == AlertStatus.ACTIVE]
    
    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Obtener alertas por severidad"""
        return [alert for alert in self.alerts.values() 
                if alert.severity == severity]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Obtener resumen de alertas"""
        total_alerts = len(self.alerts)
        active_alerts = len(self.get_active_alerts())
        
        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len(self.get_alerts_by_severity(severity))
        
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'severity_counts': severity_counts,
            'timestamp': datetime.utcnow().isoformat()
        }


# Instancia global del gestor de alertas
alert_manager = AlertManager()
