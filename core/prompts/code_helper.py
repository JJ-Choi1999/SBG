import textwrap
import sys

from langchain.prompts import PromptTemplate

from core.common.format_result.format_result import format_search_refer


class GenCodeSysPrompt:

    __prompt: str = '''
    你是一个 {code_type} 代码生成助手, 可以实现以下功能:
    1. 判断用户输入内容, 不是 {code_type} 代码编码需求, 直接输出: 【非编码需求, 请重新输入!!】, 终止后续步骤执行.
    2. 可以安装用户输入, 实现以下功能(以下功能可互相独立, 也可依次执行, 按照用户输入内容的执行要求, 进行判断):
        2.1 根据用户输入的编码需求, 进行需求分析.
        2.2 根据需求分析, 判断是否需要使用 {install_tool} 安装第三方依赖.
        2.3 按照用户需求, 编写可实现对应需求的 {code_type} 代码.
        2.4 根据生成代码, 编写针对生成代码的 {code_type} 测试代码.
        2.5 生成测试代码, 执行完成后的输出结果(如果用户要求输出预期效果, 则测试代码的执行方式要尽可能, 满足输出结果为预期效果, 不要打印多余的信息).
    '''
    __pt = PromptTemplate.from_template(__prompt)

    @classmethod
    def format(cls, **kwargs) -> str:
        platform = sys.platform
        return textwrap.dedent(cls.__pt.format(platform=platform, **kwargs))[1:-1]

class RequirementAnalysisPrompt:

    __prompt: str = '''
    用户的输入内容为 {input_text}, 按照用户输入内容进行需求分析, 完善用户提出的需求, 并把用户提出的需求细化, 并按以下格式输出:
    <requirements>
        <requirement>[分解需求1]</requirement>
        <requirement>[分解需求2]</requirement>
        <requirement>[分解需求3]</requirement>
        ...
    </requirements>
    
    说明:
        <requirements></requirements> 表示需求分解列表
        <requirement></requirement> 表示分解需求项
    '''
    __pt = PromptTemplate.from_template(__prompt)

    @classmethod
    def format(cls, **kwargs) -> str:
        platform = sys.platform
        return textwrap.dedent(cls.__pt.format(platform=platform, **kwargs))[1:-1]


class GenCodePrompt:
    __prompt: str = '''
    用户需求:{requirements}
    {knowledge_refer}{web_refer}
    要求:
        1. 生成用户需求, 编码实现后的预期结果.
        2. 判断是否需要导入第三方依赖库, 如果需要, 则打印 {install_tool} 工具安装第三方依赖库命令到输出文本中.
        3. 除非用户指定, 否则输出的代码, 必须是可在 {platform} 系统环境中运行的代码.
        4. 如果存在参考摘要, 则结合参考摘要, 实现用户需求.
        4. 生成的测试代码, 可以实现在不同文件中, 测试按照用户需求生成代码的结果.
    {remark}
    输出格式:
        1. 预期结果: <ran_result>[代码执行结果]</ran_result>
        2. 安装依赖: <install_command>[第三方依赖库安装命令]</install_command>
        3. 代码实现: <gen_code>[用户编码需求实现代码]</gen_code>
        4. 测试代码: <test_code>[测试代码]</test_code>
        5. 生成代码文件名: <code_file>[用户编码需求实现代码, 保存的文件名]</code_file>
        6. 测试代码文件名: <test_code>[测试代码, 保存的文件名]</test_code>

    输出格式说明:
        1. 预期结果: <ran_result></ran_result> 表示用户需求执行完后需要输出的内容(如果用户有指定预期结果, 就使用用户输入的预期结果)
        2. 依赖安装: <install_command></install_command> 表示需安装的第三方依赖库, 如不需要安装第三方依赖库则不需要打印
        3. 代码实现: <gen_code></gen_code> 表示安装用户输入的需求分析, 实现的满足需求的代码
        4. 测试代码: <test_code></test_code> 表示可以在其它文件下测试生成代码的测试文件代码
        5. 生成代码文件名: <code_file></code_file> 表示保存代码实现的文件名(假如用户有指定项目文件夹结构, 则添加对应项目路径到文件路径前)
        6. 测试代码文件名: <test_file></test_file> 表示保存测试代码的文件名(假如用户有指定项目文件夹结构, 则添加对应项目路径到文件路径前)
    '''
    __pt = PromptTemplate.from_template(__prompt)

    @classmethod
    def format(cls, **kwargs) -> str:

        platform = sys.platform

        knowledge_refer = ''
        web_refer = ''
        requirements = ''
        remark = ''

        knowledge_refer_data = kwargs.pop('knowledge_refer', {})
        web_refer_data = kwargs.pop('web_refer', {})
        requirement_analysis = kwargs.pop('requirements', [])
        reason = kwargs.pop('reason', '')
        solution = kwargs.pop('solution', '')

        if reason and solution:
            remark = ('\t备注:\n'
                      + f'\t\t1)防止出现以下问题: {reason}\n'
                      + f'\t\t2)生成代码时参考以下描述生成: {solution}\n')

        if knowledge_refer_data:
            knowledge_refer = '\n\t知识库摘要:' + format_search_refer(search_refer=knowledge_refer_data) + '\n'

        if web_refer_data:
            web_refer = '\n\t网页搜索摘要:' + format_search_refer(search_refer=web_refer_data) + '\n'

        if requirement_analysis:
            for req_index, req_item in enumerate(requirement_analysis):
                requirements += f'\n\t{req_index + 1}) {req_item}'

        return textwrap.dedent(
            cls.__pt.format(
                platform=platform,
                knowledge_refer=knowledge_refer,
                web_refer=web_refer,
                requirements=requirements,
                remark=remark,
                **kwargs
            )
        )[1:-1]

class ReGenCodePrompt:
    __prompt: str = '''
    存在用户需求:
        {requirements}
        
    使用以下代码实现:
        {gen_code}
        
    用以下代码调用上述代码运行:
        {test_code}
    
    预期结果:
        {ran_result}
    
    实际结果:
        {actual_result}
    
    {error_msg}
    
    回答并解决以下问题:
    {intent_msg}
    
    输出格式:
        <reason>[问题出现原因]</reason>
        <solution>[上述问题解决方案]</solution>
    说明:
        <reason></reason> 表示上述问题的出现原因
        <solution></solution> 表示上述问题的解决方案
    '''
    __pt = PromptTemplate.from_template(__prompt)

    @classmethod
    def format(cls, **kwargs) -> str:
        index = 1
        error_msg = kwargs.pop('error_msg', '')
        requirement_analysis = kwargs.pop('requirements', [])

        requirements = ''
        intent_msg = f'\t{index})输出预期结果和实际结果不一致的原因;'.strip()

        if error_msg:
            error_msg = f'出现以下异常:\n\t{error_msg}'
            index += 1
            intent_msg += f'\t{index})输出出现上述异常的原因;'.strip()

        index += 1
        intent_msg += f'\t{index})并输出解决方案.'.strip()

        if requirement_analysis:
            for req_index, req_item in enumerate(requirement_analysis):
                requirements += f'\n\t{req_index + 1}) {req_item}'

        return textwrap.dedent(
            cls.__pt.format(
                error_msg=error_msg,
                intent_msg=intent_msg,
                requirements=requirements,
                **kwargs
            )
        )[1:-1]