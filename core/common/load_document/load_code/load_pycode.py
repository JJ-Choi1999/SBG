import os.path
from pathlib import Path
from typing import Union, Iterator

from common.file.file import iter_file_infos, py_module_adap
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_core.documents import Document

class LoadPyCode:

    def __init__(self, file_path: Union[str, Path], **kwargs):
        """
        输入文件/文件夹地址, 将所有文件后缀名为 .py 的文件, 上传返回为 list[Document] 对象
        :param file_path: 文件/文件夹地址
        """
        self.__filter_suffix: list[str] = ['py']
        self.__py_files: list[dict[str, Union[str, Path]]] = list(
            iter_file_infos(
                file_path=file_path,
                filter_suffix=self.__filter_suffix
            )
        )
        self.__load_modules: list[dict[str, str]] = []
        self.__kwargs = kwargs

    def lazy_load_modules(self) -> Iterator[dict[str, str]]:
        """
        [懒加载]加载python文件对应的module导入列表,
        输入 python 文件列表, 迭代输出对应 python 代码被其它 python 文件调用的 module 路径列表
        :return: python文件module调度地址
        """
        for py_file in self.__py_files:
            py_path = py_file.get('file_path', '')
            yield py_module_adap(py_path=py_path)

    def load_modules(self) -> list[dict[str, str]]:
        """
        加载python文件对应的module导入列表,
        输入 python 文件列表, 迭代输出对应 python 代码被其它 python 文件调用的 module 路径列表
        :return: python文件module调度地址
        """
        self.__load_modules = list(self.lazy_load_modules())
        return self.__load_modules

    def lazy_load(self) -> Iterator[Document]:

        py_modules = self.lazy_load_modules()
        for py_module in py_modules:
            py_path = py_module.get('py_path', '')
            module = py_module.get('module', '')

            lazy_gen_loader = GenericLoader.from_filesystem(
                path=py_path,
                parser=LanguageParser(),
                **self.__kwargs
            ).lazy_load()

            for gen_load_item in lazy_gen_loader:
                lazy_load_obj = gen_load_item
                lazy_load_obj.metadata = {
                    'py_module': module,
                    **lazy_load_obj.metadata
                }
                yield lazy_load_obj

    def load(self) -> list[Document]:
        return list(self.lazy_load())