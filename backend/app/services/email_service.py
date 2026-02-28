"""
Email notification service for sending user notifications

Handles email notifications for claim expirations, PR updates, and other events.
"""
import logging
from typing import Optional, List
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending email notifications to users.
    
    In production, this should be configured with a proper SMTP server
    or email service provider (SendGrid, AWS SES, etc.).
    """
    
    def __init__(self):
        """Initialize email service with configuration"""
        self.smtp_host = getattr(settings, 'SMTP_HOST', 'localhost')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_user = getattr(settings, 'SMTP_USER', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@oscp.dev')
        self.enabled = getattr(settings, 'EMAIL_ENABLED', False)
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None
    ) -> bool:
        """
        Send an email to a recipient.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body_text: Plain text email body
            body_html: Optional HTML email body
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info(f"Email disabled. Would send to {to_email}: {subject}")
            return True
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Attach text and HTML parts
            part1 = MIMEText(body_text, 'plain')
            msg.attach(part1)
            
            if body_html:
                part2 = MIMEText(body_html, 'html')
                msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_claim_expiration_reminder(
        self,
        user_email: str,
        user_name: str,
        issue_title: str,
        issue_url: str,
        expires_at: datetime,
        hours_remaining: int
    ) -> bool:
        """
        Send a reminder email about an expiring claim.
        
        Args:
            user_email: User's email address
            user_name: User's name
            issue_title: Title of the issue
            issue_url: URL to the issue
            expires_at: When the claim expires
            hours_remaining: Hours until expiration
            
        Returns:
            True if email sent successfully
        """
        subject = f"Reminder: Your claimed issue expires in {hours_remaining} hours"
        
        body_text = f"""
Hi {user_name},

This is a reminder that your claimed issue is expiring soon:

Issue: {issue_title}
Expires at: {expires_at.strftime('%Y-%m-%d %H:%M UTC')}
Time remaining: {hours_remaining} hours

If you need more time, you can request an extension from your dashboard.
Otherwise, the issue will be automatically released and made available to other contributors.

View issue: {issue_url}

Best regards,
Open Source Contribution Platform Team
"""
        
        body_html = f"""
<html>
<body>
    <h2>Claim Expiration Reminder</h2>
    <p>Hi {user_name},</p>
    <p>This is a reminder that your claimed issue is expiring soon:</p>
    <ul>
        <li><strong>Issue:</strong> {issue_title}</li>
        <li><strong>Expires at:</strong> {expires_at.strftime('%Y-%m-%d %H:%M UTC')}</li>
        <li><strong>Time remaining:</strong> {hours_remaining} hours</li>
    </ul>
    <p>If you need more time, you can request an extension from your dashboard.</p>
    <p>Otherwise, the issue will be automatically released and made available to other contributors.</p>
    <p><a href="{issue_url}">View Issue</a></p>
    <p>Best regards,<br>Open Source Contribution Platform Team</p>
</body>
</html>
"""
        
        return self.send_email(user_email, subject, body_text, body_html)
    
    def send_claim_released_notification(
        self,
        user_email: str,
        user_name: str,
        issue_title: str,
        issue_url: str
    ) -> bool:
        """
        Send notification that a claim was automatically released.
        
        Args:
            user_email: User's email address
            user_name: User's name
            issue_title: Title of the issue
            issue_url: URL to the issue
            
        Returns:
            True if email sent successfully
        """
        subject = "Your claimed issue has been released"
        
        body_text = f"""
Hi {user_name},

Your claimed issue has been automatically released due to expiration:

Issue: {issue_title}

The issue is now available for other contributors to claim.
You can claim it again if you'd like to continue working on it.

View issue: {issue_url}

Best regards,
Open Source Contribution Platform Team
"""
        
        body_html = f"""
<html>
<body>
    <h2>Claim Released</h2>
    <p>Hi {user_name},</p>
    <p>Your claimed issue has been automatically released due to expiration:</p>
    <p><strong>Issue:</strong> {issue_title}</p>
    <p>The issue is now available for other contributors to claim.</p>
    <p>You can claim it again if you'd like to continue working on it.</p>
    <p><a href="{issue_url}">View Issue</a></p>
    <p>Best regards,<br>Open Source Contribution Platform Team</p>
</body>
</html>
"""
        
        return self.send_email(user_email, subject, body_text, body_html)
    
    def send_pr_merged_notification(
        self,
        user_email: str,
        user_name: str,
        issue_title: str,
        pr_url: str
    ) -> bool:
        """
        Send notification that a PR was merged.
        
        Args:
            user_email: User's email address
            user_name: User's name
            issue_title: Title of the issue
            pr_url: URL to the pull request
            
        Returns:
            True if email sent successfully
        """
        subject = "Congratulations! Your pull request was merged"
        
        body_text = f"""
Hi {user_name},

Congratulations! Your pull request has been merged:

Issue: {issue_title}

Your contribution has been accepted and is now part of the project.
Great work on completing this contribution!

View PR: {pr_url}

Best regards,
Open Source Contribution Platform Team
"""
        
        body_html = f"""
<html>
<body>
    <h2>Pull Request Merged! 🎉</h2>
    <p>Hi {user_name},</p>
    <p>Congratulations! Your pull request has been merged:</p>
    <p><strong>Issue:</strong> {issue_title}</p>
    <p>Your contribution has been accepted and is now part of the project.</p>
    <p>Great work on completing this contribution!</p>
    <p><a href="{pr_url}">View Pull Request</a></p>
    <p>Best regards,<br>Open Source Contribution Platform Team</p>
</body>
</html>
"""
        
        return self.send_email(user_email, subject, body_text, body_html)
    
    def send_bulk_emails(
        self,
        recipients: List[tuple],
        subject_template: str,
        body_template: str
    ) -> dict:
        """
        Send bulk emails to multiple recipients.
        
        Args:
            recipients: List of (email, context_dict) tuples
            subject_template: Subject template with {placeholders}
            body_template: Body template with {placeholders}
            
        Returns:
            Dictionary with success/failure counts
        """
        results = {
            "sent": 0,
            "failed": 0,
            "errors": []
        }
        
        for email, context in recipients:
            try:
                subject = subject_template.format(**context)
                body = body_template.format(**context)
                
                if self.send_email(email, subject, body):
                    results["sent"] += 1
                else:
                    results["failed"] += 1
                    
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"{email}: {str(e)}")
        
        return results
