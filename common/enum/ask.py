from enum import EnumType

class Ask(EnumType):
    STREAM: str = "stream"
    INVOKE: str = "invoke"
    ASTREAM: str = "astream"
    AINVOKE: str = "ainvoke"