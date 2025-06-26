import importlib
import os
import re
import sys
from pathlib import Path
from typing import Iterator, Union

import pandas as pd

from bs4 import BeautifulSoup

def iter_file_infos(file_path: Union[str, Path] , filter_suffix: list[str] = []) -> Iterator[dict[str, Union[str, Path]]]:
    """
    输入一个 file_path，如果是一个文件，则返回包含该文件信息的长度为1的列表，每个元素是 dict 类型；
    如果是一个目录，则递归返回该目录下所有子目录中的文件信息列表，每个文件作为一个 dict 元素。
    :param file_path: 文件/文件夹地址
    :param filter_suffix: 需要过滤的文件后缀名, 不在该列表的文件后缀不记录
    :return:
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The path {file_path} does not exist.")

    if os.path.isfile(file_path):
        # 获取文件后缀名作为文件类型
        _, ext = os.path.splitext(file_path)
        file_type = ext.lower().lstrip('.') or 'unknown'
        if not filter_suffix or file_type in filter_suffix:
            yield {'file_type': file_type, 'file_path': file_path}

    for root, dirs, files in os.walk(file_path):
        for file in files:
            full_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)
            file_type = ext.lower().lstrip('.') or 'unknown'
            if filter_suffix and not (file_type in filter_suffix): continue
            yield {'file_type': file_type, 'file_path': full_path}

    # return file_list


def bs4_extractor(html: str, features: str = 'lxml') -> str:
    soup = BeautifulSoup(html, features=features)
    return soup.text.strip()

def excel_to_markdown(input_file, output_file=None):
    """
    将Excel文件转换为Markdown格式

    参数:
        input_file (str): Excel文件路径
        output_file (str): 输出文件路径，若不提供则返回字符串
    """
    try:
        # 读取Excel文件的所有工作表
        excel_data = pd.ExcelFile(input_file)
        markdown_result = []

        # 遍历每个工作表
        for sheet_name in excel_data.sheet_names:
            # 读取工作表数据
            df = pd.read_excel(excel_data, sheet_name)

            # 处理表头
            header = "| " + " | ".join(df.columns) + " |"
            # 创建分隔行（自动适配列数）
            separator = "| " + " | ".join(["---"] * len(df.columns)) + " |"

            # 处理数据行（处理NaN值为空字符串）
            rows = []
            for _, row in df.iterrows():
                # 将每行数据转换为字符串并处理空值
                formatted_row = [
                    str(cell) if pd.notna(cell) else ""
                    for cell in row
                ]
                rows.append("| " + " | ".join(formatted_row) + " |")

            # 组合当前工作表的markdown内容
            markdown_result.append(f"## {sheet_name}")
            markdown_result.append(header)
            markdown_result.append(separator)
            markdown_result.extend(rows)
            markdown_result.append("")  # 添加空行分隔不同工作表

        # 组合所有内容
        result = "\n".join(markdown_result)

        # 决定输出方式
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result)
            return f"已成功写入到 {output_file}"
        else:
            return result

    except Exception as e:
        return f"转换失败: {str(e)}"

def py_module_adap(py_path: str) -> dict[str, str]:
    """
    python 文件导入适配器, 输入一个 python 文件路径, 返回一个在其它python文件中使用的可导入文件
    :param py_path:
    :return:
    """
    module_paths = []
    file_path = py_path

    while True:

        py_dir = os.path.dirname(py_path)
        py_path, module_name = os.path.split(py_path)
        module_name = module_name.replace('.py', '')

        if not module_name: return {}

        module_paths.insert(0, module_name)
        if py_dir in sys.path:
            return {'py_path': file_path, 'module': '.'.join(module_paths)}

        try:
            importlib.import_module('.'.join(module_paths))
        except:
            pass

def output_content_to_file(file_path: str, content: str, encoding: str = 'utf-8') -> str:
    """
    输出内容到文件
    :param file_path: 文件地址
    :param content: 文件内容
    :param encoding: 写入文件字符集编码
    :return:
    """
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    # [todo] 之后要实现自动获取字符集
    with open(file_path, 'w', encoding=encoding) as f:
        f.write(content)

    return file_path

def extract_paths(text) -> list[str]:
    """
    从文本中提取所有路径字符串。
    :param text: 需要提取字符串的文本
    :return:
        返回文本中的路径字符串(
            注意: 如果仅需要提取路径字符串, 则必须保证路径在字符串中存在空格;
            如: "该段文本的路径为 /user/gen/file.txt ", 可以在正常提取到路径 ["/user/gen/file.txt"];
            但: "该段文本的路径为 /user/gen/file.txt" 或 "该段文本的路径为/user/gen/file.txt" 则只会提取到
            ["该段文本的路径为 /user/gen/file.txt"] 或 ["该段文本的路径为/user/gen/file.txt"]
        ),
        如果文本中不存在路径字符串, 如: "今天北京的天气怎么样", 则返回 []
    """
    pattern = re.compile(r'(?:[A-Za-z]:[\\/])?(?:[^\\/\s，,]+[\\/])+[^\\/\s，,]+')
    return pattern.findall(text)