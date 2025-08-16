import filetype


def file_type(file_path: str) -> dict:
    """
    输入文件地址, 返回文件拓展类型和MIME类型字典
    :param file_path: 本地文件地址
    :return 文件拓展类型和MIME类型字典
    """
    kind = filetype.guess(file_path)
    if not kind: return {}
    return {
        'extension': kind.extension,
        'mime': kind.mime
    }


def file_info(file_path: str) -> dict:
    """
    输入文件地址, 返回文件信息
    :param file_path: 本地文件地址
    :return 文件信息字典
    """
    type_info = file_type(file_path)

    return {
        **type_info
    }

if __name__ == '__main__':
    pass