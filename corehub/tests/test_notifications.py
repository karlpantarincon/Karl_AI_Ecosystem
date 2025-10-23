"""
Tests for the notification service.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

from corehub.services.notifications import NotificationService, create_notification_service


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for notification service tests."""
    with patch.dict(os.environ, {
        "NOTIFICATION_EMAIL_ENABLED": "true",
        "NOTIFICATION_EMAIL_SENDER": "test@example.com",
        "NOTIFICATION_EMAIL_RECIPIENT": "admin@example.com",
        "NOTIFICATION_EMAIL_SMTP_SERVER": "smtp.test.com",
        "NOTIFICATION_EMAIL_SMTP_PORT": "587",
        "NOTIFICATION_EMAIL_SMTP_USER": "testuser",
        "NOTIFICATION_EMAIL_SMTP_PASSWORD": "testpassword",
        "NOTIFICATION_WEBHOOK_ENABLED": "true",
        "NOTIFICATION_WEBHOOK_URL": "http://mock-webhook.com",
        "NOTIFICATION_LOG_ENABLED": "true",
    }):
        yield


class TestNotificationService:
    """Tests for the NotificationService."""
    
    def test_init(self, mock_env_vars):
        """Test initialization of NotificationService."""
        service = NotificationService()
        assert service.email_enabled is True
        assert service.email_sender == "test@example.com"
        assert service.webhook_enabled is True
        assert service.webhook_url == "http://mock-webhook.com"
        assert service.log_enabled is True
    
    def test_send_notification_email_disabled(self):
        """Test sending email when disabled."""
        with patch.dict(os.environ, {"NOTIFICATION_EMAIL_ENABLED": "false"}):
            service = NotificationService()
            assert not service._send_email("Subject", "Message")
    
    def test_send_notification_webhook_disabled(self):
        """Test sending webhook when disabled."""
        with patch.dict(os.environ, {"NOTIFICATION_WEBHOOK_ENABLED": "false"}):
            service = NotificationService()
            assert not service._send_webhook({"key": "value"})
    
    def test_send_notification_log_enabled(self):
        """Test sending log when enabled."""
        with patch("loguru.logger.info") as mock_logger_info:
            service = NotificationService()
            assert service._send_log("Test log message")
            mock_logger_info.assert_called_with("NOTIFICATION (INFO): Test log message")
    
    def test_send_notification_unknown_type(self):
        """Test sending notification with unknown type."""
        with patch("loguru.logger.info") as mock_logger_info:
            service = NotificationService()
            service.log_enabled = True  # Ensure log is enabled for this test
            service.email_enabled = False
            service.webhook_enabled = False
            assert service.send_notification("unknown", "Test message")
            mock_logger_info.assert_called_with("NOTIFICATION (INFO): [UNKNOWN] Test message")
    
    def test_send_notification_exception(self):
        """Test exception handling in send_notification."""
        with patch.dict(os.environ, {"NOTIFICATION_EMAIL_ENABLED": "false", "NOTIFICATION_WEBHOOK_ENABLED": "false", "NOTIFICATION_LOG_ENABLED": "true"}):
            service = NotificationService()
            result = service.send_notification("test", "Test message", "Test Subject", {"data": "test"})
            assert result is True  # Because log notification still works
    
    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp, mock_env_vars):
        """Test successful email sending."""
        service = NotificationService()
        mock_instance = mock_smtp.return_value.__enter__.return_value
        assert service._send_email("Test Subject", "Test Message")
        mock_instance.starttls.assert_called_once()
        mock_instance.login.assert_called_with("testuser", "testpassword")
        mock_instance.send_message.assert_called_once()
    
    def test_send_email_missing_config(self):
        """Test email sending with missing configuration."""
        with patch.dict(os.environ, {"NOTIFICATION_EMAIL_SENDER": ""}):
            service = NotificationService()
            assert not service._send_email("Subject", "Message")
    
    @patch("requests.post")
    def test_send_webhook_success(self, mock_post, mock_env_vars):
        """Test successful webhook sending."""
        service = NotificationService()
        mock_post.return_value.raise_for_status.return_value = None
        assert service._send_webhook({"text": "Test Webhook"})
        mock_post.assert_called_with("http://mock-webhook.com", json={"text": "Test Webhook"}, timeout=5)
    
    def test_send_webhook_missing_url(self):
        """Test webhook sending with missing URL."""
        with patch.dict(os.environ, {"NOTIFICATION_WEBHOOK_URL": ""}):
            service = NotificationService()
            assert not service._send_webhook({"text": "Test Webhook"})
    
    def test_send_task_notification(self, mock_env_vars):
        """Test send_task_notification method."""
        service = NotificationService()
        result = service.send_task_notification("T-001", "Test Task", "in_progress", "Some details")
        assert result is True  # Should succeed with log notifications
    
    def test_send_system_notification(self, mock_env_vars):
        """Test send_system_notification method."""
        service = NotificationService()
        result = service.send_system_notification("health_alert", "DB connection lost", "ERROR")
        assert result is True  # Should succeed with log notifications
    
    def test_format_email_message(self, mock_env_vars):
        """Test format_email_message method."""
        service = NotificationService()
        payload = {"key": "value"}
        message = service.format_email_message("test", "Test message", payload)
        assert "Type: TEST" in message
        assert "Message: Test message" in message
        assert "Details:" in message
        assert "key" in message
    
    def test_is_notification_enabled(self, mock_env_vars):
        """Test is_notification_enabled method."""
        service = NotificationService()
        assert service.is_notification_enabled() is True
        
        service.email_enabled = False
        service.webhook_enabled = False
        service.log_enabled = False
        assert service.is_notification_enabled() is False


def test_create_notification_service():
    """Test the factory function for creating notification service."""
    service1 = create_notification_service()
    service2 = create_notification_service()
    assert service1 is service2  # Should be singleton