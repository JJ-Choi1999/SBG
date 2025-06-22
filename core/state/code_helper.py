import operator
import os
import uuid

from typing import Annotated, List
from pydantic import BaseModel, Field

from common.config.config import YAML_CONFIGS_INFO
from core.state.base_state import BaseState

ENABLE_MUTUAL = YAML_CONFIGS_INFO['code_helper']['mutual_config']['enable_mutual']

class GenResult(BaseModel):
    requirement_analysis: list[str] = Field(
        default_factory=list,
        deprecated="需求分析",
        strict=False
    )
    install_command: str = Field(
        default_factory=str,
        deprecated="第三方依赖安装命令",
        strict=False
    )
    gen_code: str = Field(
        default_factory=str,
        deprecated="生成代码内容",
        strict=False
    )
    test_code: str = Field(
        default_factory=str,
        deprecated="生成测试代码内容",
        strict=False
    )
    code_file: str = Field(
        default_factory=str,
        description='代码文件路径',
        strict=False
    )
    test_file: str = Field(
        default_factory=str,
        description='测试代码文件路径',
        strict=False
    )
    ran_result: str = Field(
        default_factory=str,
        deprecated='预期代码运行结果',
        strict=False
    )
    actual_result: str = Field(
        default_factory=str,
        deprecated='实际代码运行结果',
        strict=False
    )
    code_error: str = Field(
        default_factory=str,
        deprecated='代码执行,异常描述',
        strict=False
    )
    knowledge_refer: dict[str, list[str]] = Field(
        default_factory=dict,
        deprecated='知识库参考资料',
        strict=False
    )
    web_refer: dict[str, list[str]] = Field(
        default_factory=dict,
        deprecated='网页搜索参考资料',
        strict=False
    )
    is_success: bool = Field(
        default=True,
        description='运行测试生成代码结果是否和 ran_result 字段保存结果一致'
    )

class GlobalSetting(BaseModel):
    enable_knowledge: bool = Field(
        default=(
            False
            if ENABLE_MUTUAL
            else YAML_CONFIGS_INFO['code_helper']['mutual_config']['global_setting']['enable_knowledge']
        ),
        description="是否启用知识库功能[True/False]"
    )
    enable_web: bool = Field(
        default=(
            False
            if ENABLE_MUTUAL
            else YAML_CONFIGS_INFO['code_helper']['mutual_config']['global_setting']['enable_web']
        ),
        description="是否启用Web搜索功能[True/False]"
    )
    max_retry: int = Field(
        default=(
            3
            if ENABLE_MUTUAL
            else YAML_CONFIGS_INFO['code_helper']['mutual_config']['global_setting']['max_retry']
        ),
        description="[代码生成]最大重试次数[>0]",
        gt=0
    )
    project_path: str = Field(
        default=(
            os.path.join(os.getcwd(), f'pj_{str(uuid.uuid1())}')
            if ENABLE_MUTUAL
            else YAML_CONFIGS_INFO['code_helper']['mutual_config']['global_setting']['project_path']
        ),
        description='项目保存路径'
    )

class DataSource(BaseModel):
    workspace: str = Field(
        default=(
            ""
            if ENABLE_MUTUAL
            else YAML_CONFIGS_INFO['code_helper']['mutual_config']['data_source']['workspace']
        ),
        description='工作区'
    )
    file_paths: list = Field(
        default=(
            []
            if ENABLE_MUTUAL
            else YAML_CONFIGS_INFO['code_helper']['mutual_config']['data_source']['file_paths']
        ),
        description='作为数据源文件路径列表'
    )

class CodeHelperState(BaseState):
    global_setting: GlobalSetting = Field(
        default_factory=GlobalSetting,
        description='全局设置'
    )
    data_source: DataSource = Field(
        default_factory=DataSource,
        description='数据源'
    )
    gen_result: GenResult = Field(
        default_factory=GenResult,
        deprecated='当前生成代码结果'
    )
    gen_states: Annotated[List[GenResult], operator.add] = Field(
        default_factory=list,
        description='生成代码状态记录列表'
    )
