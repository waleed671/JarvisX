import ast
import operator

from config import settings
from tools.base import Tool
from tools.http_client import post_json
from tools.n8n_router import ask_n8n_router, extract_answer, extract_sources, extract_speak, router_url


class AnswerTool(Tool):
    name = "answer"
    description = "Answer a question using configured AI or local fallbacks"

    def execute(self, parameters):
        question = parameters.get("question", "").strip()
        if not question:
            return {
                "success": False,
                "message": "Question is required.",
            }

        local_answer = _answer_locally(question)
        if local_answer:
            return {
                "success": True,
                "message": local_answer,
                "data": {"answer": local_answer, "source": "local"},
            }

        if settings.answer_webhook_url:
            response = post_json(settings.answer_webhook_url, {"question": question, "source": "jarvisx"})
            answer = _extract_answer(response["body"])
            return {
                "success": response["ok"],
                "message": answer or "Answer webhook responded.",
                "data": {"answer": answer, "response": response, "source": "n8n"},
            }

        if router_url():
            response = ask_n8n_router(question, {"task_type": "answer", "mode": parameters.get("mode", "voice")})
            answer = extract_answer(response["body"])
            if not response["ok"]:
                answer = (
                    "n8n router workflow is not active yet. Import and activate "
                    "n8n/jarvis-router.workflow.json in n8n."
                )
            return {
                "success": response["ok"],
                "message": answer or "n8n router did not return an answer.",
                "data": {
                    "answer": answer,
                    "speak": extract_speak(response["body"]) or answer,
                    "sources": extract_sources(response["body"]),
                    "response": response,
                    "source": "n8n_router",
                },
            }

        if settings.openai_api_key:
            response = post_json(
                "https://api.openai.com/v1/chat/completions",
                {
                    "model": settings.openai_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are JarvisX, a concise helpful desktop assistant.",
                        },
                        {"role": "user", "content": question},
                    ],
                    "temperature": 0.2,
                },
                {"Authorization": f"Bearer {settings.openai_api_key}"},
            )
            answer = _extract_openai_answer(response["body"])
            return {
                "success": response["ok"],
                "message": answer or "OpenAI request completed.",
                "data": {"answer": answer, "response": response, "source": "openai"},
            }

        answer = (
            "I can perform local tasks now. For live internet answers, import the n8n "
            "JarvisX Router workflow and set JARVIS_N8N_ROUTER_WEBHOOK_URL."
        )
        return {
            "success": True,
            "message": answer,
            "data": {"answer": answer, "source": "fallback"},
        }


def _answer_locally(question: str) -> str | None:
    lowered = question.lower().strip()

    if lowered in {"hi", "hello", "hey", "salam", "assalamualaikum"}:
        return "Hi, I am JarvisX. Ask me a question or give me a task."

    if "what can you do" in lowered or "help" == lowered:
        return (
            "I can open apps, search the web, draft WhatsApp messages, draft emails, "
            "and trigger n8n webhooks."
        )

    math_answer = _try_math(lowered)
    if math_answer is not None:
        return math_answer

    return None


def _try_math(text: str) -> str | None:
    allowed_words = {"calculate", "calc", "what is", "solve"}
    expression = text
    for word in allowed_words:
        expression = expression.replace(word, "")
    expression = expression.strip().replace("x", "*")

    if not expression or any(char not in "0123456789+-*/(). % " for char in expression):
        return None

    try:
        result = _eval_math(ast.parse(expression, mode="eval").body)
    except Exception:
        return None

    return str(result)


def _eval_math(node):
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in operators:
        return operators[type(node.op)](_eval_math(node.left), _eval_math(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in operators:
        return operators[type(node.op)](_eval_math(node.operand))

    raise ValueError("Unsupported expression")


def _extract_answer(body):
    if isinstance(body, dict):
        for key in ("answer", "text", "message", "output"):
            if body.get(key):
                return str(body[key])
    if isinstance(body, str):
        return body
    return None


def _extract_openai_answer(body):
    if not isinstance(body, dict):
        return None

    choices = body.get("choices") or []
    if not choices:
        return None

    message = choices[0].get("message") or {}
    return message.get("content")
