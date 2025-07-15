import os.path
import sys
import time
from itertools import chain
from pathlib import Path
import uuid
import warnings

from weaviate.config import AdditionalConfig, Timeout

from common.error.load import UnLoadableError
from common.file.file import iter_file_infos

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from common.config.config import YAML_CONFIGS_INFO
from common.smtp.send_mail import SendMail
from core.agent.llm_agent import LLMAgent
from core.common.rag.embedding import EmbeddingClient
from core.common.rag.rerank import RerankClient
from core.common.rag.vector_stores import WeaviateClient
from core.graphs.base_graph import BaseGraph
from core.graphs.code_helper.end_graph import EndGraph
from core.graphs.code_helper.exec_graph import ExecGraph
from core.graphs.code_helper.init_graph import InitGraph
from core.prompts.code_helper import GenCodeSysPrompt
from core.state.code_helper import CodeHelperState

# python3 -W ignore script.py
warnings.filterwarnings("ignore")

class CompileGraph:
    def __init__(
        self,
        enable_mutual: bool = True,
        vector_store: WeaviateClient | None = None,
        agent_client: LLMAgent | None = None,
        send_mail: SendMail | None = None,
        code_type: str | None = None,
        install_tool: str | None = None,
        tavily_api_key: str | None =None
    ):
        self.__vector_store = vector_store
        self.__agent_client = agent_client
        self.__send_mail = send_mail

        self.__enable_mutual = enable_mutual
        self.__code_type = code_type if code_type else YAML_CONFIGS_INFO['code_helper']['code_type']
        self.__install_tool = install_tool if install_tool else YAML_CONFIGS_INFO['code_helper']['install_tool']
        self.__tavily_api_key = tavily_api_key if tavily_api_key else YAML_CONFIGS_INFO['code_helper']['tavily_api_key']
        self.__chunk_size = YAML_CONFIGS_INFO.get('code_helper', {}).get('chunk_size', 200)
        self.__chunk_overlap = YAML_CONFIGS_INFO.get('code_helper', {}).get('chunk_size', 20)
        self.__running_command = YAML_CONFIGS_INFO['code_helper']['running_command']

        if not self.__vector_store:
            self.__vector_store = WeaviateClient(
                embedding_client=EmbeddingClient(
                    base_url=YAML_CONFIGS_INFO['code_helper']['vector_store']['embedding_client']['base_url'],
                    model_uid=YAML_CONFIGS_INFO['code_helper']['vector_store']['embedding_client']['model_uid']
                ).xinference_embeddings,
                rerank_client=RerankClient(
                    base_url=YAML_CONFIGS_INFO['code_helper']['vector_store']['rerank_client']['base_url'],
                    model_uid=YAML_CONFIGS_INFO['code_helper']['vector_store']['embedding_client']['model_uid']
                ),
                port=YAML_CONFIGS_INFO['code_helper']['vector_store']['port'],
                grpc_port=YAML_CONFIGS_INFO['code_helper']['vector_store']['grpc_port'],
                additional_config=AdditionalConfig(
                    timeout=Timeout(
                        init=YAML_CONFIGS_INFO['code_helper']['vector_store']['additional_config']['timeout']['init'],
                        query=YAML_CONFIGS_INFO['code_helper']['vector_store']['additional_config']['timeout']['query'],
                        insert=YAML_CONFIGS_INFO['code_helper']['vector_store']['additional_config']['timeout']['insert'],
                    )  # 单位: s
                )
            )

        if not self.__agent_client:
            self.__extra_body = YAML_CONFIGS_INFO.get('code_helper', {}).get('agent_client', {}).get('extra_body', {})
            self.__agent_client = LLMAgent(
                base_url=YAML_CONFIGS_INFO['code_helper']['agent_client']['base_url'],
                api_key=YAML_CONFIGS_INFO['code_helper']['agent_client']['api_key'],
                model=YAML_CONFIGS_INFO['code_helper']['agent_client']['model'],
                system_propt=GenCodeSysPrompt.format(
                    code_type=self.__code_type,
                    install_tool=self.__install_tool
                ),
                extra_body={} if not self.__extra_body else self.__extra_body,
                chat_id=str(uuid.uuid1()),
                tools=[]
            )

        if not self.__send_mail:
            self.__send_mail = SendMail(
                from_mail=YAML_CONFIGS_INFO['code_helper']['send_mail']['from_mail'],
                to_mail=YAML_CONFIGS_INFO['code_helper']['send_mail']['to_mail'],
                auth_code=YAML_CONFIGS_INFO['code_helper']['send_mail']['auth_code'],
            )


    def compile_and_run(self, graph_class, graph_name: str, **kwargs) -> CodeHelperState:

        input_data = kwargs.pop("input_data", {})
        config = kwargs.pop("config", {})
        kwargs['enable_mutual'] = self.__enable_mutual

        graph_instance = graph_class(**kwargs)
        node_funcs = graph_instance.graph_nodes()
        edge_maps = graph_instance.graph_edges()

        workflow = BaseGraph(state=CodeHelperState, node_funcs=node_funcs, edge_maps=edge_maps)
        graph = workflow.compile()

        max_retry = input_data.get('global_setting', {}).get('max_retry', 3)
        if "recursion_limit" not in config:
            config["recursion_limit"] = len(edge_maps) * max_retry * 2 if graph_name == 'ExecGraph' else len(edge_maps)

        result = graph.invoke(input=input_data, config=config)
        return CodeHelperState(**result)

    def run(self, prompt):

        end_result = {}

        try:
            # Step 1: InitGraph
            init_result = self.compile_and_run(
                graph_class=InitGraph,
                graph_name='InitGraph',
                vector_store=self.__vector_store,
                input_data={"prompt": prompt},
                chunk_size=self.__chunk_size,
                chunk_overlap=self.__chunk_overlap
            )


            workspace = init_result.data_source.workspace
            file_paths = init_result.data_source.file_paths
            enable_knowledge = init_result.global_setting.enable_knowledge

            if self.__enable_mutual and enable_knowledge and workspace and file_paths:
                self.update_vector_data(index_name=workspace, file_paths=file_paths)

            # Step 2: ExecGraph
            self.__max_retry = init_result.global_setting.max_retry
            exec_result = self.compile_and_run(
                graph_class=ExecGraph,
                graph_name='ExecGraph',
                install_tool=self.__install_tool,
                max_retry=self.__max_retry,
                agent_client=self.__agent_client,
                vector_store=self.__vector_store,
                tavily_api_key=self.__tavily_api_key,
                input_data=init_result.model_dump(),
                chunk_size=self.__chunk_size,
                running_command=self.__running_command
            )

            # Step 3: EndGraph
            end_result = self.compile_and_run(
                graph_class=EndGraph,
                graph_name='EndGraph',
                send_mail=self.__send_mail,
                input_data=exec_result.model_dump()
            )
        except Exception as e:
            print(f'代码生成器执行出现异常, 异常原因: {str(e)}')
        finally:
            self.__close_vector()

        return end_result

    def __close_vector(self):
        if not self.__vector_store:
            self.__vector_store.close()

    def update_vector_data(self, index_name: str, file_paths: list[str]):
        """
        更新向量数据库指定索引数据
        :param index_name: 索引名
        :param file_paths: 作为更新源数据的文件列表
        :return:
        """
        print(f'=' * 100)
        split_docs_map = {}

        for file_index, file_path in enumerate(file_paths):
            try:
                split_docs_map[file_path] = self.__vector_store.load_file(
                    file_path=file_path,
                    file_type=os.path.splitext(file_path)[-1][1:],
                    chunk_size=self.__chunk_size,
                    chunk_overlap=self.__chunk_overlap
                )
                print(f'【{file_index + 1}/{len(file_paths)}】已添加文件: {file_path}')

            except UnLoadableError as e:
                print(f'【{file_index + 1}/{len(file_paths)}】文件: {file_path} 出现异常: {str(e)}')

        print(f'* 文件正在写入知识库...')
        s_time = time.time()
        split_docs = list(chain.from_iterable(list(split_docs_map.values())))
        if index_name in self.__vector_store.all_collections():
            self.__vector_store.delete_collection(collection_name=index_name)
        self.__vector_store.init_vector(split_docs=split_docs, index_name=index_name)
        print(f'* 文件写入知识库完成, 耗时: 【{time.time() - s_time}(s)】')

if __name__ == '__main__':
    __enable_mutual = YAML_CONFIGS_INFO['code_helper']['mutual_config']['enable_mutual']
    prompt = input(f'我是一个编码助手, 请输入您的编码需求: ') \
        if __enable_mutual \
        else YAML_CONFIGS_INFO['code_helper']['mutual_config']['prompt']
    compile_graph = CompileGraph(enable_mutual=__enable_mutual)
    compile_graph.run(prompt=prompt)
