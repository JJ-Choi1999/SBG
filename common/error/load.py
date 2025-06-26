class UnLoadableError(Exception):
    def __init__(self, msg='不支持该类型上传'):
        super().__init__(msg)