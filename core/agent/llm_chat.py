# -*- coding: utf-8 -*-
import uuid
from collections.abc import Iterator, Sequence

from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage, BaseMessageChunk, AIMessage, HumanMessage, SystemMessage


class LLMChat:

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        system_propt: str | None = None,
        chat_id: str | None = None,
        **kwargs: any
    ):
        self._base_url: str = base_url
        self._api_key: str = api_key
        self._model: str = model
        self._system_propt: str | None = system_propt
        self._chat_id: str = chat_id if chat_id else str(uuid.uuid1())
        self._stream_record: str = ""
        self._messages: list[BaseMessage] = []

        if self._system_propt:
            self._messages.insert(
                0,
                # {'role': 'system', 'content': self._system_propt}
                SystemMessage(content=self._system_propt, id=self._chat_id)
            )

        self._client = init_chat_model(
            base_url=self._base_url,
            api_key=self._api_key,
            model=self._model,
            model_provider="openai",
            **kwargs
        )

    def get_client(self):
        return self._client

    @property
    def messages(self):
        return self._messages

    def get_chat_id(self):
        return self._chat_id

    def merge_messages(self, msg: list | HumanMessage | AIMessage):
        if isinstance(msg, list):
            self._messages += msg
        else:
            self._messages.append(msg)

    def ask_stream_msg(self, ask_stream, is_print: bool = False) -> AIMessage:
        """
        获取对话流文本对象
        :param ask_stream: 对话流
        :param is_print: 是否打印对话流
        :return:
        """
        messages = []
        for chunk in ask_stream:
            msg = chunk.content
            messages.append(msg)
            if is_print: print(msg, end='')

        return AIMessage(content=("".join(messages)), id=self._chat_id)

    # [todo] 之后要统一token输入输出计数
    def ask(
        self,
        prompt: str,
        is_steam: bool = False,
        enable_assistant: bool = False
    ) -> Iterator[BaseMessageChunk] | BaseMessage:
        """
        模型对话
        :param prompt: 用户提示词
        :param is_steam: 是否流调用
        :param enable_assistant: 是否记录模型对话返回结果
        :return:
        """
        self._messages.append(HumanMessage(content=prompt, id=self._chat_id))
        ask_msg: AIMessage = None

        if is_steam:
            ask_result: any = self._client.stream(self._messages)
            if enable_assistant: ask_msg = self.ask_stream_msg(ask_stream=ask_result, is_print=True)
        else:
            ask_result: any = self._client.invoke(self._messages)
            ask_msg = ask_result.model_copy(update={"id": self._chat_id})

        if enable_assistant:
            self._messages.append(ask_msg)

        return ask_result
