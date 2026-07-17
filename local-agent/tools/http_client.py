import json
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config import settings


def post_json(url: str, payload: dict, headers: dict | None = None) -> dict:
    request_headers = {"Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)

    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=request_headers,
        method="POST",
    )

    try:
        with urlopen(request, timeout=settings.request_timeout_seconds) as response:
            body = response.read().decode("utf-8")
            return {
                "ok": 200 <= response.status < 300,
                "status": response.status,
                "body": _parse_body(body),
            }
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        return {
            "ok": False,
            "status": exc.code,
            "body": _parse_body(body),
        }
    except URLError as exc:
        return {
            "ok": False,
            "status": None,
            "body": str(exc.reason),
        }


def get_json(url: str, params: dict | None = None, headers: dict | None = None) -> dict:
    request_headers = {"Accept": "application/json"}
    if headers:
        request_headers.update(headers)

    request_url = url
    if params:
        request_url = f"{url}?{urlencode(params)}"

    request = Request(request_url, headers=request_headers, method="GET")

    try:
        with urlopen(request, timeout=settings.request_timeout_seconds) as response:
            body = response.read().decode("utf-8")
            return {
                "ok": 200 <= response.status < 300,
                "status": response.status,
                "body": _parse_body(body),
            }
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        return {
            "ok": False,
            "status": exc.code,
            "body": _parse_body(body),
        }
    except URLError as exc:
        return {
            "ok": False,
            "status": None,
            "body": str(exc.reason),
        }


def _parse_body(body: str):
    if not body:
        return None

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body
