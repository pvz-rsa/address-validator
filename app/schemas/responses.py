from pydantic import BaseModel
from typing import Any, Dict


class ErrorResponse(BaseModel):
    error: str
    detail: str


class SuccessResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any] = {}