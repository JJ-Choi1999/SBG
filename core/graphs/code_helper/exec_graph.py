import re
import subprocess
import sys
import os.path
import uuid
import warnings
import shutil

from langchain_community.tools import TavilySearchResults
from langgraph.constants import START, END
from langgraph.types import RetryPolicy

from common.enum.graph import ActionState
from common.error.extra import ExtraTagError
from common.file.file import output_content_to_file, extract_paths
from core.agent.llm_agent import LLMAgent
from core.common.format_result.format_result import extract_tags, format_search_refer
from core.common.rag.vector_stores import WeaviateClient
from core.graphs.base_graph import BaseGraph
from core.prompts.code_helper import GenCodePrompt, RequirementAnalysisPrompt, GenCodeSysPrompt, ReGenCodePrompt
from core.state.code_helper import CodeHelperState, GenResult, GlobalSetting

# python3 -W ignore script.py
warnings.filterwarnings("ignore")

class ExecGraph:

    def __init__(
        self,
        install_tool: str,
        max_retry: int = 5,
        agent_client: LLMAgent | None = None,
        vector_store: WeaviateClient | None = None,
        tavily_api_key: str | None = None,
        chunk_size=200,
        running_command: str | None = None,
        enable_mutual: bool = True
    ):
        """
        执行流程
        :param install_tool: 代码安装第三方依赖的工具
        :param max_attempts: 最大重试次数
        :param agent_client: 智能体对象
        :param vector_store: 向量数据库对象
        :param tavily_api_key: tavily 搜索引擎 api_key(该值为空则不会使用web搜索)
        :param chunk_size: 切片大小
        :param running_command: 运行命令
        :param enable_mutual: 是否开启交互模式
        """
        self.__spacing = 100
        self.__install_tool = install_tool
        self.__max_retry = max_retry
        self.__agent_client = agent_client
        self.__vector_store = vector_store
        self.__tavily_api_key = tavily_api_key
        self.__chunk_size = chunk_size
        self.__running_command = running_command
        self.__retry_count: int = 1
        self.__reason: str | None = None
        self.__solution: str | None = None
        self.__enable_mutual: bool = enable_mutual

    def is_read_file(self, state: CodeHelperState):
        """
        是否读取文件内容
        :param state:
        :return:
        """
        prompt = state.prompt
        if not extract_paths(text=prompt): return False
        return True

    def insert_file_content(self, state: CodeHelperState):
        """
        插入 prompt 中文件内容到 prompt 中
        :param state:
        :return:
        """
        index = 1
        prompt = state.prompt
        file_paths = extract_paths(text=prompt, file_exists=True)
        for file_path in file_paths:

            if not os.path.exists(file_path):
                print(f' => 文件: 【{file_path}】 不存在, 跳过...')
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    prompt += (f'\n\n文件内容(<file_content></file_content>标签内为文件内容):'
                               f'\n\t({index}){file_path}内容:\n\n'
                               f'<file_content>\n{f.read()}\n</file_content>')
            except:
                pass
            finally:
                index += 1

        print(f'prompt:', prompt)

        return {
            'prompt': prompt
        }


    def requirement_analysis(self, state: CodeHelperState):
        """
        根据用户输入内容进行需求完善和需求分析
        :param state:
        :return:
        """
        print('=' * self.__spacing)
        print(f' -> 需求分析中, 用户输入需求: 【{state.prompt}】 ...')
        prompt = RequirementAnalysisPrompt.format(input_text=state.prompt)
        self.__agent_client.agent_ask(prompt=prompt, enable_assistant=True, enable_print=False)

        req_analysis = self.__agent_client.messages[-1].content
        # print(f'requirement_analysis.req_analysis:', req_analysis)
        requirement_analysis = extract_tags(text=req_analysis, tag='requirement')
        if not requirement_analysis:
            raise ExtraTagError(f'需求分析标签提取异常, 源提取文本: {req_analysis}')

        print(f' -> 需求分析结束, 需求补全与任务分解:')
        for index, req_item in enumerate(requirement_analysis):
            print(f'\t{index+1}) {req_item}')

        return {
            'gen_result': {
                'requirement_analysis': requirement_analysis
            }
        }

    def select_knowledge_workspace(self, state: CodeHelperState) -> str | None:
        """
        选择知识库工作区,
        假如未开启知识库检索则直接返回None;
        初始化时已选择工作区则返回对应初始化时选择的工作区;
        初始化时未选择工作区则选择已有工作区
        :param state:
        :return:
        """
        if not state.global_setting.enable_knowledge:
            return None

        workspace = state.data_source.workspace
        if workspace:
            return workspace
        else:
            all_collections = self.__vector_store.all_collections()

            print(f'-' * round(self.__spacing / 2))
            print(f' * 知识库工作区列表:')
            for collection_index, collection_name in enumerate(all_collections):
                print(f'\t{collection_index+1}) {collection_name}')
            print(f'-' * self.__spacing)

            while True:
                input_val = input(f' * 请选择需要作为检索源的知识库工作区:') if self.__enable_mutual else state.data_source.workspace
                input_val = input_val[0].upper() + input_val[1:]
                print(f'-' * self.__spacing)
                if input_val in all_collections:
                    print(f' * 选择工作区【{input_val}】作为检索源...')
                    break
                print(f' * 工作区【{input_val}】 不存在, 请重新输入...')

            print(f'-' * round(self.__spacing / 2))
            return input_val

    def search_knowledge(self, state: CodeHelperState):
        """
        查询知识库
        :param state:
        :return:
        """
        gen_result = state.gen_result.model_dump()
        knowledge_workspace = self.select_knowledge_workspace(state=state)
        if not knowledge_workspace: return {}

        print('=' * self.__spacing)
        print(f' -> 开始搜索知识库...')

        search_map = {}
        requirement_analysis = state.gen_result.requirement_analysis
        self.__vector_store.init_vector(split_docs=[], index_name=knowledge_workspace)

        for req_index, req_item in enumerate(requirement_analysis):
            print(f'\t-> {req_index + 1}) {req_item}')
            search_result = self.__vector_store.search(query=req_item, is_rerank=True, k=10, rerank_topn=2)
            search_result = [item.get('content') for item in search_result]

            search_map[req_item] = search_result
            for search_index, search_item in enumerate(search_result):
                print(f'\t\t{req_index + 1}.{search_index+1}) {search_item}')

        gen_result['knowledge_refer'] = search_map
        return {
            'aggregate': [gen_result]
        }

    # [todo] 之后看效果决定使用 TavilySearch 还是自研
    def search_web(self, state: CodeHelperState):
        """
        查询网页搜索引擎
        :param state:
        :return:
        """
        gen_result = state.gen_result.model_dump()
        if not state.global_setting.enable_web or not self.__tavily_api_key:
            return {}

        print('=' * self.__spacing)
        print(f' -> 开启网页搜索...')

        search_map = {}
        requirement_analysis = state.gen_result.requirement_analysis

        for req_index, req_item in enumerate(requirement_analysis):
            try:

                print(f'\t-> {req_index + 1}) {req_item}')
                tavily_search = TavilySearchResults(max_results=2, tavily_api_key=self.__tavily_api_key)
                search_result = tavily_search.invoke({'query': req_item})
                search_result = [item.get('content', '')[:self.__chunk_size] for item in search_result]

                search_map[req_item] = search_result
                for search_index, search_item in enumerate(search_result):
                    print(f'\t\t{req_index + 1}.{search_index + 1}) {search_item}')

            except Exception as e:
                print(f'\t* 网页搜索异常, 退出网页搜索, 异常原因:', str(e))

        gen_result['web_refer'] = search_map
        return {
            'aggregate': [gen_result],
        }

    def __insert_refer(self, state: CodeHelperState) -> dict:
        """
        插入web搜索摘要和知识库检索摘要
        :param state:
        :return:
        """
        gen_result = state.gen_result.model_dump()
        for item in state.aggregate:
            gen_result.update(
                GenResult(**item).model_dump(exclude_unset=True, exclude_none=True, exclude_defaults=True))
        state.aggregate.clear()

        return gen_result

    def realize_requirements(self, state: CodeHelperState):
        """
        实现需求
        :param state:
        :return:
        """
        tip_text = f'== 第【{self.__retry_count}】次执行【代码生成】【开始】'
        print(tip_text + ('=' * (self.__spacing - len(tip_text))))

        gen_result = self.__insert_refer(state=state)

        requirement_analysis = state.gen_result.requirement_analysis
        knowledge_refer = gen_result.get('knowledge_refer')
        web_refer = gen_result.get('web_refer')

        gencode_prompt = GenCodePrompt.format(
            install_tool=self.__install_tool,
            requirements=requirement_analysis,
            knowledge_refer=knowledge_refer,
            web_refer=web_refer,
            reason=self.__reason if self.__reason else '',
            solution=self.__solution if self.__solution else ''
        )
        print(f'=> 【代码生成】提示词(共 {len(gencode_prompt)} 字):\n{gencode_prompt}')
        self.__agent_client.agent_ask(prompt=gencode_prompt, enable_assistant=True, enable_print=False)
        req_analysis = self.__agent_client.messages[-1].content
        # print(f'realize_requirements.req_analysis:', req_analysis)

        gen_result = self.gen_code_wrap(text=req_analysis, gen_result=gen_result)
        self.__reason = ''
        self.__solution = ''
        return {
            'gen_result': gen_result
        }

    def gen_code_wrap(self, text: str, gen_result: dict):
        """
        生成代码结果装配器, 解析 text 文本, 把对应标签内容装配到 gen_code 对象
        :param text: 生成代码解析文本
        :param gen_result: 生成代码结果对象字典
        :return:
        """
        tags = list(GenResult.__pydantic_fields__.keys())
        for tag in tags:
            extract_result = extract_tags(text, tag=tag)
            if not extract_result: continue
            extract_content = '\n'.join(extract_result)
            gen_result[tag] = extract_content
            if tag in ['code_file', 'test_file']: re.sub(r'[\n\t\r\f\v]', '', extract_content)

        return gen_result

    def write_code_to_file(self, state: CodeHelperState):
        """
        写入生成的代码到文件
        :param state:
        :return:
        """
        project_path = state.global_setting.project_path
        if not os.path.exists(project_path): os.makedirs(project_path, exist_ok=True)

        uuid_str = str(uuid.uuid1())
        gen_result = state.gen_result.model_dump()
        gen_code = gen_result.get('gen_code', '')
        test_code = gen_result.get('test_code', '')

        code_file = os.path.join(project_path, gen_result.get('code_file', ''))
        test_file = os.path.join(project_path, gen_result.get('test_file', ''))

        if self.__retry_count > 1:
            backup_dir = os.path.join(project_path, f'v_{self.__retry_count}_{uuid_str}')
            os.makedirs(backup_dir, exist_ok=True)
            if os.path.exists(code_file): shutil.move(code_file, backup_dir)
            if os.path.exists(test_file): shutil.move(test_file, backup_dir)

        print(f'=' * self.__spacing)
        print(f'-> 生成代码写入文件【{code_file}】...')
        code_file = output_content_to_file(file_path=code_file, content=gen_code)
        print(f'-> 生成代码写入【完成】')
        print(f'-> 测试代码写入文件【{test_file}】...')
        test_file = output_content_to_file(file_path=test_file, content=test_code)
        print(f'-> 测试代码写入【完成】')

        return {
            'gen_result': {
                **gen_result,
                'code_file': code_file,
                'test_file': test_file
            }
        }

    def action_code(self, state: CodeHelperState):
        """
        执行代码
        :param state:
        :return:
        """
        tip_text = f'== 第【{self.__retry_count}】次执行【代码生成】【完成】'
        print(f'=' * self.__spacing)

        project_path = state.global_setting.project_path
        install_command = state.gen_result.install_command
        test_file = state.gen_result.test_file
        ran_result = state.gen_result.ran_result
        action_state = state.action_state

        if install_command:
            print(f' => 安装第三方依赖, 执行命令【{install_command}】')
            command_result = subprocess.run(
                install_command,
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8",  # 显式指定编码
                timeout=300
            ).stdout
            print(f' => 命令执行完成:\n', command_result)
            print(f'-' * self.__spacing)

        # 注册项目目录
        sys.path.append(project_path)

        running_command = self.__running_command if self.__running_command else 'python -W ignore'
        running_command = f'{running_command} {test_file}'
        print(f' => 运行测试文件, 执行命令【{running_command}】')

        sp_command = subprocess.run(
            running_command,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",  # 显式指定编码
            timeout=300
        )
        command_result = sp_command.stdout
        code_error = sp_command.stderr

        print(f' => 命令执行完成:\n', command_result.strip())
        print(f'-' * self.__spacing)
        print(f' => 预期结果:\n', ran_result.strip())

        # 判断运行测试文件, 测试生成代码结果, 是否与预期效果 ran_result 一样
        if command_result.strip() == ran_result.strip():
            is_success = True
        else:
            is_success = False

        # 假如超过重试次数都没实现预期效果, 则把该 graph 执行状态设置为空
        if self.__retry_count >= state.global_setting.max_retry and not is_success:
            action_state = ActionState.FAIL if code_error else ActionState.VERIFY

        print(tip_text + ('=' * (self.__spacing - len(tip_text))))
        gen_result = {
            **state.gen_result.model_dump(),
            'is_success': is_success,
            'code_error': code_error,
            'actual_result': command_result
        }
        return {
            'gen_result': gen_result,
            'gen_states': [gen_result],
            'action_state': action_state,
        }

    def is_regen_code(self, state: CodeHelperState):
        """
        判断是否重新生成代码:
        1. state.gen_result.is_success 为 True 则直接返回 END
        2. 重新执行 realize_requirements 流程:
            2.1 直到  gen_result.is_success 为 True
            2.2 重试次数(state.global_setting.max_retry)耗尽, 记录 state.action_state 为 Fail
        :param state:
        :return:
        """
        if state.gen_result.is_success: return True
        if self.__retry_count >= state.global_setting.max_retry: return True

        self.__retry_count += 1
        return False

    def error_handle(self, state: CodeHelperState):
        """
        异常处理
        :param state:
        :return:
        """
        print(f'=' * self.__spacing)

        requirement_analysis = state.gen_result.requirement_analysis
        gen_code = state.gen_result.gen_code
        test_code = state.gen_result.test_code
        ran_result = state.gen_result.ran_result
        actual_result = state.gen_result.ran_result
        code_error = state.gen_result.code_error

        regencode_prompt = ReGenCodePrompt.format(
            requirements=requirement_analysis,
            gen_code=gen_code.strip(),
            test_code=test_code.strip(),
            ran_result=ran_result.strip(),
            actual_result=actual_result.strip(),
            error_msg=code_error.strip()
        )
        print(f'重新生成代码 prompt(共【{len(regencode_prompt)}】字):\n', regencode_prompt)

        self.__agent_client.agent_ask(prompt=regencode_prompt, enable_assistant=True, enable_print=False)
        suggestion = self.__agent_client.messages[-1].content
        print(f'suggestion:', suggestion)

        reason = extract_tags(text=suggestion, tag='reason')
        solution = extract_tags(text=suggestion, tag='solution')
        self.__reason = '\n'.join(reason)
        self.__solution = '\n'.join(solution)
        print(f'reason:', self.__reason)
        print(f'solution:', self.__solution)

        print(f'=' * self.__spacing)
        reset_keys = [
            'install_command',
            'gen_code',
            'test_code',
            # 'code_file',
            # 'test_file',
            'ran_result',
            'actual_result',
            'code_error'
        ]
        gen_result = state.gen_result.model_dump()
        for reset_key in reset_keys:
            gen_result[reset_key] = ''

        return {
            'gen_result': gen_result
        }

    def graph_nodes(self):
        """
        初始化graph模块节点
        :return:
        """
        return [
            {
                'node': self.requirement_analysis,
                'action': self.requirement_analysis,
                'retry': RetryPolicy(retry_on=ExtraTagError, backoff_factor=1, max_attempts=self.__max_retry)
            },
            {
                'node': self.search_knowledge
            },
            {
                'node': self.search_web
            },
            {
                'node': self.realize_requirements,
                'defer': True
            },
            {
                'node': self.write_code_to_file
            },
            {
                'node': self.action_code
            },
            {
                'node': self.error_handle
            },
            {
                'node': self.insert_file_content
            }
        ]

    def graph_edges(self):
        """
        初始化graph 边
        :return:
        """
        return [
            {
                'source': START,
                'path': self.is_read_file,
                'path_map': {True: 'insert_file_content', False: 'requirement_analysis'},
                'edge_func': 'add_conditional_edges'
            },
            {
                'start_key': 'insert_file_content',
                'end_key': 'requirement_analysis',
                'edge_func': 'add_edge'
            },
            {
                'start_key': 'requirement_analysis',
                'end_key': 'search_knowledge',
                'edge_func': 'add_edge'
            },
            {
                'start_key': 'requirement_analysis',
                'end_key': 'search_web',
                'edge_func': 'add_edge'
            },
            {
                'start_key': 'search_knowledge',
                'end_key': 'realize_requirements',
                'edge_func': 'add_edge'
            },
            {
                'start_key': 'search_web',
                'end_key': 'realize_requirements',
                'edge_func': 'add_edge'
            },
            {
                'start_key': 'realize_requirements',
                'end_key': 'write_code_to_file',
                'edge_func': 'add_edge'
            },
            {
                'start_key': 'write_code_to_file',
                'end_key': 'action_code',
                'edge_func': 'add_edge'
            },
            {
                'source': 'action_code',
                'path': self.is_regen_code,
                'path_map': {True: END, False: 'error_handle'},
                'edge_func': 'add_conditional_edges'
            },
            {
                'start_key': 'error_handle',
                'end_key': 'realize_requirements',
                'edge_func': 'add_edge'
            },
        ]