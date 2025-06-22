class EdgeMapsError(Exception):
    def __init__(self, msg='边映射为空或只有一个节点'):
        super().__init__(msg)

class EdgeFuncHasError(Exception):
    def __init__(self, msg='不存在边映射方法'):
        super().__init__(msg)
