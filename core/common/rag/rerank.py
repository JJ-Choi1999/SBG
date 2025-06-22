from typing import List, Optional

from xinference.client import Client
from xinference.client.restful.restful_client import RESTfulRerankModelHandle
from xinference.types import Rerank

class RerankClient:

    def __init__(self, base_url: str, model_uid: str):

        self.__base_url = base_url
        self.__model_uid = model_uid

        self.__client: Client = Client(base_url=self.__base_url)
        self.__model: RESTfulRerankModelHandle = self.__client.get_model(model_uid=self.__model_uid)

    def rerank(self,
        documents: List[str],
        query: str,
        top_n: Optional[int] = None,
        max_chunks_per_doc: Optional[int] = None,
        **kwargs
    ) -> Rerank:
        return self.__model.rerank(
            documents=documents,
            query=query,
            top_n=top_n,
            max_chunks_per_doc=max_chunks_per_doc,
            return_documents=True,
            return_len=True,
            **kwargs
        )

    def get_rerank_meta(self, rerank_result: Rerank) -> dict:
        return rerank_result.get('meta', {})