import logging
import os.path
from logging.handlers import RotatingFileHandler

from common.config.config import YAML_CONFIGS_INFO



class Logger:

    @staticmethod
    def get_instance(file_path: str):

        # 默认 log 路径
        project_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        default_log_path = os.path.join(project_path, 'logs', 'app.log')

        # 初始化 log 文件夹
        log_file = YAML_CONFIGS_INFO.get('log_config', {}).get('LOG_FILE')
        log_file = log_file if log_file else default_log_path
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)

        # 获取log 配置参数
        max_bytes = YAML_CONFIGS_INFO.get('log_config', {}).get('LOG_FILE_MAX_SIZE') * 1024 * 1024
        backup_count = YAML_CONFIGS_INFO.get('log_config', {}).get('LOG_FILE_BACKUP_COUNT')
        format = YAML_CONFIGS_INFO.get('log_config', {}).get('LOG_FORMAT')

        # 创建日志器
        file_name = os.path.split(file_path)[1]
        logger = logging.getLogger(file_name)
        logger.setLevel(logging.DEBUG)  # 设置全局日志级别

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # 控制台仅记录 INFO 及以上级别

        # 文件处理器（自动轮换日志文件）
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)  # 文件记录所有 DEBUG 及以上级别

        # 定义日志格式
        formatter = logging.Formatter(
            # "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
            format
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # 将处理器添加到日志器
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger