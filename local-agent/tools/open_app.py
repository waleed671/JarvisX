import subprocess
from pathlib import Path

from config import settings
from tools.base import Tool


class OpenAppTool(Tool):

    name = "open_app"

    description = "Open installed desktop applications"

    # Map canonical app name → command list
    apps = {
        "calculator": ["calc"],
        "notepad": ["notepad"],
        "paint": ["mspaint"],
        "vscode": ["code"],
        "chrome": ["chrome"],          # handled specially by _command_for
        "word": ["winword"],
        "excel": ["excel"],
        "powerpoint": ["powerpnt"],
        "vlc": ["vlc"],
        "spotify": ["spotify"],
        "telegram": ["telegram"],
        "taskmgr": ["taskmgr"],
        "explorer": ["explorer"],
    }

    def execute(self, parameters):
        app = parameters.get("app", "").lower()

        if app not in self.apps:
            return {
                "success": False,
                "message": f"'{app}' is not in my supported apps list. Try: {', '.join(self.apps)}",
            }

        try:
            command = self._command_for(app)
            subprocess.Popen(command, shell=False)
            return {
                "success": True,
                "message": f"{app} opened successfully.",
                "data": {"app": app},
            }
        except FileNotFoundError:
            return {
                "success": False,
                "message": f"Could not find '{app}'. Make sure it is installed.",
            }
        except Exception as exc:
            return {
                "success": False,
                "message": str(exc),
            }

    def _command_for(self, app: str) -> list:
        if app == "chrome":
            chrome_path = settings.chrome_path or self._find_chrome()
            if chrome_path:
                return [chrome_path]

        return self.apps[app]

    def _find_chrome(self) -> str | None:
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        for candidate in candidates:
            if Path(candidate).exists():
                return candidate
        return None
