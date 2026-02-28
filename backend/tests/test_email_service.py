"""
Tests for email notification service
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app.services.email_service import EmailService


class TestEmailService:
    """Tests for EmailService"""
    
    def test_email_service_initialization(self):
        """Test email service initializes with default config"""
        service = EmailService()
        
        assert service.from_email == "noreply@oscp.dev"
        assert service.enabled is False  # Disabled by default in tests
    
    @patch('app.services.email_service.smtplib.SMTP')
    def test_send_email_disabled(self, mock_smtp):
        """Test sending email when disabled (logs only)"""
        service = EmailService()
        service.enabled = False
        
        result = service.send_email(
            to_email="test@example.com",
            subject="Test Subject",
            body_text="Test body"
        )
        
        assert result is True
        mock_smtp.assert_not_called()
    
    @patch('app.services.email_service.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test successfully sending email"""
        service = EmailService()
        service.enabled = True
        
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = service.send_email(
            to_email="test@example.com",
            subject="Test Subject",
            body_text="Test body",
            body_html="<p>Test body</p>"
        )
        
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.send_message.assert_called_once()
    
    @patch('app.services.email_service.smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp):
        """Test handling email send failure"""
        service = EmailService()
        service.enabled = True
        
        # Mock SMTP failure
        mock_smtp.side_effect = Exception("SMTP connection failed")
        
        result = service.send_email(
            to_email="test@example.com",
            subject="Test Subject",
            body_text="Test body"
        )
        
        assert result is False
    
    def test_send_claim_expiration_reminder(self):
        """Test sending claim expiration reminder"""
        service = EmailService()
        service.enabled = False  # Disabled for testing
        
        expires_at = datetime.utcnow() + timedelta(hours=12)
        
        result = service.send_claim_expiration_reminder(
            user_email="user@example.com",
            user_name="Test User",
            issue_title="Fix bug in authentication",
            issue_url="https://github.com/test/repo/issues/1",
            expires_at=expires_at,
            hours_remaining=12
        )
        
        assert result is True
    
    def test_send_claim_released_notification(self):
        """Test sending claim released notification"""
        service = EmailService()
        service.enabled = False
        
        result = service.send_claim_released_notification(
            user_email="user@example.com",
            user_name="Test User",
            issue_title="Fix bug in authentication",
            issue_url="https://github.com/test/repo/issues/1"
        )
        
        assert result is True
    
    def test_send_pr_merged_notification(self):
        """Test sending PR merged notification"""
        service = EmailService()
        service.enabled = False
        
        result = service.send_pr_merged_notification(
            user_email="user@example.com",
            user_name="Test User",
            issue_title="Fix bug in authentication",
            pr_url="https://github.com/test/repo/pull/123"
        )
        
        assert result is True
    
    @patch.object(EmailService, 'send_email')
    def test_send_bulk_emails(self, mock_send_email):
        """Test sending bulk emails"""
        service = EmailService()
        
        # Mock send_email to return True
        mock_send_email.return_value = True
        
        recipients = [
            ("user1@example.com", {"name": "User 1", "count": 5}),
            ("user2@example.com", {"name": "User 2", "count": 3}),
            ("user3@example.com", {"name": "User 3", "count": 7})
        ]
        
        subject_template = "Hello {name}"
        body_template = "You have {count} notifications"
        
        result = service.send_bulk_emails(recipients, subject_template, body_template)
        
        assert result["sent"] == 3
        assert result["failed"] == 0
        assert len(result["errors"]) == 0
        assert mock_send_email.call_count == 3
    
    @patch.object(EmailService, 'send_email')
    def test_send_bulk_emails_with_failures(self, mock_send_email):
        """Test sending bulk emails with some failures"""
        service = EmailService()
        
        # Mock send_email to fail for second recipient
        mock_send_email.side_effect = [True, False, True]
        
        recipients = [
            ("user1@example.com", {"name": "User 1"}),
            ("user2@example.com", {"name": "User 2"}),
            ("user3@example.com", {"name": "User 3"})
        ]
        
        result = service.send_bulk_emails(
            recipients,
            "Hello {name}",
            "Test message"
        )
        
        assert result["sent"] == 2
        assert result["failed"] == 1


class TestEmailServiceIntegration:
    """Integration tests for email service"""
    
    def test_email_content_formatting(self):
        """Test that email content is properly formatted"""
        service = EmailService()
        service.enabled = False
        
        # Test with special characters and formatting
        result = service.send_claim_expiration_reminder(
            user_email="test@example.com",
            user_name="Test User <script>alert('xss')</script>",
            issue_title="Fix bug & improve performance",
            issue_url="https://github.com/test/repo/issues/1?param=value",
            expires_at=datetime.utcnow() + timedelta(hours=24),
            hours_remaining=24
        )
        
        # Should handle special characters without errors
        assert result is True
    
    def test_email_with_missing_html(self):
        """Test sending email with only text body"""
        service = EmailService()
        service.enabled = False
        
        result = service.send_email(
            to_email="test@example.com",
            subject="Test",
            body_text="Plain text only",
            body_html=None
        )
        
        assert result is True
