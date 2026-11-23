"""
Email service for sending templated emails.

This module provides functions for rendering email templates and sending emails
using the Celery email tasks.
"""

from typing import List, Optional, Dict, Any
from jinja2 import Environment, FileSystemLoader
from app.core.config import settings
from app.core.logging import get_logger
from app.tasks.email_tasks import send_email, send_bulk_emails

logger = get_logger(__name__)

# Initialize Jinja2 environment with template directory
template_env = Environment(
    loader=FileSystemLoader('app/templates'),
    autoescape=True
)


class EmailTemplates:
    """Email template constants."""
    
    ACCOUNT_SETUP = "emails/account_setup.html"
    PASSWORD_RESET = "emails/password_reset.html"
    WEEKLY_STATUS = "emails/weekly_status.html"


def render_template(template_name: str, **context) -> str:
    """
    Render a Jinja2 template with the given context.
    
    Args:
        template_name: Name of the template file
        **context: Template variables
        
    Returns:
        Rendered HTML string
    """
    try:
        template = template_env.get_template(template_name)
        return template.render(**context)
    except Exception as e:
        logger.error(
            "Failed to render email template",
            template_name=template_name,
            error=str(e)
        )
        raise


def send_account_setup_email(
    to: str,
    recipient_name: str,
    setup_url: str,
    company_name: Optional[str] = None,
    cc: Optional[List[str]] = None,
) -> dict:
    """
    Send account setup email to a new user.
    
    Args:
        to: Recipient email address
        recipient_name: Name of the recipient
        setup_url: URL for password setup page (e.g., "https://example.com/set-password?token=xyz")
        company_name: Optional company name (defaults to config)
        cc: Optional CC recipients
        
    Returns:
        Result from email task
    """
    company = company_name or settings.EMAIL_FROM_NAME
    
    # Render HTML template using Jinja2
    html_body = render_template(
        EmailTemplates.ACCOUNT_SETUP,
        recipient_name=recipient_name,
        setup_url=setup_url,
        company_name=company
    )
    
    # Send email
    result = send_email.delay(
        to=[to],
        subject=f"Your Account is Ready - {company}",
        body=html_body,
        cc=cc,
        html=True
    )
    
    logger.info(
        "Account setup email queued",
        to=to,
        recipient_name=recipient_name
    )
    
    return result


def send_password_reset_email(
    to: str,
    recipient_name: str,
    reset_url: str,
    company_name: Optional[str] = None,
    cc: Optional[List[str]] = None,
) -> dict:
    """
    Send password reset email to a user.
    
    Args:
        to: Recipient email address
        recipient_name: Name of the recipient
        reset_url: URL for password reset page (e.g., "https://example.com/reset-password?token=xyz")
        company_name: Optional company name (defaults to config)
        cc: Optional CC recipients
        
    Returns:
        Result from email task
    """
    company = company_name or settings.EMAIL_FROM_NAME
    
    # Render HTML template using Jinja2
    html_body = render_template(
        EmailTemplates.PASSWORD_RESET,
        recipient_name=recipient_name,
        reset_url=reset_url,
        company_name=company
    )
    
    # Send email
    result = send_email.delay(
        to=[to],
        subject=f"Password Reset Request - {company}",
        body=html_body,
        cc=cc,
        html=True
    )
    
    logger.info(
        "Password reset email queued",
        to=to,
        recipient_name=recipient_name
    )
    
    return result


def send_custom_email(
    to: List[str],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    html: bool = False,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
) -> dict:
    """
    Send a custom email with provided content.
    
    Args:
        to: List of recipient email addresses
        subject: Email subject
        body: Email body
        cc: Optional CC recipients
        bcc: Optional BCC recipients
        html: Whether body is HTML
        from_email: Optional sender email
        from_name: Optional sender name
        
    Returns:
        Result from email task
    """
    result = send_email.delay(
        to=to,
        subject=subject,
        body=body,
        cc=cc,
        bcc=bcc,
        html=html,
        from_email=from_email,
        from_name=from_name
    )
    
    logger.info(
        "Custom email queued",
        to=to,
        subject=subject
    )
    
    return result


def send_bulk_account_setup_emails(
    recipients: List[Dict[str, str]],
    setup_url_base: str,
    company_name: Optional[str] = None,
    common_cc: Optional[List[str]] = None,
) -> dict:
    """
    Send account setup emails to multiple recipients.
    
    Each recipient dict should contain:
    - 'email': Recipient email address (required)
    - 'name': Recipient name (required)
    - 'token': Setup token for URL (optional, appended to setup_url_base)
    
    Args:
        recipients: List of dicts with 'email', 'name', and optional 'token'
        setup_url_base: Base URL for password setup (e.g., "https://example.com/set-password")
        company_name: Optional company name (defaults to config)
        common_cc: Optional CC recipients for all emails
        
    Returns:
        Result from bulk email task
    """
    company = company_name or settings.EMAIL_FROM_NAME
    
    # Prepare email configs for bulk send
    email_configs = []
    
    for recipient in recipients:
        email = recipient.get('email')
        name = recipient.get('name')
        token = recipient.get('token')
        
        if not email or not name:
            logger.warning("Skipping recipient with missing email or name", recipient=recipient)
            continue
        
        # Build setup URL with token if provided
        setup_url = setup_url_base
        if token:
            setup_url = f"{setup_url_base}?token={token}"
        
        # Render template for this recipient
        html_body = render_template(
            EmailTemplates.ACCOUNT_SETUP,
            recipient_name=name,
            setup_url=setup_url,
            company_name=company
        )
        
        email_configs.append({
            'to': [email],
            'subject': f"Your Account is Ready - {company}",
            'body': html_body,
            'cc': common_cc
        })
    
    # Log instead of send in dev mode
    if settings.is_development:
        logger.info(
            "Development mode: Bulk account setup emails logged instead of sent",
            total_recipients=len(email_configs),
            recipients=[config['to'][0] for config in email_configs]
        )
        return {
            'status': 'logged',
            'mode': 'development',
            'total': len(email_configs),
            'message': f'{len(email_configs)} emails logged in development mode'
        }
    
    # Send bulk emails
    result = send_bulk_emails.delay(
        email_configs=email_configs,
        html=True,
        from_email=settings.EMAIL_FROM,
        from_name=company
    )
    
    logger.info(
        "Bulk account setup emails queued",
        total_recipients=len(email_configs)
    )
    
    return result
