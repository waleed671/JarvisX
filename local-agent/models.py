from pydantic import BaseModel
from typing import Dict, Any


class ChatRequest(BaseModel):
    message: str


class ExecuteRequest(BaseModel):
    tool: str
    parameters: Dict[str, Any]


class ExecuteResponse(BaseModel):
    success: bool
    message: str
