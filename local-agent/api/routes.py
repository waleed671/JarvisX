from fastapi import APIRouter

from core.executor import Executor
from core.planner import Planner
from core.registry import list_tools
from models import ChatRequest, ExecuteRequest

router = APIRouter()

planner = Planner()
executor = Executor()


@router.post("/chat")
def chat(request: ChatRequest):
    message = request.message.strip()
    actions = planner.plan(message)
    results = []

    for action in actions:
        result = executor.execute(action)
        results.append(result)
        results.extend(_execute_returned_actions(result))

    return {
        "message": message,
        "answer": _answer_from(results),
        "speak": _speak_from(results),
        "sources": _sources_from(results),
        "actions": actions,
        "results": results,
    }


@router.post("/execute")
def execute_command(request: ExecuteRequest):
    return executor.execute(
        {
            "tool": request.tool,
            "parameters": request.parameters,
        }
    )


@router.get("/tools")
def tools():
    return {"tools": list_tools()}


def _answer_from(results):
    for result in results:
        data = result.get("data") or {}
        if data.get("answer"):
            return data["answer"]

    messages = [result.get("message") for result in results if result.get("message")]
    return " ".join(messages)


def _speak_from(results):
    for result in results:
        data = result.get("data") or {}
        if data.get("speak"):
            return data["speak"]

    return _answer_from(results)


def _sources_from(results):
    sources = []
    for result in results:
        data = result.get("data") or {}
        for source in data.get("sources") or []:
            if source not in sources:
                sources.append(source)
    return sources


def _execute_returned_actions(result):
    data = result.get("data") or {}
    actions = data.get("actions") or []
    followup_results = []

    for action in actions:
        if action.get("tool") in {"answer", "n8n_router", "n8n_webhook"}:
            continue
        followup_results.append(executor.execute(action))

    return followup_results
