from pydantic import BaseModel
from typing import Any

class BaseResponse(BaseModel):
    code: int
    message: str
    data: Any | None = None