import os

from langchain_core.tools import tool


@tool(
    "read_file",
    description='输入参数file_path 作为文件路径, 读取文件内容'
)
def read_file(file_path: str) -> dict:

    file_content = 'ERROR: 【输入路径非可读文件...】'

    try:
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
    except Exception as e:
        file_content = 'ERROR: 【打开文件出错, 内容无法读取...】'

    return {
        'file_path': file_path,
        'file_content': file_content
    }