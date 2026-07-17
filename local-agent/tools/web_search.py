from urllib.parse import quote_plus

from tools.base import Tool
from tools.browser import open_url


class WebSearchTool(Tool):
    name = "web_search"
    description = "Search the web in Chrome"

    def execute(self, parameters):
        query = parameters.get("query", "").strip()
        if not query:
            return {
                "success": False,
                "message": "Search query is required.",
            }

        url = f"https://www.google.com/search?q={quote_plus(query)}"
        open_url(url)
        return {
            "success": True,
            "message": f"Searched for: {query}",
            "data": {"query": query, "url": url},
        }
