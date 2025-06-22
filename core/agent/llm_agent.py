# -*- coding: utf-8 -*-
from typing import Dict, Any, Callable
from typing import Union
from collections.abc import Sequence, Iterator

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from core.agent.llm_chat import LLMChat
from core.common.format_result.format_result import output_stream

class LLMAgent(LLMChat):

    def __init__(
        self,
        chat_id: str,
        tools: Sequence[
            Union[Dict[str, Any], type, Callable, BaseTool]
        ] = [],
        recursion_limit: int = 25,
        response_format: any = None,
        agent_args: dict = {},
        **kwargs
    ):
        """

        :param chat_id: 对话id
        :param tools: agent 可调用的工具
        :param recursion_limit: react 链请求步数
        :param response_format: 请求返回格式(在输出流添加kv映射, 'structured_response': response_format_class)
        :param agent_args: LLMAgent 拓展参数字典
        :param kwargs: LLMChat 拓展参数字典
        """
        super().__init__(chat_id=chat_id, **kwargs)
        self._recursion_limit = recursion_limit
        self._tools = tools
        self._memory = MemorySaver()

        # [todo] 之后改为wrap装饰器 + anno 注解判断
        if self._recursion_limit < 2:
            raise Exception(f'recursion_limit 不能小于2')

        self._config = {"recursion_limit": self._recursion_limit, "configurable": { "thread_id": self._chat_id }}
        self._agent_system = SystemMessage(content=self._system_propt) if self._system_propt else None

        self._agent_executor = create_react_agent(
            model=self._client,
            tools=self._tools,
            prompt=self._agent_system,
            checkpointer=self._memory,
            response_format=response_format,
            **agent_args
        )

    def agent_state_snapshot(self):
        """
        获取agent执行快照(用来记录对话历史或debug 遇到的异常下一步执行节点应该是哪个)
        :return:
        """
        return self._agent_executor.get_state(config=self._config)

    def agent_ask(self, prompt: str, enable_assistant: bool = False, enable_print: bool = True) -> Iterator[dict[str, Any] | Any]:
        """
        agent 对话
        :param prompt: 提示词
        :param enable_assistant: 是否记录对话流
        :param enable_print: 是否打印 stream 流输出
        :return:
        """
        self._messages.append(HumanMessage(content=prompt, id=self._chat_id))
        agent_stream = self._agent_executor.stream(
            {
                "messages": [
                    HumanMessage(content=prompt)
                ]
            },
            self._config,
            stream_mode=["updates", "messages", "custom"]
        )

        stream_msgs = output_stream(agent_stream=agent_stream, chat_id=self._chat_id, enable_print=enable_print)
        if enable_assistant:
            self.merge_messages(stream_msgs)

        return agent_stream