"""
Notification service for CoreHub.

This module provides a unified notification system that supports:
- Email notifications
- Webhook notifications  
- Log notifications
"""

import os
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional

import requests
from loguru import logger


class NotificationService:
    """
    Service for sending various types of notifications.
    Supports email, webhook, and logging.
    """
    
    def __init__(self):
        self.email_enabled = os.getenv("NOTIFICATION_EMAIL_ENABLED", "false").lower() == "true"
        self.email_sender = os.getenv("NOTIFICATION_EMAIL_SENDER")
        self.email_recipient = os.getenv("NOTIFICATION_EMAIL_RECIPIENT")
        self.smtp_server = os.getenv("NOTIFICATION_EMAIL_SMTP_SERVER")
        self.smtp_port = int(os.getenv("NOTIFICATION_EMAIL_SMTP_PORT", "587"))
        self.smtp_user = os.getenv("NOTIFICATION_EMAIL_SMTP_USER")
        self.smtp_password = os.getenv("NOTIFICATION_EMAIL_SMTP_PASSWORD")
        
        self.webhook_enabled = os.getenv("NOTIFICATION_WEBHOOK_ENABLED", "false").lower() == "true"
        self.webhook_url = os.getenv("NOTIFICATION_WEBHOOK_URL")
        
        self.log_enabled = os.getenv("NOTIFICATION_LOG_ENABLED", "true").lower() == "true"
    
    def _send_email(self, subject: str, message: str) -> bool:
        """Sends an email notification."""
        if not self.email_enabled:
            return False
            
        if not all([self.email_sender, self.email_recipient, self.smtp_server, self.smtp_user, self.smtp_password]):
            logger.warning("Email notification is enabled but configuration is incomplete.")
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_sender
            msg['To'] = self.email_recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            logger.info(f"Email notification sent to {self.email_recipient} with subject: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    def _send_webhook(self, payload: dict) -> bool:
        """Sends a webhook notification."""
        if not self.webhook_enabled:
            return False
            
        if not self.webhook_url:
            logger.warning("Webhook notification is enabled but URL is not configured.")
            return False
            
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=5)
            response.raise_for_status()
            logger.info(f"Webhook notification sent to {self.webhook_url}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False
    
    def _send_log(self, message: str, level: str = "INFO") -> bool:
        """Logs a notification."""
        if not self.log_enabled:
            return False
        
        log_message = f"NOTIFICATION ({level}): {message}"
        if level == "INFO":
            logger.info(log_message)
        elif level == "WARNING":
            logger.warning(log_message)
        elif level == "ERROR":
            logger.error(log_message)
        else:
            logger.debug(log_message)
        return True
    
    def send_notification(self, type: str, message: str, subject: Optional[str] = None, payload: Optional[dict] = None, level: str = "INFO") -> bool:
        """
        Sends a notification through configured channels.
        
        Args:
            type (str): Type of notification (e.g., "task", "system").
            message (str): The main message content.
            subject (str, optional): Subject for email notifications. Defaults to None.
            payload (dict, optional): Additional data for webhook notifications. Defaults to None.
            level (str): Log level for log notifications. Defaults to "INFO".
        
        Returns:
            bool: True if at least one notification was sent successfully, False otherwise.
        """
        sent_any = False
        
        # Log notification
        if self.log_enabled:
            self._send_log(f"[{type.upper()}] {message}", level)
            sent_any = True
        
        # Email notification
        if self.email_enabled and subject:
            email_body = self.format_email_message(type, message, payload)
            if self._send_email(subject, email_body):
                sent_any = True
        
        # Webhook notification
        if self.webhook_enabled and payload:
            webhook_payload = {
                "type": type,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                **payload
            }
            if self._send_webhook(webhook_payload):
                sent_any = True
        
        if not sent_any:
            logger.warning(f"No notification channels enabled or configured for type: {type}")
        
        return sent_any
    
    def send_task_notification(self, task_id: str, title: str, status: str, details: Optional[str] = None) -> bool:
        """Sends a notification for a task update."""
        subject = f"Task Update: {task_id} - {status.upper()}"
        message = f"Task {task_id}: {title}\nStatus: {status.upper()}"
        if details:
            message += f"\nDetails: {details}"
        
        payload = {
            "task_id": task_id,
            "title": title,
            "status": status,
            "details": details,
        }
        return self.send_notification("task", message, subject, payload)
    
    def send_system_notification(self, event_type: str, description: str, severity: str = "INFO") -> bool:
        """Sends a notification for a system event."""
        subject = f"System Alert: {event_type.upper()}"
        message = f"System Event: {event_type}\nDescription: {description}"
        
        payload = {
            "event_type": event_type,
            "description": description,
            "severity": severity,
        }
        return self.send_notification("system", message, subject, payload, severity)
    
    def format_email_message(self, type: str, message: str, payload: Optional[dict] = None) -> str:
        """Formats the email message body."""
        formatted_message = f"Type: {type.upper()}\n"
        formatted_message += f"Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        formatted_message += f"Message: {message}\n"
        if payload:
            formatted_message += f"Details:\n{json.dumps(payload, indent=2)}\n"
        return formatted_message
    
    def is_notification_enabled(self) -> bool:
        """Checks if any notification channel is enabled."""
        return self.email_enabled or self.webhook_enabled or self.log_enabled


# Global notification service instance
_notification_service: Optional[NotificationService] = None


def create_notification_service() -> NotificationService:
    """Factory function to create a singleton NotificationService instance."""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service