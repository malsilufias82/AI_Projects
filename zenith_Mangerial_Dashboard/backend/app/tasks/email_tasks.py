"""
Celery tasks for email sending.

This module provides background tasks for sending emails with support for
local mode (logging instead of sending) and flexible recipient handling.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.email_tasks.send_email",
    max_retries=3,
    default_retry_delay=60,
)
def send_email(
    self,
    to: List[str],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    html: bool = False,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
    reply_to: Optional[str] = None,
) -> dict:
    """
    Send an email task with support for local mode.
    
    In local/development mode, emails are logged instead of actually sent.
    
    Args:
        to: List of recipient email addresses
        subject: Email subject line
        body: Email body content (text or HTML based on html parameter)
        cc: Optional list of CC recipients
        bcc: Optional list of BCC recipients
        html: Whether the body is HTML (True) or plain text (False)
        from_email: Optional sender email address (defaults to config)
        from_name: Optional sender name (defaults to config)
        reply_to: Optional reply-to email address
        
    Returns:
        Dictionary with send result and details
    """
    logger.info(
        "Email send task started",
        task_id=self.request.id,
        to=to,
        subject=subject,
        cc=cc,
        bcc=bcc,
        html=html
    )
    
    # Handle local mode - log instead of send
    if settings.is_development and not settings.EMAIL_ENABLED:
        logger.info(
            "Local mode: Email logged instead of sent",
            task_id=self.request.id,
            to=to,
            subject=subject,
            cc=cc,
            bcc=bcc,
            body=body,
            html=html
        )
        return {
            'status': 'logged',
            'mode': 'local',
            'to': to,
            'subject': subject,
            'message': 'Email logged in local mode (not sent)'
        }
    
    try:
        # Use config defaults if not provided
        sender_email = from_email or settings.EMAIL_FROM
        sender_name = from_name or settings.EMAIL_FROM_NAME
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{sender_name} <{sender_email}>"
        msg['To'] = ', '.join(to)
        
        if cc:
            msg['Cc'] = ', '.join(cc)
        
        if reply_to:
            msg['Reply-To'] = reply_to
        
        # Add body
        if html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        # Connect to SMTP server and send
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            if settings.EMAIL_USE_TLS:
                server.starttls()
            
            if settings.EMAIL_USERNAME and settings.EMAIL_PASSWORD:
                server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            
            # Combine all recipients
            all_recipients = to.copy()
            if cc:
                all_recipients.extend(cc)
            if bcc:
                all_recipients.extend(bcc)
            
            server.send_message(msg, sender_email, all_recipients)
        
        logger.info(
            "Email sent successfully",
            task_id=self.request.id,
            to=to,
            subject=subject
        )
        
        return {
            'status': 'sent',
            'to': to,
            'subject': subject,
            'message': 'Email sent successfully'
        }
        
    except Exception as e:
        logger.error(
            "Email send failed",
            task_id=self.request.id,
            to=to,
            subject=subject,
            error=str(e)
        )
        raise self.retry(exc=e)


@celery_app.task(
    bind=True,
    name="app.tasks.email_tasks.send_bulk_emails",
    max_retries=3,
    default_retry_delay=60,
)
def send_bulk_emails(
    self,
    email_configs: List[dict],
    common_subject: Optional[str] = None,
    common_body: Optional[str] = None,
    common_cc: Optional[List[str]] = None,
    common_bcc: Optional[List[str]] = None,
    html: bool = False,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
) -> dict:
    """
    Send bulk emails with common content but individual recipients.
    
    Each config in email_configs can override common settings.
    
    Args:
        email_configs: List of dicts with 'to' (required) and optional 'subject', 'body', 'cc', 'bcc'
        common_subject: Default subject for all emails
        common_body: Default body for all emails
        common_cc: Default CC for all emails
        common_bcc: Default BCC for all emails
        html: Whether bodies are HTML (True) or plain text (False)
        from_email: Optional sender email address (defaults to config)
        from_name: Optional sender name (defaults to config)
        
    Returns:
        Dictionary with bulk send results
    """
    logger.info(
        "Bulk email send task started",
        task_id=self.request.id,
        total_emails=len(email_configs)
    )
    
    results = []
    sent_count = 0
    failed_count = 0
    logged_count = 0
    
    for config in email_configs:
        to = config.get('to', [])
        if not to:
            logger.warning("Skipping email config with no recipients", config=config)
            continue
        
        # Merge config with common settings
        subject = config.get('subject', common_subject)
        body = config.get('body', common_body)
        cc = config.get('cc', common_cc)
        bcc = config.get('bcc', common_bcc)
        
        if not subject or not body:
            logger.warning("Skipping email config with missing subject or body", config=config)
            continue
        
        try:
            result = send_email(
                to=to,
                subject=subject,
                body=body,
                cc=cc,
                bcc=bcc,
                html=html,
                from_email=from_email,
                from_name=from_name
            )
            
            results.append({
                'to': to,
                'subject': subject,
                'status': result.get('status')
            })
            
            if result.get('status') == 'sent':
                sent_count += 1
            elif result.get('status') == 'logged':
                logged_count += 1
                
        except Exception as e:
            failed_count += 1
            results.append({
                'to': to,
                'subject': subject,
                'status': 'failed',
                'error': str(e)
            })
            logger.error(
                "Failed to send email in bulk",
                to=to,
                subject=subject,
                error=str(e)
            )
    
    logger.info(
        "Bulk email send completed",
        task_id=self.request.id,
        total=len(results),
        sent=sent_count,
        logged=logged_count,
        failed=failed_count
    )
    
    return {
        'total': len(results),
        'sent': sent_count,
        'logged': logged_count,
        'failed': failed_count,
        'results': results
    }
