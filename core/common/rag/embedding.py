from typing import Union, List

from xinference.client import Client
from xinference.client.restful.restful_client import RESTfulEmbeddingModelHandle
from xinference.types import Embedding

from langchain_community.embeddings import XinferenceEmbeddings

class EmbeddingClient:

    def __init__(self, base_url: str, model_uid: str):
        self.__base_url = base_url
        self.__model_uid = model_uid

        self.__xinference_embeddings = XinferenceEmbeddings(server_url=self.__base_url, model_uid=self.__model_uid)
        self.__client: Client = self.__xinference_embeddings.client
        self.__model: RESTfulEmbeddingModelHandle = self.__client.get_model(model_uid=self.__model_uid)

    @property
    def xinference_embeddings(self) -> XinferenceEmbeddings:
        return self.__xinference_embeddings

    def create_embedding(self, input: Union[str, List[str]], **kwargs) -> "Embedding":
        return self.__model.create_embedding(input=input, **kwargs)

    def get_embedding(self, embedding_result: Embedding) -> list:
        embedding_datas = embedding_result.get('data', [])
        if not embedding_datas: return []

        embedding_data = embedding_datas[-1]
        embedding = embedding_data.get('embedding', [])

        return embedding

    def get_usage(self, embedding_result: Embedding) -> dict:
        return embedding_result.get('usage', {})