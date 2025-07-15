import base64
import importlib
import os
import re
import sys
import time

from pathlib import Path
from typing import Iterator, Union

import pandas as pd
import requests

from bs4 import BeautifulSoup

IMG_FORMAT = ['.jpg', '.jpeg', '.png', '.webp', '.avif', '.svg', '.gif', '.jxl', '.heic', '.heif', '.tiff', '.tif', '.png']

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
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # [todo] 之后要实现自动获取字符集
    with open(file_path, 'w', encoding=encoding) as f:
        f.write(content)

    return file_path

def extract_paths(text: str, file_exists: bool = False, timeout: int = 300) -> list[str]:
    """
    从文本中提取所有路径字符串。
    :param text: 需要提取字符串的文本
    :param file_exists: 提取出来的文件是否需要存在
    :param timeout: 递归超时时间(单位: s)
    :return:
        返回文本中的路径字符串(
            注意: 如果仅需要提取路径字符串, 则必须保证路径在字符串中存在空格;
            如: "该段文本的路径为 /user/gen/file.txt ", 可以在正常提取到路径 ["/user/gen/file.txt"];
            但: "该段文本的路径为 /user/gen/file.txt" 或 "该段文本的路径为/user/gen/file.txt" 则只会提取到
            ["该段文本的路径为 /user/gen/file.txt"] 或 ["该段文本的路径为/user/gen/file.txt"];
            如果 file_exists=True 则会不停递归识别出来的文件路径, 剔除误提取的内容.
        ),
        如果文本中不存在路径字符串, 如: "今天北京的天气怎么样", 则返回 []
    """
    pattern = re.compile(r'(?:[A-Za-z]:[\\/])?(?:[^\\/\s，,]+[\\/])+[^\\/\s，,]+', re.IGNORECASE)
    if not file_exists: return pattern.findall(text)
    file_paths = [recursion_file_path(file_path, timeout=timeout) for file_path in pattern.findall(text)]
    return file_paths

def recursion_file_path(path_text: str, timeout: int = 300):
    """
    递归去除文本中不属于文件路径的文本
    :param path_text: 包含文件路径的文本
    :param timeout: 递归超时时间(单位: s)
    :return: 返回文件路径
    """
    recursion_path = path_text
    s_time = time.time()

    while time.time() - s_time <= timeout:

        if recursion_path[-1] in ['\\', '/']:
            return path_text

        if os.path.exists(recursion_path) and os.path.isfile(recursion_path):
            return recursion_path

        recursion_path = recursion_path[:-1]
        #print(f'recursion_path:', recursion_path)

def extract_img_url(text: str):
    """
    从文本中提取所有网络可访问图片资源字符串
    :param text: 需要提取字符串的文本
    :return:
        输入:
            '''
            查看这张照片：https://example.com/images/photo.jpg
            带参数的图片：http://example.com/images/avatar.jpg?size=100
            带多个参数的图片：https://example.com/images/logo.png?Expires=1234567890&Signature=SIGNATURE
            带片段的图片：https://example.com/images/thumbnail.gif#preview
            路径复杂的图片：https://example.com/path/to/image.webp?param1=value1&param2=value2
            '''
        输出:
            [
                'https://example.com/images/photo.jpg',
                'http://example.com/images/avatar.jpg?size=100',
                'https://example.com/images/logo.png?Expires=1234567890&Signature=SIGNATURE',
                'https://example.com/images/thumbnail.gif',
                'https://example.com/path/to/image.webp?param1=value1&param2=value2'
            ]
    """
    pattern_text = r'https?://(?:[^\s<>"\'\]?#]+)\.(?:jpe?g|png|gif|bmp|webp)(?:\?[a-zA-Z0-9_\-\.+]+=[a-zA-Z0-9_\-\.+]+(?:&[a-zA-Z0-9_\-\.+]+=[a-zA-Z0-9_\-\.+]+)*)?'

    pattern = re.compile(pattern_text, re.IGNORECASE)
    matches = pattern.findall(text)

    return matches

def valid_image_url(url: str) -> bool:
    """
    验证图片是否可访问
    :param url: 需要验证的的图片url
    :return: 图片是否url可访问
    """
    try:
        response = requests.head(url, timeout=5)
        return response.headers.get('Content-Type', '').startswith('image/')
    except:
        return False

def encode_image(image_path: str) -> str | None:
    """
    本地图片转base64
    :param image_path: 需要转换的本地图片地址
    :return: 图片base64码
    """
    try:
        if os.path.splitext(image_path)[-1] in IMG_FORMAT:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
    except:
        return None

    return None

if __name__ == '__main__':
    image_path = r"C:\Users\Lenovo\908fa0ec08fa513dcce161dd326d55fbb2fbd96e.webp"
    # image_path = r"C:\Users\Lenovo\Downloads\README.md"
    print(encode_image(image_path))