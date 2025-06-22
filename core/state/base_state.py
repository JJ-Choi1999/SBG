from typing import List, Dict, Annotated
from pydantic import BaseModel, Field
import operator

from common.enumerate.graph import ActionState


class BaseState(BaseModel):
    prompt: str = Field(
        description='用户输入提示词'
    )
    aggregate: Annotated[List, operator.add] = Field(
        default_factory=list,
        description="记录Agent 对话过程的Agent"
    )
    action_state: str = Field(
        default=ActionState.SUCCESS,
        description='执行状态'
    )