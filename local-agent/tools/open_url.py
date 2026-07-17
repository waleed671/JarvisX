from tools.base import Tool
from tools.browser import open_url


class OpenUrlTool(Tool):
    name = "open_url"
    description = "Open a URL in Chrome or the default browser"

    def execute(self, parameters):
        url = parameters.get("url", "").strip()
        if not url:
            return {
                "success": False,
                "message": "URL is required.",
            }

        open_url(url)
        return {
            "success": True,
            "message": f"Opened {url}",
            "data": {"url": url},
        }
