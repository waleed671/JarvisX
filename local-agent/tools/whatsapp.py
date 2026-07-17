import re
from urllib.parse import quote_plus

from config import settings
from tools.base import Tool
from tools.browser import open_url
from tools.http_client import post_json


class WhatsAppTool(Tool):
    name = "whatsapp"
    description = "Send or draft a WhatsApp message"

    def execute(self, parameters):
        target = parameters.get("to", "").strip()
        message = parameters.get("message", "").strip()
        send = bool(parameters.get("send", False))

        if not target or not message:
            return {
                "success": False,
                "message": "WhatsApp target (phone number) and message text are required.",
            }

        # Auto-send via n8n if webhook is configured
        if settings.whatsapp_webhook_url:
            response = post_json(
                settings.whatsapp_webhook_url,
                {"to": target, "message": message, "source": "jarvisx"},
            )
            return {
                "success": response["ok"],
                "message": "WhatsApp message sent via n8n." if response["ok"] else "WhatsApp n8n task failed.",
                "data": {
                    "sent_via": "n8n",
                    "to": target,
                    **response,
                },
            }

        # Fallback: open WhatsApp Web draft
        phone = _normalize_phone(target)
        if not phone:
            return {
                "success": False,
                "message": "A phone number like 923001234567 is needed for WhatsApp Web.",
            }

        url = f"https://web.whatsapp.com/send?phone={phone}&text={quote_plus(message)}"
        open_url(url)
        return {
            "success": True,
            "message": "WhatsApp draft opened in browser. Press Send manually, or set JARVIS_WHATSAPP_WEBHOOK_URL for auto-send.",
            "data": {
                "sent_via": "browser_draft",
                "url": url,
                "note": "Set JARVIS_WHATSAPP_WEBHOOK_URL in .env to enable auto-send via n8n.",
            },
        }


def _normalize_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) < 10:
        return ""
    return digits
