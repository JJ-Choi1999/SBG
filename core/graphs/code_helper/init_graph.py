import os
import time
import warnings
from itertools import chain

from langgraph.constants import START, END
from weaviate.config import AdditionalConfig, Timeout

from common.error.load import UnLoadableError
from common.file.file import iter_file_infos
from core.common.rag.embedding import EmbeddingClient
from core.common.rag.rerank import RerankClient
from core.common.rag.vector_stores import WeaviateClient
from core.graphs.base_graph import BaseGraph
from core.state.code_helper import CodeHelperState

# python3 -W ignore script.py
warnings.filterwarnings("ignore")

class InitGraph:

    def __init__(
        self,
        vector_store: WeaviateClient | None = None,
        chunk_size=200,
        chunk_overlap=20,
        enable_mutual: bool = True
    ):
        """
        初始化代码生成器
        :param vector_store: 向量数据库
        :param chunk_size: 切片大小
        :param chunk_overlap: 切片重合度
        :param enable_mutual: 是否开启交互
        """
        self.__spacing = 100
        self.__vector_store: WeaviateClient | None = vector_store
        self.__chunk_size = chunk_size
        self.__chunk_overlap = chunk_overlap
        self.__enable_mutual: bool = enable_mutual

    def print_global_setting(self, state: CodeHelperState):
        """
        打印全局变量
        :param state:
        :return:
        """
        index = 1
        data = {}
        global_setting = state.global_setting
        print('=' * self.__spacing)
        print('[当前全局变量]:')

        for field_name, field_info in global_setting.__pydantic_fields__.items():
            if not field_info.description: continue
            print(f'{index}) {field_info.description}: {field_info.default}')
            data[field_name] = field_info.default
            index += 1

        print('=' * self.__spacing)

    def is_global_setting(self, state: CodeHelperState):
        """
        是否设置全局变量
        :param state:
        :return:
        """
        print_text = f'* 输入值为空, 不修改全局变量...'
        # change_type: str = 'unchage_global'
        is_change: bool = False

        while True:

            input_val = input(f'是否设置全局变量[Y/N](直接回车表示N): ') if self.__enable_mutual else 'N'

            if not input_val.lower() in ['y', 'n', '']:
                print('输入类型不为 Y/N, 请重新输入...')
            else:
                if input_val.lower() == 'y':
                    print_text = f'* 输入值为 {input_val}, 修改全局变量...'
                    # change_type = 'chage_global'
                    is_change = True

                elif input_val.lower() == 'n':
                    print_text = f'* 输入值为 {input_val}, 不修改全局变量...'
                    # change_type = 'unchage_global'
                    is_change = False

                # if input_val in ['n', ''] and state.global_setting.enable_knowledge:
                #     print_text = f'* 不修改全局变量, 跳转设置知识库...'
                #     change_type = 'edit_knowledge'

                print(print_text)
                print('=' * self.__spacing)
                # return change_type
                return is_change

    def edit_global_setting(self, state: CodeHelperState):
        """
        修改全局变量
        :param state:
        :return:
        """
        data = {}
        index = 1
        global_setting = state.global_setting

        for field_name, field_info in global_setting.__pydantic_fields__.items():
            if not field_info.description: continue
            input_val = input(f'{index}) {field_info.description}(当前值: {field_info.default}; 直接回车则不修改原值): ')
            # [todo] input_val 要用更安全的方法转换对应值
            if field_name == 'project_path':
                dir_path = f'{input_val}' if input_val else field_info.default
                data[field_name] = dir_path
            else:
                data[field_name] = eval(input_val) if input_val else field_info.default
            index += 1

        print('=' * self.__spacing)
        return {
            'global_setting': data
        }

    def is_setting_knowledge(self, state: CodeHelperState):
        """
        不修复全局变量的条件下, 通过判断 state.global_setting.enable_knowledge 设置是否需要开启知识库编辑
        :param state:
        :return:
        """
        return {
            'global_setting': state.global_setting.model_dump()
        }
    
    def is_setting_vector(self, state: CodeHelperState):
        """
        判断是否设置向量数据库路由
        :param state:
        :return: 返回True 表示设置向量数据库路由, 返回False 表示不设置向量数据库路由
        """
        enable_knowledge = state.global_setting.enable_knowledge
        all_collections = self.__vector_store.all_collections()

        while enable_knowledge:
            if not all_collections:
                print(f'* 目前知识库没有工作区, 请输入工作区并上传文件到知识库...')
                return True
            else:
                input_val = input('* 是否需要对原有知识库工作区进行修改[Y/N]: ') if self.__enable_mutual else 'N'
                if input_val.lower() == 'y':
                    print('* 开始编辑已有知识库...')
                    return True
                elif input_val.lower() == 'n':
                    print('* 无需修改知识库工作区, 已完成全局变量设置...')
                    return False
                else:
                    print('* 输入标识异常, 请重新输入, 仅支持[Y/N](不区分大小写)...')

        return False

    # [todo] 之后要加上数据库映射, 工作区名和实际文件映射要分离
    def edit_workspace(self, state: CodeHelperState):
        """
        编辑知识库工作区
        :param state:
        :return: 新增、更新、追加的工作区名
        """

        all_collections = self.__vector_store.all_collections()
        for index in range(len(all_collections)):
            if index == 0: print(f'** 已创建工作区列表: ')
            print(f'{index + 1}) {all_collections[index]}')

        input_val = input('[选择/新增]知识库工作区[仅英文, 如: my_workspace]: ')
        input_val = input_val[0].upper() + input_val[1:]
        work_mode = '创建并上传文件'

        while input_val in all_collections:
            print(f'-' * round(self.__spacing / 2))
            print(f'* 工作区【{input_val}】已存在, 请选择操作模式:')
            print(f'[1] 全量更新(使用新文件完全替换旧工作区内容)')
            print(f'[2] 增量插入(上传文件追加到原知识库[注意: 内容不要重复, 否则可能影响检索效率和准确度])')
            print(f'[3] 重新选择/输入工作区')
            select_val = input('* 请输入操作模式序号:')

            if select_val == '1':
                self.__vector_store.delete_collection(collection_name=input_val)
                work_mode = '全量更新'
                break
            elif select_val == '2':
                work_mode = '增量插入'
                break
            elif select_val == '3':
                input_val = input('请输入知识库工作区名[仅英文, 可选择已存在知识库, 或新增知识库]: ')
            else:
                print(f'选择模式不存在, 输入值必须为【{'\\'.join(['1', '2', '3'])}】')

        print(f'-' * round(self.__spacing / 2))
        print(f'* 已{'选择' if input_val in all_collections else '创建'}工作区【{input_val}】, 工作模式【{work_mode}】')
        print(f'-' * round(self.__spacing / 2))

        return {
            'data_source': {
                **state.global_setting.model_dump(),
                'workspace': input_val
            }
        }

    def add_data_to_vector(self, state: CodeHelperState):
        """
        添加数据到向量数据库
        :param state:
        :return:
        """
        file_count = 0
        file_paths = []
        split_docs_map = {}

        while True:

            input_val = input(f'输入需要作为数据源的文件/文件夹地址, 输入Exit() 结束上传并保存退出: ')
            if input_val.lower() == 'exit()':
                break

            file_path = input_val
            if not os.path.exists(file_path):
                print(f'* 该文件/文件夹不存在请重新输入...')

            else:

                input_file_paths = list(iter_file_infos(file_path))
                file_count += len(input_file_paths)

                for file_index in range(len(input_file_paths)):

                    file_info = input_file_paths[file_index]

                    input_file = file_info.get('file_path', '')
                    input_type = file_info.get('file_type', 'txt')

                    try:

                        if input_file in file_paths:
                            file_paths.remove(input_file)
                            split_docs_map.pop(input_file)
                            file_count -= 1
                            print(f'*文件 【{input_file}】 重复输入, 更新文件内容...')

                        split_docs_map[input_file] = self.__vector_store.load_file(
                            file_path=input_file,
                            file_type=input_type,
                            chunk_size=self.__chunk_size,
                            chunk_overlap=self.__chunk_overlap
                        )
                        file_paths.append(input_file)
                        print(f'【{len(file_paths)}/{file_count}】已添加文件: {input_file}')
                    except UnLoadableError as e:
                        print(f'文件: {input_file} 出现异常: {str(e)}')

        s_time = time.time()
        print(f'* 文件正在写入知识库...')
        split_docs = list(chain.from_iterable(list(split_docs_map.values())))
        self.__vector_store.init_vector(split_docs=split_docs, index_name=state.data_source.workspace)
        print(f'* 文件写入知识库完成...')
        e_time = time.time()
        print(f'c_time:', e_time - s_time)

        return {
            'data_source': {
                **state.data_source.model_dump(),
                'file_paths': file_paths
            }
        }

    def graph_nodes(self):
        """
        初始化graph模块节点
        :return:
        """
        return [
            {
                'node': self.print_global_setting
            },
            {
                'node': self.edit_global_setting
            },
            {
                'node': self.add_data_to_vector
            },
            {
                'node': self.edit_workspace
            },
            {
                'node': self.is_setting_knowledge
            }
        ]

    def graph_edges(self):
        """
        初始化graph 边
        :return:
        """
        return [
            {
                'start_key': START,
                'end_key': 'print_global_setting',
                'edge_func': 'add_edge'
            },
            {
                'source': 'print_global_setting',
                'path': self.is_global_setting,
                'path_map': { True: 'edit_global_setting', False: 'is_setting_knowledge' },
                'edge_func': 'add_conditional_edges'
            },
            {
                'source': 'is_setting_knowledge',
                'path': self.is_setting_vector,
                'path_map': {True: 'edit_workspace', False: END},
                'edge_func': 'add_conditional_edges'
            },
            {
                'source': 'edit_global_setting',
                'path': self.is_setting_vector,
                'path_map': {True: 'edit_workspace', False: END},
                'edge_func': 'add_conditional_edges'
            },
            {
                'start_key': 'edit_workspace',
                'end_key': 'add_data_to_vector',
                'edge_func': 'add_edge'
            },
            {
                'start_key': 'add_data_to_vector',
                'end_key': END,
                'edge_func': 'add_edge'
            },
        ]