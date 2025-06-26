import os
import importlib
from pathlib import Path
from typing import Iterator, Union

from langchain_community.document_loaders.parsers.language.language_parser import LANGUAGE_EXTENSIONS
from langchain_core.documents import Document
from langchain_community.document_loaders.parsers import LanguageParser

from common.error.load import UnLoadableError
from common.inspect.inpect_instance import InpectInstance

# Unstructured 需要设置环境变量, 防止下载 nlp 和 cv 包
os.environ["AUTO_DOWNLOAD_NLTK"] = "false"

class LoadDocument:

    def __init__(self, file_path: Union[str, Path], file_type: str, **kwargs):
        """

        :param file_path:
        :param file_type:
        :param kwargs: 各解析器拓展参数
        """
        self.__file_path: str = file_path
        self.__file_type: str = file_type
        self.__dir_type: list[str] = ['py_module']

        if os.path.isdir(self.__file_path) and not (self.__file_type in self.__dir_type):
            raise Exception(f'非 {self.__dir_type} 类型, file_path 不能为目录!!')

        # [todo] excel 解析格式要对齐csv
        self.__excel_loader: dict = {
            'module_path': 'langchain_community.document_loaders',
            'class_name': 'UnstructuredExcelLoader',
            'init_args': {
                'file_path': self.__file_path,
                'mode': 'elements',
                **kwargs
            }
        }
        self.__code_loader: dict = {
            'module_path': 'langchain_community.document_loaders.generic',
            'class_name': 'GenericLoader.from_filesystem',
            'init_args': {
                'path': self.__file_path,
                'parser': LanguageParser(),
                **kwargs
            }
        }
        self.__doc_loader: dict = {
            'module_path': 'langchain_community.document_loaders',
            'class_name': 'Docx2txtLoader',
            'init_args': {
                'file_path': self.__file_path,
                **kwargs
            }
        }
        self.__py_loader: dict = {
            'module_path': 'core.common.load_document.load_code.load_pycode',
            'class_name': 'LoadPyCode',
            'init_args': {
                'file_path': self.__file_path,
                **kwargs
            }
        }
        self.__text_loader: dict = {
            'module_path': 'langchain_community.document_loaders',
            'class_name': 'TextLoader',
            'init_args': {
                'file_path': self.__file_path,
                'encoding': 'utf-8',
                'autodetect_encoding': True,
                **kwargs
            }
        }

        self.__load_map: dict = {
            # [todo] excel 要单独封装
            # [todo] pdf 的图文能力之后要结合飞桨ocr和pymupdf实现
            # [todo] web 要支持多代理服务器, 防止被拦截
            'web': {
                'module_path': 'langchain_community.document_loaders',
                'class_name': 'RecursiveUrlLoader',
                'init_args': {
                    'url': self.__file_path,
                    **kwargs
                }
            },
            'pdf': {
                'module_path': 'langchain_community.document_loaders',
                'class_name': 'PyMuPDFLoader',
                'init_args': {
                    'file_path': self.__file_path,
                    **kwargs
                }
            },
            'csv': {
                'module_path': 'langchain_community.document_loaders.csv_loader',
                'class_name': 'CSVLoader',
                'init_args': {
                    'file_path': self.__file_path,
                    **kwargs
                }
            },
            'json': {
                'module_path': 'langchain_community.document_loaders',
                'class_name': 'JSONLoader',
                'init_args': {
                    'file_path': self.__file_path,
                    **kwargs
                }
            },
            **dict.fromkeys(['txt', 'yml', 'ipynb'], self.__text_loader),
            **dict.fromkeys(LANGUAGE_EXTENSIONS.keys(), self.__code_loader),
            **dict.fromkeys(['xlsx', 'xls'], self.__excel_loader),
            **dict.fromkeys(['doc', 'docx'], self.__doc_loader),
            **dict.fromkeys(['py_module'], self.__py_loader),
        }

        if not (self.__file_type in list(self.uploadable_type)):
            raise UnLoadableError(f'上传文件类型【{self.__file_type}】, 不属于可上传类型 【{"|".join(self.uploadable_type)}】')

        self.__load_instance = InpectInstance(module_map=self.__load_map, module_key=self.__file_type).load_instance


    @property
    def load_instance(self):
        return self.__load_instance

    @property
    def uploadable_type(self) -> list[str]:
        return list(self.__load_map.keys())

    def load(self) -> list[Document]:
        return list(self.lazy_load())

    def lazy_load(self) -> Iterator[Document]:
        lazy_result = self.__load_instance.lazy_load()
        return lazy_result