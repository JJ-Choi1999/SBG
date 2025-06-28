import os

from langchain_core.tools import tool
from common.file.file import recursion_file_path


@tool(
    "read_file",
    description='输入参数file_path 作为文件路径, 读取文件内容'
)
def read_file(file_path: str) -> str:

    file_content = 'ERROR: 【输入路径非可读文件...】'
    file_path = recursion_file_path(file_path)

    try:
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
    except Exception as e:
        file_content = 'ERROR: 【打开文件出错, 内容无法读取...】'

    return f'文件路径: {file_path}\n\n文件内容:\n {file_content}'