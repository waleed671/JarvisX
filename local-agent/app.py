from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from tools.answer import AnswerTool
from tools.email_tool import EmailTool
from tools.n8n import N8NWebhookTool
from tools.n8n_router import N8NRouterTool
from tools.open_app import OpenAppTool
from tools.open_url import OpenUrlTool
from tools.weather import WeatherTool
from tools.web_search import WebSearchTool
from tools.whatsapp import WhatsAppTool

from core.registry import register
from config import PROJECT_DIR

for tool in [
    AnswerTool(),
    EmailTool(),
    N8NWebhookTool(),
    N8NRouterTool(),
    OpenAppTool(),
    OpenUrlTool(),
    WeatherTool(),
    WebSearchTool(),
    WhatsAppTool(),
]:
    register(tool)

app = FastAPI(
    title="JarvisX Local Agent",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "agent": "JarvisX",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/ui")
def ui():
    return FileResponse(PROJECT_DIR / "frontend" / "index.html")
