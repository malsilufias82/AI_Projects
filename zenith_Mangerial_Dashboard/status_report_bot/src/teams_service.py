"""
teams_service.py
-----------------
Handles all communication with Microsoft Teams via the Microsoft
Graph API: posting channel messages (with @mentions), and creating
online meetings for the 5 PM escalation.

Auth: client-credentials flow (MSAL) using TENANT_ID / CLIENT_ID /
CLIENT_SECRET from .env. The Azure AD App Registration needs
(application) permissions such as ChannelMessage.Send, OnlineMeetings.ReadWrite.All,
and User.Read.All, granted with admin consent.

NOTE ON "AUTOMATED CALLS": Graph can create/start an online meeting
and add the manager, PM and TL as required attendees, and the bot can
post the meeting join link in the channel/chat. Graph cannot make the
meeting "speak" to the TL or hold a conversation — a human still needs
to join and deliver the message, or you rely on the chat message/tag
to prompt them. This module exposes create_escalation_meeting() to
support that workflow.
"""

from typing import Dict, List, Optional

import requests
from msal import ConfidentialClientApplication

from config import AppConfig
from logger import get_logger


GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


class TeamsService:
    """Thin wrapper around the Microsoft Graph API for Teams operations."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__, config.logs_folder, config.log_level)
        self._app = ConfidentialClientApplication(
            client_id=config.client_id,
            client_credential=config.client_secret,
            authority=f"https://login.microsoftonline.com/{config.tenant_id}",
        )
        self._token: Optional[str] = None

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------
    def _get_token(self) -> str:
        if self._token:
            return self._token

        result = self._app.acquire_token_for_client(scopes=[self.config.graph_scope])
        if "access_token" not in result:
            error_desc = result.get("error_description", "Unknown auth error")
            self.logger.error(f"Failed to acquire Graph API token: {error_desc}")
            raise RuntimeError(f"Graph auth failed: {error_desc}")

        self._token = result["access_token"]
        return self._token

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # Channel messaging
    # ------------------------------------------------------------------
    def send_channel_message(self, html_body: str, mentions: Optional[List[Dict]] = None) -> None:
        """
        Post a message to the configured Teams channel.

        Args:
            html_body: HTML-formatted message body. Use <at id="N">Name</at>
                       placeholders matching entries in `mentions`.
            mentions: List of Graph 'mentions' payload dicts, e.g.
                [{"id": 0, "mentionText": "Rahul", "mentioned": {"user": {"id": "...", "userIdentityType": "aadUser"}}}]
        """
        cfg = self.config
        url = f"{GRAPH_BASE_URL}/teams/{cfg.team_id}/channels/{cfg.channel_id}/messages"

        body = {"body": {"contentType": "html", "content": html_body}}
        if mentions:
            body["mentions"] = mentions

        try:
            resp = requests.post(url, headers=self._headers(), json=body, timeout=30)
            resp.raise_for_status()
            self.logger.info("Teams channel message sent successfully.")
        except requests.RequestException as exc:
            self.logger.error(f"Failed to send Teams channel message: {exc}")
            raise

    @staticmethod
    def build_mention(index: int, display_name: str, user_aad_id: str) -> Dict:
        """Helper to build a single Graph @mention entry."""
        return {
            "id": index,
            "mentionText": display_name,
            "mentioned": {"user": {"id": user_aad_id, "userIdentityType": "aadUser"}},
        }

    @staticmethod
    def mention_tag(index: int, display_name: str) -> str:
        """Inline <at> HTML tag matching a build_mention() entry."""
        return f'<at id="{index}">{display_name}</at>'

    # ------------------------------------------------------------------
    # Escalation meetings (5 PM / 6 PM)
    # ------------------------------------------------------------------
    def create_escalation_meeting(
        self,
        organizer_user_id: str,
        subject: str,
        attendee_emails: List[str],
        duration_minutes: int = 15,
    ) -> Optional[str]:
        """
        Create a Teams online meeting to escalate a pending TL, with
        the requester/manager/PM/TL as attendees, starting immediately.

        Args:
            organizer_user_id: AAD object ID of the meeting organizer
                (typically the service/automation account, or the requester).
            subject: Meeting subject line.
            attendee_emails: Emails of required attendees (requester, PM, TL...).
            duration_minutes: Meeting length.

        Returns:
            The join URL of the created meeting, or None on failure.
        """
        from datetime import datetime, timedelta

        start = datetime.utcnow()
        end = start + timedelta(minutes=duration_minutes)

        url = f"{GRAPH_BASE_URL}/users/{organizer_user_id}/onlineMeetings"
        body = {
            "subject": subject,
            "startDateTime": start.isoformat() + "Z",
            "endDateTime": end.isoformat() + "Z",
            "participants": {
                "attendees": [
                    {"upn": email, "role": "presenter"} for email in attendee_emails
                ]
            },
        }

        try:
            resp = requests.post(url, headers=self._headers(), json=body, timeout=30)
            resp.raise_for_status()
            join_url = resp.json().get("joinWebUrl")
            self.logger.info(f"Escalation meeting created: '{subject}' -> {join_url}")
            return join_url
        except requests.RequestException as exc:
            self.logger.error(f"Failed to create escalation meeting '{subject}': {exc}")
            return None
