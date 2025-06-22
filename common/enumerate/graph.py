from enum import EnumType

class ActionState(EnumType):
    SUCCESS: str = 'success'
    FAIL: str = 'fail'
    VERIFY: str = 'verify'