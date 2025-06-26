class GlobalSettingError(Exception):
    def __init__(self, msg='输入类型不为 Y/N'):
        super().__init__(msg)

class SelectModeError(Exception):
    def __init__(self, msg='选择模式不存在'):
        super().__init__(msg)