from typing import Any, Iterator

from langgraph.graph.state import CompiledStateGraph
from langgraph.pregel import Pregel
from langgraph.prebuilt.chat_agent_executor import Prompt
from langgraph_swarm import create_swarm
from langgraph_supervisor import create_supervisor
from langchain_core.language_models import LanguageModelLike
from langgraph.graph import StateGraph

class LLMA2A:

    def __init__(self, agent_executors: list[Pregel]):
        self.__agent_executors: list[Pregel] = agent_executors
        self.__supervisor: StateGraph | None = None
        self.__swam: StateGraph | None = None

    def init_supervisor(
            self,
            model: LanguageModelLike,
            prompt: Prompt | None = None,
            spv_args: dict = {},
            spv_compile: dict = {}
    ) -> CompiledStateGraph:

        self.__supervisor = create_supervisor(
            agents=self.__agent_executors,
            model=model,
            prompt=prompt,
            **spv_args
        ).compile(**spv_compile)

        return self.__supervisor

    def init_swarm(self, default_active_agent: str, **kwargs) -> CompiledStateGraph:

        self.__swam = create_swarm(
            agents=self.__agent_executors,
            default_active_agent=default_active_agent
        ).compile()

        return self.__swam

    # [todo] ask_args 要改为 pydantic
    def ask(
        self,
        client: CompiledStateGraph,
        ask_type: str = Ask.STREAM,
        ask_args: dict = {"input": {"messages": []}}
    ) -> dict[str, Any] | Iterator[dict[str, Any] | Any]:
        edge_method = getattr(client, ask_type)
        return edge_method(**ask_args)