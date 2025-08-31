import os
import yaml

__PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
__CONFIGS_PATH = os.path.join(__PROJECT_PATH, 'configs')
YAML_CONFIGS_INFO = {}

for filename in os.listdir(__CONFIGS_PATH):
    file_path = os.path.join(__CONFIGS_PATH, filename)
    if not os.path.isfile(file_path): continue

    yaml_name = os.path.split(file_path)[1].replace('.yaml', '')
    YAML_CONFIGS_INFO[yaml_name] = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        __config = yaml.safe_load(f)  # 安全加载方法
        YAML_CONFIGS_INFO[yaml_name] = __config if __config else {}