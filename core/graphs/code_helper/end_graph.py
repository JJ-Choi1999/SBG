import sys
import os
import warnings

import winsound

from langgraph.constants import START, END

from common.error.smtp import SendMailError
from common.smtp.send_mail import SendMail
from core.common.format_result.format_result import format_search_refer
from core.graphs.base_graph import BaseGraph
from core.state.code_helper import CodeHelperState

# python3 -W ignore script.py
warnings.filterwarnings("ignore")

class EndGraph:

    def __init__(
        self,
        send_mail: SendMail | None = None,
        enable_mutual: bool = True
    ):
        """
        结束流程
        :param enable_mutual:
        """
        self.__send_mail = send_mail
        self.__enable_mutual = enable_mutual
        self.__action_state_map = {
            'success': '成功',
            'fail': '异常',
            'verify': '待确认'
        }

    def end_bel(self, state: CodeHelperState):
        """
        流程结束后, 发出响铃
        :param state:
        :return:
        """
        for i in range(3):
            # 发出 1000Hz 频率的声音，持续 500ms
            if sys.platform.startswith('win'): winsound.Beep(1000, 500)
            if sys.platform.startswith('linux'): os.system("beep -f 1000 -l 500")
            if sys.platform == 'darwin': os.system("afplay /System/Library/Sounds/Ping.aiff")

    def __format_mail_content(self, state: CodeHelperState):
        """
        格式化输出发送到邮箱的内容文本
        :param state:
        :return:
        """
        prompt = state.prompt

        requirement_analysis = [f'{index + 1}){val}' for index, val in enumerate(state.gen_result.requirement_analysis)]
        gen_code = state.gen_result.gen_code
        test_code = state.gen_result.test_code
        ran_result = state.gen_result.ran_result
        actual_result = state.gen_result.actual_result
        code_file = state.gen_result.code_file
        test_file = state.gen_result.test_file

        code_error = state.gen_result.code_error
        knowledge_refer = state.gen_result.knowledge_refer
        web_refer = state.gen_result.web_refer

        knowledge_refer_content = f'''
            <h3>知识库摘要</h3>
            <div style="border: 1px dashed black;white-space: pre-wrap;margin: 0; padding: 15px;">
                {format_search_refer(search_refer=knowledge_refer)}
            </div>
        ''' if knowledge_refer else ''

        web_refer_content = f'''
            
            <h3>网页搜索摘要</h3>
            <div style="border: 1px dashed black;white-space: pre-wrap;margin: 0; padding: 15px;">
                {format_search_refer(search_refer=web_refer)}
            </div>
        ''' if web_refer else ''

        code_error_content = f'''
            
            <h3>异常描述</h3>
            <div style="border: 1px dashed black;white-space: pre-wrap;margin: 0; padding: 15px;">
                {code_error}
            </div>
        ''' if code_error else ''

        html_content = f'''
            <h2>需求分析与完善:</h2>
            <div style="border: 1px dashed black;white-space: pre-wrap;margin: 0; padding: 15px;">
                <h3>用户需求:</h3>
                <div style="border: 1px dashed black;white-space: pre-wrap;margin: 0; padding: 15px;">{prompt}</div>
                
                <h3>需求分析:</h3>
                <div style="border: 1px dashed black;white-space: pre-wrap;margin: 0; padding: 15px;">{'\n'.join(requirement_analysis)}</div>
                {knowledge_refer_content}
                {web_refer_content}
            </div>
            <h2>代码生成与测试:</h2>
            <div style="border: 1px dashed black;white-space: pre-wrap;margin: 0; padding: 15px;">
                <h3>生成代码[{code_file}]:</h3>
                <div style="border: 1px dashed black;white-space: pre-wrap;margin: 0; padding: 15px;">
                    {gen_code}
                </div>
                
                <h3>测试代码[{test_file}]:</h3>
                <div style="border: 1px dashed black;white-space: pre-wrap;margin: 0; padding: 15px;">
                    {test_code}
                </div>
            </div>
            <h2>执行结果:</h2>
            <div style="border: 1px dashed black;white-space: pre-wrap;margin: 0; padding: 15px;">
                <h3>预期结果:</h3>
                <div style="border: 1px dashed black;white-space: pre-wrap;margin: 0; padding: 15px;">
                    {ran_result}
                </div>
                
                <h3>实际结果:</h3>
                <div style="border: 1px dashed black;white-space: pre-wrap;margin: 0; padding: 15px;">
                    {actual_result}
                </div>
                {code_error_content}
            </div>
            <h2>最终state data:</h2>
            <div style="border: 1px dashed black;white-space: pre-wrap;margin: 0; padding: 15px;">{state.model_dump_json(indent=2)}</div>
        '''

        return html_content

    def send_mail(self, state: CodeHelperState):
        """
        发送代码助手流程执行结果邮件
        :param state:
        :return:
        """
        if not self.__send_mail: return

        prompt = state.prompt
        action_state = state.action_state

        subject = (f'【{self.__action_state_map.get(action_state, "")}】需求: '
                   f'【{prompt[:20]}{'...' if len(prompt) > 20 else ''}】 运行结果')
        content = self.__format_mail_content(state=state)

        try:
            self.__send_mail.send(subject=subject, content=content, mime_type='html')
        except SendMailError as e:
            print(str(e))

    def graph_nodes(self):
        """
        初始化graph模块节点
        :return:
        """
        return [
            {
                'node': self.end_bel,
            },
            {
                'node': self.send_mail,
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
                'end_key': 'send_mail',
                'edge_func': 'add_edge'
            },
            {
                'start_key': 'send_mail',
                'end_key': 'end_bel',
                'edge_func': 'add_edge'
            },
            {
                'start_key': 'end_bel',
                'end_key': END,
                'edge_func': 'add_edge'
            },
        ]