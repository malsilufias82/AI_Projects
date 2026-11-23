"""Service helpers for BGV completion emails."""

from typing import List, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.services.email_service import render_template, send_custom_email

logger = get_logger(__name__)


BGV_COMPLETION_TEMPLATE = "emails/bgvcompletion.html"


def _normalized_recipients(recipients: Optional[List[str]], primary_email: str) -> List[str]:
	"""Normalize and deduplicate CC recipients, excluding the primary recipient."""
	primary = str(primary_email or "").strip().lower()
	unique = set()
	cleaned = []

	for value in recipients or []:
		email = str(value or "").strip()
		if not email:
			continue
		lowered = email.lower()
		if lowered == primary or lowered in unique:
			continue
		unique.add(lowered)
		cleaned.append(email)

	return cleaned


def send_bgv_completion_email(
	to_email: str,
	recipient_name: str,
	cc: Optional[List[str]] = None,
	company_name: Optional[str] = None,
) -> dict:
	"""Queue a BGV completion email using the bgvcompletion template."""
	to_email = str(to_email or "").strip()
	if not to_email:
		raise ValueError("Recipient email is required for BGV completion email.")

	company = company_name or settings.EMAIL_FROM_NAME
	cc_recipients = _normalized_recipients(cc, to_email)

	html_body = render_template(
		BGV_COMPLETION_TEMPLATE,
		recipient_name=recipient_name,
		company_name=company,
	)

	result = send_custom_email(
		to=[to_email],
		subject=f"BGV Completed - {company}",
		body=html_body,
		cc=cc_recipients or None,
		html=True,
		from_email=settings.EMAIL_FROM,
		from_name=company,
	)

	logger.info(
		"BGV completion email queued",
		to=to_email,
		cc=cc_recipients,
		recipient_name=recipient_name,
	)
	return result
