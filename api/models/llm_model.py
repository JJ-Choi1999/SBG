import json
from pydantic import BaseModel

class Chat(BaseModel):
    id: int
    chat: str
    is_search: bool

class Feedback(BaseModel):
    id: int
    chat_id: int
    feedback_code: int