from urllib.parse import quote_plus

from config import settings
from tools.base import Tool
from tools.browser import open_url
from tools.http_client import post_json


class EmailTool(Tool):
    name = "email"
    description = "Send or draft an email"

    def execute(self, parameters):
        to = parameters.get("to", "").strip()
        subject = parameters.get("subject", "").strip()
        body = parameters.get("body", "").strip()

        if not to:
            return {
                "success": False,
                "message": "Email recipient address is required.",
            }

        # Auto-send via n8n if webhook is configured
        if settings.email_webhook_url:
            response = post_json(
                settings.email_webhook_url,
                {
                    "to": to,
                    "subject": subject or "Message from JarvisX",
                    "body": body,
                    "source": "jarvisx",
                },
            )
            return {
                "success": response["ok"],
                "message": "Email sent via n8n." if response["ok"] else "Email n8n task failed.",
                "data": {
                    "sent_via": "n8n",
                    "to": to,
                    **response,
                },
            }

        # Fallback: open Gmail compose draft
        url = (
            "https://mail.google.com/mail/?view=cm&fs=1"
            f"&to={quote_plus(to)}"
            f"&su={quote_plus(subject or 'Message from JarvisX')}"
            f"&body={quote_plus(body)}"
        )
        open_url(url)
        return {
            "success": True,
            "message": "Email draft opened in Gmail. Press Send manually, or set JARVIS_EMAIL_WEBHOOK_URL for auto-send.",
            "data": {
                "sent_via": "browser_draft",
                "url": url,
                "note": "Set JARVIS_EMAIL_WEBHOOK_URL in .env to enable auto-send via n8n.",
            },
        }
