import importlib


class InpectInstance:

    def __init__(self, module_map: dict[str, dict], module_key: str):

        self.__module_map = module_map
        self.__module_key = module_key

        # [todo] 这三个要加上验证
        __module_path = self.__module_map.get(self.__module_key, {}).get('module_path', '')
        __class_name = self.__module_map.get(self.__module_key, {}).get('class_name', '')
        __init_args = self.__module_map.get(self.__module_key, {}).get('init_args', {})

        self.__load_module = importlib.import_module(__module_path)
        __class_names = __class_name.split('.')
        for index, cls_name in enumerate(__class_names):
            if index == 0:
                self.__load_cls = getattr(self.__load_module, cls_name)
            else:
                self.__load_cls = getattr(self.__load_cls, cls_name)

        self.__load_instance = self.__load_cls(**__init_args)

    @property
    def load_instance(self):
        return self.__load_instance

    @property
    def module_map(self):
        return self.__module_map