from config import settings
from tools.base import Tool
from tools.http_client import post_json


class N8NRouterTool(Tool):
    name = "n8n_router"
    description = "Ask n8n to research online or route a task"

    def execute(self, parameters):
        message = parameters.get("message") or parameters.get("question") or ""
        message = message.strip()
        if not message:
            return {
                "success": False,
                "message": "Message is required for n8n router.",
            }

        response = ask_n8n_router(message, parameters)
        answer = extract_answer(response["body"])
        sources = extract_sources(response["body"])
        actions = extract_actions(response["body"])

        if not response["ok"]:
            return {
                "success": False,
                "message": (
                    "n8n router is not reachable. Import and activate the JarvisX Router workflow, "
                    "then set JARVIS_N8N_ROUTER_WEBHOOK_URL."
                ),
                "data": {
                    "answer": "n8n router is not reachable yet.",
                    "response": response,
                    "source": "n8n_router",
                },
            }

        return {
            "success": True,
            "message": answer or "n8n router responded.",
            "data": {
                "answer": answer,
                "speak": extract_speak(response["body"]) or answer,
                "sources": sources,
                "actions": actions,
                "response": response,
                "source": "n8n_router",
            },
        }


def ask_n8n_router(message: str, parameters: dict | None = None) -> dict:
    url = router_url()
    if not url:
        return {
            "ok": False,
            "status": None,
            "body": "JARVIS_N8N_ROUTER_WEBHOOK_URL is not configured.",
        }

    payload = {
        "source": "jarvisx",
        "message": message,
        "mode": (parameters or {}).get("mode", "voice"),
        "task_type": (parameters or {}).get("task_type", "auto"),
        "local_callback_url": settings.local_callback_url,
        "capabilities": [
            "latest_news",
            "trending_music",
            "stocks",
            "crypto",
            "bitcoin_rate",
            "internet_research",
            "email",
            "whatsapp",
            "local_actions",
        ],
    }
    return post_json(url, payload)


def router_url() -> str | None:
    return settings.n8n_router_webhook_url or settings.n8n_webhook_url


def extract_answer(body):
    if isinstance(body, dict):
        for key in ("answer", "text", "message", "output", "result"):
            if body.get(key):
                return str(body[key])
    if isinstance(body, str):
        return body
    return None


def extract_speak(body):
    if isinstance(body, dict):
        for key in ("speak", "voice", "spoken"):
            if body.get(key):
                return str(body[key])
    return None


def extract_sources(body):
    if not isinstance(body, dict):
        return []

    sources = body.get("sources") or body.get("citations") or []
    if not isinstance(sources, list):
        return []

    clean_sources = []
    for source in sources:
        if isinstance(source, str):
            clean_sources.append({"title": source, "url": source})
        elif isinstance(source, dict):
            title = source.get("title") or source.get("name") or source.get("url")
            url = source.get("url") or source.get("link")
            if title or url:
                clean_sources.append({"title": title or url, "url": url or title})
    return clean_sources


def extract_actions(body):
    if not isinstance(body, dict):
        return []

    actions = body.get("actions") or body.get("local_actions") or []
    if not isinstance(actions, list):
        return []

    clean_actions = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        tool = action.get("tool")
        parameters = action.get("parameters") or {}
        if isinstance(tool, str) and isinstance(parameters, dict):
            clean_actions.append({"tool": tool, "parameters": parameters})
    return clean_actions
