class ExtraTagError(Exception):
    def __init__(self, msg='提取标签内容异常'):
        super().__init__(msg)