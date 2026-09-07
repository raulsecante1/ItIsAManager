import mcp_server.config as mcfg

import abc

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
    def rerank(self, query: str, file_contents: list[str]) -> list[tuple[float, str]]:
        ...


class CEReranker(BaseReranker):

    def __init__(self):

        from sentence_transformers import CrossEncoder
        self.model = CrossEncoder("BAAI/bge-reranker-base")

    def rerank(self, query: str, file_contents: list[str]) -> list[tuple[float, str]]:

        pairs = [(query, file_content) for file_content in file_contents]
        scores = self.model.predict(pairs)
        results = sorted(
            zip(scores, file_contents),
            key=lambda x: x[0],
            reverse=True,
        )
        return results[:(mcfg.TOP_K)]


class SBERTReranker(BaseReranker):

    def __init__(self):

        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def rerank(self, query: str, file_contents: list[str]) -> list[tuple[float, str]]:

        pairs = [(query, file_content) for file_content in file_contents]
        scores = self.model.predict(pairs)
        results = sorted(
            zip(scores, file_contents),
            key=lambda x: x[0],
            reverse=True,
        )
        return results[:(mcfg.TOP_K)]


class MLPReranker(BaseReranker):
    pass



def get_reranker(config: dict) -> BaseReranker:

    model_type = mcfg.MODLE.get("type", "dummy")
    if model_type == "CrossEncoder":
        return CEReranker()
