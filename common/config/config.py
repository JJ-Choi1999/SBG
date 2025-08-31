import os
import yaml

class Config:

    __project_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    __configs_path = os.path.join(__project_path, 'configs')

    __yaml_configs_info = {}

    def __new__(cls, *args, **kwargs):

        if cls.__yaml_configs_info:
            return cls.__yaml_configs_info
        else:
            for filename in os.listdir(cls.__configs_path):
                file_path = os.path.join(cls.__configs_path, filename)
                if not os.path.isfile(file_path): continue

                yaml_name = os.path.split(file_path)[1].replace('.yaml', '')
                cls.__yaml_configs_info[yaml_name] = {}
                with open(file_path, 'r', encoding='utf-8') as f:
                    __config = yaml.safe_load(f)  # 安全加载方法
                    cls.__yaml_configs_info[yaml_name] = __config if __config else {}

            return cls.__yaml_configs_info
