from config import settings
from tools.base import Tool
from tools.http_client import post_json


class N8NWebhookTool(Tool):
    name = "n8n_webhook"
    description = "Send a task payload to an n8n webhook"

    def execute(self, parameters):
        url = parameters.get("url") or settings.n8n_webhook_url
        if not url:
            return {
                "success": False,
                "message": "Set JARVIS_N8N_WEBHOOK_URL or pass a webhook URL.",
            }

        payload = {
            "source": "jarvisx",
            "task": parameters.get("task", ""),
            "message": parameters.get("message", ""),
            "data": parameters.get("data", {}),
        }
        response = post_json(url, payload)

        return {
            "success": response["ok"],
            "message": "n8n webhook triggered." if response["ok"] else "n8n webhook failed.",
            "data": response,
        }
