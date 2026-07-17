import re

# Keywords that should be answered by the n8n internet-research router instead
# of the local fallback. Order matters — more-specific patterns first.
_N8N_RESEARCH_PATTERNS = [
    r"\b(bitcoin|btc|ethereum|eth|crypto|cryptocurrency)\b",
    r"\b(stock|share price|nasdaq|nyse|tesla|apple stock|microsoft stock|nvidia|meta stock|amazon stock)\b",
    r"\b(trending|viral)\b.{0,30}\b(song|music|gaana|gana|track)\b",
    r"\b(song|music|gaana|gana)\b.{0,30}\b(trending|viral|popular|top|latest)\b",
    r"\btrending songs\b",
    r"\bpopular songs\b",
    r"\btop songs\b",
    r"\blatest songs\b",
    r"\b(latest|breaking|today.?s?|aaj.?ki?)\b.{0,30}\b(news|khabar|khabrain|headlines)\b",
    r"\bnews\b",
    r"\b(rate|price|cost|value)\b.{0,20}\b(bitcoin|btc|ethereum|eth|dollar|usd|pkr)\b",
    r"\binformation\b.{0,30}\b(about|on|regarding)\b",
    r"\btell me about\b",
    r"\bwikipedia\b",
]


class Planner:
    app_aliases = {
        "chrome": "chrome",
        "google chrome": "chrome",
        "calculator": "calculator",
        "calc": "calculator",
        "notepad": "notepad",
        "paint": "paint",
        "vscode": "vscode",
        "vs code": "vscode",
        "visual studio code": "vscode",
        "word": "word",
        "excel": "excel",
        "powerpoint": "powerpoint",
        "vlc": "vlc",
        "spotify": "spotify",
        "telegram": "telegram",
        "task manager": "taskmgr",
        "file explorer": "explorer",
        "explorer": "explorer",
    }

    def plan(self, text: str):
        message = text.strip()
        lowered = message.lower()
        actions = []

        # --- Local automation tasks (highest priority) ---
        whatsapp_action = self._whatsapp_action(message, lowered)
        if whatsapp_action:
            actions.append(whatsapp_action)

        email_action = self._email_action(message, lowered)
        if email_action:
            actions.append(email_action)

        weather_action = self._weather_action(message, lowered)
        if weather_action:
            actions.append(weather_action)

        url_action = self._open_url_action(message, lowered)
        if url_action:
            actions.append(url_action)

        app_action = self._open_app_action(lowered)
        if app_action and not url_action:
            actions.append(app_action)

        # Explicit "search/google/find" → open browser search
        search_action = self._explicit_search_action(message, lowered)
        if search_action:
            actions.append(search_action)

        # Explicit n8n/workflow trigger keyword
        n8n_action = self._explicit_n8n_action(message, lowered)
        if n8n_action:
            actions.append(n8n_action)

        # --- If no local action matched, route everything else ---
        if not actions:
            # Live-internet query → n8n router
            if self._is_research_query(lowered):
                actions.append(
                    {
                        "tool": "n8n_router",
                        "parameters": {"message": message, "task_type": "research"},
                    }
                )
            else:
                # Math / greetings / local knowledge
                actions.append(
                    {
                        "tool": "answer",
                        "parameters": {"question": message},
                    }
                )

        return actions

    def _open_app_action(self, lowered: str):
        if not self._contains_any(lowered, ["open", "start", "launch", "khol", "kholo", "chalo", "chalao"]):
            return None

        for alias, app in self.app_aliases.items():
            if alias in lowered:
                return {
                    "tool": "open_app",
                    "parameters": {"app": app},
                }

        return None

    def _explicit_search_action(self, message: str, lowered: str):
        """Only match explicit 'search/google/find X' commands — opens browser search."""
        if "weather" in lowered or "mausam" in lowered:
            return None

        patterns = [
            r"(?:search|google|find)\s+(?:for\s+|about\s+)?(.+)",
            r"(.+?)\s+(?:search karo|google karo|dhundo|dhoondo)$",
        ]

        for pattern in patterns:
            match = re.search(pattern, lowered, flags=re.IGNORECASE)
            if not match:
                continue
            query = self._clean_tail(match.group(1))
            if query:
                return {
                    "tool": "web_search",
                    "parameters": {"query": query},
                }

        return None

    def _is_research_query(self, lowered: str) -> bool:
        """Return True if the query should be answered live via n8n internet research."""
        for pattern in _N8N_RESEARCH_PATTERNS:
            if re.search(pattern, lowered, flags=re.IGNORECASE):
                return True
        return False

    def _weather_action(self, message: str, lowered: str):
        if "weather" not in lowered and "mausam" not in lowered:
            return None

        location = self._weather_location(message, lowered)
        return {
            "tool": "weather",
            "parameters": {"location": location},
        }

    def _open_url_action(self, message: str, lowered: str):
        if "open" not in lowered and "khol" not in lowered:
            return None

        match = re.search(r"(https?://\S+|www\.\S+|[a-zA-Z0-9-]+\.[a-zA-Z]{2,}\S*)", message)
        if not match:
            return None

        url = match.group(1).rstrip(".,)")
        if "@" in url:
            return None
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        return {
            "tool": "open_url",
            "parameters": {"url": url},
        }

    def _whatsapp_action(self, message: str, lowered: str):
        if "whatsapp" not in lowered:
            return None

        phone_match = re.search(r"(\+?\d[\d\s\-()]{8,}\d)", message)
        target = phone_match.group(1).strip() if phone_match else self._between_to_and_message(message)
        body = self._after_any(
            message,
            ["message", "msg", "text", "saying", "keh do", "likho", "body"],
        )

        if not body and phone_match:
            body = message[phone_match.end() :].strip(" :-,")
        if not body:
            body = self._after_any(message, ["whatsapp"])

        return {
            "tool": "whatsapp",
            "parameters": {
                "to": target,
                "message": body,
                "send": self._looks_like_send(lowered),
            },
        }

    def _email_action(self, message: str, lowered: str):
        if "email" not in lowered and "mail" not in lowered:
            return None

        email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", message)
        recipient = email_match.group(0) if email_match else ""
        subject = self._section_after(message, "subject", ["body", "message", "msg"])
        body = self._section_after(message, "body", [])

        if not body:
            body = self._section_after(message, "message", [])
        if not body and "about" in lowered:
            body = self._after_any(message, ["about"])

        return {
            "tool": "email",
            "parameters": {
                "to": recipient,
                "subject": subject or "Message from JarvisX",
                "body": body,
                "send": self._looks_like_send(lowered),
            },
        }

    def _explicit_n8n_action(self, message: str, lowered: str):
        """Only trigger when user explicitly mentions n8n/workflow/automation."""
        if not self._contains_any(lowered, ["n8n", "workflow", "automation"]):
            return None

        return {
            "tool": "n8n_webhook",
            "parameters": {
                "task": "workflow",
                "message": message,
                "data": {"raw": message},
            },
        }

    def _n8n_action(self, message: str, lowered: str):
        """Kept for backward compatibility — delegates to explicit check."""
        return self._explicit_n8n_action(message, lowered)

    def _weather_location(self, message: str, lowered: str) -> str:
        cleaned = re.sub(r"[?!.]", " ", message).strip()
        lowered_cleaned = re.sub(r"[?!.]", " ", lowered).strip()

        for marker in [" in ", " for ", " mein ", " main "]:
            index = lowered_cleaned.rfind(marker)
            if index != -1:
                location = cleaned[index + len(marker) :].strip()
                location = self._remove_weather_noise(location)
                if "pakistan" in lowered and "pakistan" not in location.lower():
                    location = f"{location}, Pakistan"
                return location

        location = self._remove_weather_noise(cleaned)
        return location or "Okara, Pakistan"

    def _remove_weather_noise(self, text: str) -> str:
        replacements = [
            "what is",
            "whats",
            "what's",
            "weather",
            "mausam",
            "today",
            "aaj",
            "now",
            "current",
            "ka",
            "ki",
            "kya hai",
        ]
        result = text
        for replacement in replacements:
            result = re.sub(rf"\b{re.escape(replacement)}\b", " ", result, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", result).strip(" ,-:")

    def _between_to_and_message(self, message: str) -> str:
        match = re.search(
            r"(?:to|ko|pe)\s+(.+?)(?:\s+(?:message|msg|text|keh do|likho|body)\b|$)",
            message,
            flags=re.IGNORECASE,
        )
        return match.group(1).strip(" :-,") if match else ""

    def _after_any(self, message: str, keywords: list[str]) -> str:
        for keyword in keywords:
            match = re.search(rf"\b{re.escape(keyword)}\b\s*[:,-]?\s*(.+)$", message, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""

    def _section_after(self, message: str, keyword: str, stop_keywords: list[str]) -> str:
        stop_pattern = "|".join(re.escape(stop) for stop in stop_keywords)
        if stop_pattern:
            pattern = rf"\b{re.escape(keyword)}\b\s*[:,-]?\s*(.+?)(?=\s+\b(?:{stop_pattern})\b|$)"
        else:
            pattern = rf"\b{re.escape(keyword)}\b\s*[:,-]?\s*(.+)$"

        match = re.search(pattern, message, flags=re.IGNORECASE)
        return match.group(1).strip(" :-,") if match else ""

    def _clean_tail(self, text: str) -> str:
        return re.sub(r"\s+(?:in chrome|on google|please|plz)$", "", text, flags=re.IGNORECASE).strip()

    def _looks_like_send(self, lowered: str) -> bool:
        return self._contains_any(lowered, ["send", "bhejo", "kar do", "kr do"])

    def _contains_any(self, text: str, needles: list[str]) -> bool:
        return any(needle in text for needle in needles)
