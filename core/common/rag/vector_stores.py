from pathlib import Path
from typing import Optional, Dict, Union, List

import weaviate
from langchain_community.embeddings import XinferenceEmbeddings
from langchain_core.documents import Document
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthCredentials
from weaviate.collections.classes.filters import _Filters
from weaviate.collections.collections.sync import _Collections
from weaviate.config import AdditionalConfig
from weaviate.classes.query import Filter

from core.common.format_result.format_result import vector_results, transform_rerank_texts, transform_rerank_results
from core.common.rag.rerank import RerankClient
from core.common.load_document.load_document import LoadDocument
from core.common.split_document.split_document import SplitDocument

class WeaviateClient:

    def __init__(
        self,
        embedding_client: XinferenceEmbeddings = None,
        rerank_client: RerankClient = None,
        host: str = "localhost",
        port: int = 8080,
        grpc_port: int = 50051,
        headers: Optional[Dict[str, str]] = None,
        additional_config: Optional[AdditionalConfig] = None,
        skip_init_checks: bool = False,
        auth_credentials: Optional[AuthCredentials] = None,
    ):
        """

        :param embedding_client: # [todo] 之后改为配置文件设置是否开启, 动态导入对应依赖和调用方法
        :param rerank_client: # [todo] 之后改为配置文件设置是否开启, 动态导入对应依赖和调用方法
        :param host: # [todo] 要改为配置读取
        :param port: # [todo] 要改为配置读取
        :param grpc_port: # [todo] 要改为配置读取
        :param headers:
        :param additional_config:
        :param skip_init_checks:
        :param auth_credentials:
        """
        self.__rerank_client = rerank_client
        self.__embedding_client = embedding_client
        self.__db: WeaviateVectorStore | None = None
        self.__dbs: list[WeaviateVectorStore] = []
        self.__client = weaviate.connect_to_local(
            host=host,
            port=port,
            grpc_port=grpc_port,
            headers=headers,
            additional_config=additional_config,
            skip_init_checks=skip_init_checks,
            auth_credentials=auth_credentials
        )

    @property
    def client(self):
        return self.__client

    @property
    def collections(self) -> _Collections:
        return self.__client.collections

    @property
    def collection_keys(self) -> list:
        return list(self.__client.collections.list_all().keys())

    def load_file(
        self,
        file_path: Union[str, Path],
        file_type: str,
        chunk_size: int = 200,
        chunk_overlap: int = 10,
        separators: list = ['\n', ' ']
    ):
        loader = LoadDocument(
            file_path=file_path,
            file_type=file_type
        )
        docs = loader.load()
        spliter = SplitDocument(file_type=file_type, chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=separators)
        split_docs = spliter.split_documents(docs)

        return split_docs

    def init_vector(
        self,
        split_docs: List[Document],
        uuids: list[str] = [],
        index_name: str | None = None,
        tenant: str | None = None,
        **kwargs
    ):
        """
        初始化写入向量库
        :param split_docs: 切片数据
        :param uuids: 切片对应的uuid列表, 存在该值时, 第一次是插入之后按照uuid 匹配更新; 没有该值每次都是新增
        :param index_name: 索引名, 不同名会新建索引
        :param tenant: 租户名
        :return:
        """
        if uuids: kwargs['uuids'] = uuids

        self.__db = WeaviateVectorStore.from_documents(
            split_docs,
            embedding=self.__embedding_client,
            client=self.__client,
            index_name=index_name,
            tenant=tenant,
            **kwargs
        )
        self.__dbs.append(self.__db)

        return self.__db

    # [todo] 以后需要统一wrap验证
    # [todo] 该结果之后用 pydantic 表示, 并封装对应输出格式的方法
    def search(
        self,
        query: str,
        alpha = 0.75,
        k: int = 5,
        rerank_topn: int = 5,
        is_rerank: bool = False,
        filter: _Filters | None = None,
        tenant: str | None = None,
    ) -> list[dict]:
        """
        查询向量数据库数据, 返回可信度最高的 k 个结果
        :param query: 需要查询的问题
        :param alpha: 向量和关键字比重, 范围: [0,1], 1 表示完全使用向量, 默认值 0.75
        :param k: 需要返回的结果个数
        :param rerank_topn: rerank 需要返回的结果个数
        :param is_rerank: 查询结果是否再次使用 rerank 结果
        :param filter: weaviate 过滤表达式
        :return:
        """
        if not self.__db:
            raise Exception('Weaviate 向量数据库未加载向量!!')

        # similarity_search_with_score 返回的结果分数越小可信度越高
        docs = self.__db.similarity_search_with_score(query, alpha=alpha, k=k, filters=filter, tenant=tenant)
        search_results = vector_results(docs)

        if is_rerank and self.__rerank_client:
            search_results = transform_rerank_results(self.rerank(query=query, vector_results=search_results, top_n=rerank_topn))

        return search_results

    def rerank(self, query: str, vector_results: list[dict], top_n: int = 5) -> list[dict]:
        if not self.__rerank_client: return vector_results
        rerank_texts = transform_rerank_texts(vector_results)
        return self.__rerank_client.rerank(rerank_texts, query, top_n=top_n).get('results', [])

    def delete_collection(self, collection_name: str):
        self.__client.collections.delete(collection_name)

    def clear_collections(self):
        self.__client.collections.delete_all()

    def all_collections(self) -> list:
        return list(self.__client.collections.list_all().keys())

    def close(self):
        """
        关闭 weaviate 连接防止内存溢出
        :return:
        """
        self.__client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()