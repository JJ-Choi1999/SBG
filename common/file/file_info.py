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
        'extension': kind.extension,
        'mime': kind.mime
    }

# [todo] 需要补全其它的文件信息提取
def extract_file_info(file_path: str) -> dict:
    """
    提取文件信息, 输入文件地址, 返回文件信息
    :param file_path: 本地文件地址
    :return 文件信息字典
    """
    type_info = extract_file_type(file_path)

    return {
        **type_info
    }

if __name__ == '__main__':
    pass