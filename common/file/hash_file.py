import os.path
import uuid
import hashlib

def get_device_id():
    """
    获取设备唯一标识
    :return:
    """
    mac = uuid.getnode()
    return format(mac, '012x')  # 格式化为12位十六进制MAC地址

def calculate_file_hash(file_path, algorithm='sha256'):
    """
    计算文件内容或目录路径字符串的哈希值

    :param file_path: 文件或目录的路径
    :param algorithm: 使用的哈希算法，默认为 'sha256'
    :return: 哈希值的十六进制字符串
    """
    if os.path.isdir(file_path):
        # 如果是目录，直接对目录路径字符串进行哈希
        hash_func = hashlib.new(algorithm)
        hash_func.update(file_path.encode('utf-8'))
        return hash_func.hexdigest()
    else:
        # 如果是文件，按原有逻辑读取文件内容并计算哈希
        hash_func = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()

def generate_unique_hash(file_path):
    """
    合并设备标识与文件哈希
    :param file_path:
    :return:
    """
    device_id = get_device_id()
    file_hash = calculate_file_hash(file_path)
    combined = device_id + file_hash
    final_hash = hashlib.sha256(combined.encode()).hexdigest()
    return final_hash