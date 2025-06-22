import io
import os
import uuid

from PIL import Image
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph

from common.err.graph import EdgeMapsError, EdgeFuncHasError


class BaseGraph:

    # [todo] edge_maps 里面的字典要使用 pydantic 验证
    def __init__(self, state: any, node_funcs: list, edge_maps: list[dict]):
        self.__state = state
        self.__node_funcs = node_funcs
        self.__edge_maps = edge_maps
        self.__builder: StateGraph = StateGraph(self.__state)
        self.__graph: CompiledStateGraph | None = None

    def __add_nodes(self) -> StateGraph:
        """
        添加节点
        :return:
        """
        for node in self.__node_funcs:
            self.__builder.add_node(**node)

        return self.__builder

    def __add_edges(self) -> StateGraph:
        """
        添加边
        :return:
        """
        if len(self.__edge_maps) <= 1:
            raise EdgeMapsError('边映射为空或只有一个节点')

        for edge_map in self.__edge_maps:

            edge_func = edge_map.pop('edge_func')
            if not hasattr(self.__builder, edge_func):
                raise EdgeFuncHasError(f'不存在边映射方法: {edge_func}')

            edge_method = getattr(self.__builder, edge_func)
            edge_method(**edge_map)

        return self.__builder

    @property
    def graph(self):
        return self.__graph

    def compile(self, **kwargs) -> CompiledStateGraph:
        self.__add_nodes()
        self.__add_edges()
        self.__graph = self.__builder.compile(**kwargs)
        return self.__graph

    def draw_graph(self, graph: CompiledStateGraph) -> str:

        file_path = os.path.join(os.getcwd(), f'graph-{str(uuid.uuid1())}.png')
        image_stream = io.BytesIO(graph.get_graph().draw_mermaid_png())
        image = Image.open(image_stream)
        image.save(file_path)

        return file_path