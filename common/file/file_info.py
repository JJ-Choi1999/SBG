import os
import filetype


def extract_file_type(file_path: str) -> dict:
    """
    提取文件类型, 输入文件地址, 返回文件拓展类型和MIME类型字典
    :param file_path: 本地文件地址
    :return 文件拓展类型和MIME类型字典
    """
    kind = filetype.guess(file_path)
    if not kind: return {}
    return {
        'file_extension': kind.extension,
        'file_mime': kind.mime
    }

def extract_file_path(file_path: str) -> dict:
    return {
        'file_name': os.path.basename(file_path),
        'file_dir': os.path.dirname(file_path),
        'file_path': file_path
    }

# [todo] 需要补全其它的文件信息提取
def extract_file_info(file_path: str) -> dict:
    """
    提取文件信息, 输入文件地址, 返回文件信息
    :param file_path: 本地文件地址
    :return 文件信息字典
    """
    type_info = extract_file_type(file_path)
    path_info = extract_file_path(file_path)

    return {
        'file_size': os.path.getsize(file_path),
        **type_info,
        **path_info
    }

if __name__ == '__main__':
    pass