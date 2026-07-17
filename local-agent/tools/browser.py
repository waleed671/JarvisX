import subprocess
import webbrowser
from pathlib import Path

from config import settings


def open_url(url: str) -> bool:
    chrome_path = settings.chrome_path or _find_chrome()
    if chrome_path:
        subprocess.Popen([chrome_path, url])
        return True

    webbrowser.open(url)
    return True


def _find_chrome() -> str | None:
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return None
