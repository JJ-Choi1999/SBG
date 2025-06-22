from fastapi import APIRouter
from api.models.llm_model import Chat, Feedback
from common.logger.logging import Logger

logger = Logger.get_instance(__file__)
router = APIRouter(prefix="/format_result", tags=["format_result 对话管理"])

@router.get("/history", summary="获取llm 历史对话信息")
async def llm_history(id: int = 0, status: str = "done", tags: str = ""):
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "id": id,
            "status": status,
            "tags": tags.split(',')
        }
    }

@router.post("/chat", summary="对话")
async def llm_chat(chat: Chat):
    return {
        "code": 200,
        "msg": "success",
        "data": chat
    }

@router.put("/feedback", summary="反馈")
async def llm_feedback(feedback: Feedback):
    return {
        "code": 200,
        "msg": "success",
        "data": feedback
    }

@router.delete("/del", summary="删除记录")
async def llm_del(id: int=0, chat_id: int=0, record_id: int=0):
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "id": id,
            "chat_id": chat_id,
            "record_id": record_id
        }
    }