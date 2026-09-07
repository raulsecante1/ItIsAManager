import mcp_server.config as mcfg

import abc
import numpy as np
import pydantic


class RerankResult(pydantic.BaseModel):
    score: float
    content: str


class BaseReranker(abc.ABC):

    """
    Contract for reranking documents based on relevance to query.

    Args:
        query: User query string.
        file_contents: List of file contents.
        top_k: Number of top files to return.

    Returns:
        List of (score, file_contents) tuples, sorted descending by score.
    """

    @abc.abstractmethod
    def rerank(self, query: str, file_contents: list[str]) -> list[RerankResult]:
        ...


class CEReranker(BaseReranker):

    def __init__(self):

        from sentence_transformers import CrossEncoder
        self.model = CrossEncoder("BAAI/bge-reranker-base", backend="onnx")

    def rerank(self, query: str, file_contents: list[str]) -> list[RerankResult]:

        pairs = [(query, file_content) for file_content in file_contents]
        scores = self.model.predict(pairs)
        unstructured_results = sorted(
            zip(scores, file_contents),
            key=lambda x: x[0],
            reverse=True,
        )
        structured_result = []
        for lft, rit in unstructured_results[:mcfg.TOP_K]:
            structured_result.append(RerankResult(score=lft, content=rit))

        return structured_result


class SBERTReranker(BaseReranker):

    def __init__(self):

        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer("all-MiniLM-L6-v2", backend="onnx")

    def rerank(self, query: str, file_contents: list[str]) -> list[RerankResult]:

        from sentence_transformers import util

        query_emb = self.model.encode(query, convert_to_tensor=True)
        doc_embs = self.model.encode(file_contents, convert_to_tensor=True)
        
        cos_vals = util.cos_sim(query_emb, doc_embs)[0].cpu().numpy()
        
        sorted_indices = np.argsort(cos_vals)[::-1][:mcfg.TOP_K]

        structured_result = []
        for idx in sorted_indices:
            structured_result.append(RerankResult(score=float(cos_vals[idx]), content=file_contents[idx]))

        return structured_result


class TrainedReranker(BaseReranker):
    pass


RERANKERS = {
    mcfg.RerankerType.SBERT: SBERTReranker,
    mcfg.RerankerType.CROSS_ENCODER: CEReranker,
    mcfg.RerankerType.TRAINED_MODEL: TrainedReranker,
}




def get_reranker(config: dict | None = None) -> BaseReranker:

    if config:
        reranker_type = config.get("type", "SBERT")
    else:
        reranker_type = mcfg.RERANKER.get("type", "SBERT")

    reranker_type = mcfg.RerankerType(str(reranker_type))
    
    try:
        return RERANKERS[reranker_type]()
    except KeyError:
        raise ValueError(f"Unknown reranker type: {reranker_type}")
    
