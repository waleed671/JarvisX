import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_env_file(PROJECT_DIR / ".env")
_load_env_file(BASE_DIR / ".env")


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    chrome_path = os.getenv("JARVIS_CHROME_PATH")
    n8n_router_webhook_url = os.getenv("JARVIS_N8N_ROUTER_WEBHOOK_URL")
    n8n_webhook_url = os.getenv("JARVIS_N8N_WEBHOOK_URL")
    answer_webhook_url = os.getenv("JARVIS_ANSWER_WEBHOOK_URL")
    email_webhook_url = os.getenv("JARVIS_EMAIL_WEBHOOK_URL")
    whatsapp_webhook_url = os.getenv("JARVIS_WHATSAPP_WEBHOOK_URL")
    local_callback_url = os.getenv("JARVIS_LOCAL_CALLBACK_URL", "http://host.docker.internal:8000")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    request_timeout_seconds = int(os.getenv("JARVIS_REQUEST_TIMEOUT_SECONDS", "20"))


settings = Settings()
