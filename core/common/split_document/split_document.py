import importlib
from pathlib import Path
from typing import Iterator, Union, Iterable

from langchain_text_splitters import Language
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from common.inspect.inpect_instance import InpectInstance

class SplitDocument:

    def __init__(
        self,
        file_type: str = 'default',
        chunk_size: int = 200,
        chunk_overlap: int = 10,
        separators: list[str] = ['\n', ' '],
        **kwargs
    ):
        self.__file_type = file_type if file_type != 'py_module' else 'py'
        self.__chunk_size = chunk_size
        self.__chunk_overlap = chunk_overlap
        self.__separators = separators
        self.__kwargs = kwargs
        # print(f'self.__file_type:', self.__file_type)

        self.__default_spliter = {
            'module_path': 'langchain_text_splitters.character',
            'class_name': 'RecursiveCharacterTextSplitter',
            'init_args': {
                'separators': self.__separators,
                'chunk_size': self.__chunk_size,
                'chunk_overlap': self.__chunk_overlap,
                **self.__kwargs
            }
        }

        self.__code_spliter = {
            'module_path': 'langchain_text_splitters.character',
            'class_name': 'RecursiveCharacterTextSplitter',
            'init_args': {
                'separators': RecursiveCharacterTextSplitter.get_separators_for_language(
                    Language(Language._value2member_map_.get(self.__file_type))
                ) if Language._value2member_map_.get(self.__file_type) else None,
                'chunk_size': self.__chunk_size,
                'chunk_overlap': self.__chunk_overlap,
                **self.__kwargs
            }
        }

        self.__split_map = {
            'json': {
                'module_path': 'langchain_text_splitters.json',
                'class_name': 'RecursiveJsonSplitter',
                'init_args': {
                    'max_chunk_size': self.__chunk_size,
                    'min_chunk_size': self.__kwargs.pop('min_chunk_size') if 'min_chunk_size' in self.__kwargs.keys() else None,
                    **self.__kwargs
                }
            },
            'md': {
                'module_path': 'langchain_text_splitters.markdown',
                'class_name': 'MarkdownTextSplitter',
                'init_args': {
                    'chunk_size': self.__chunk_size,
                    'chunk_overlap': self.__chunk_overlap,
                    **self.__kwargs
                }
            },
            'default': self.__default_spliter,
            **dict.fromkeys(list(Language._value2member_map_.keys()), self.__code_spliter),
        }

        # 找不到对应文件的分割策略的话, 就使用默认分割策略
        if not self.__split_map.get(self.__file_type): self.__split_map[self.__file_type] = self.__default_spliter

        self.__split_instance = InpectInstance(module_map=self.__split_map, module_key=self.__file_type).load_instance

    @property
    def split_instance(self):
        return self.__split_instance

    @property
    def splittable_type(self) -> list[str]:
        return list(self.__split_map.keys())

    def split_documents(self, documents: Union[str, Path, Iterable[Document]]) -> list[Document]:
        if self.__file_type == 'json':
            with open(documents, 'r') as f:
                split_json_texts = self.__split_instance.split_json(json_data=f.read())
                return self.__split_instance.create_documents(texts=split_json_texts)

        return self.__split_instance.split_documents(documents=documents)