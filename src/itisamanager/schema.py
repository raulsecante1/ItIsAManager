import pydantic

class ChunkText(pydantic.BaseModel):
    """
    chunks of the extracted Document
    """
    content: str
    index: int


class KnowledgeChunk (pydantic.BaseModel):
    """
    knowledge fragments retrived from the document
    """

    title: str
    key_terms: str
    summary: str = pydantic.Field(min_length=1, max_length=750) # by avenge 5-6 char = 1 words, so plus 1 ' ', 6-7 chars, plus 50 as insurance


class KnowledgeChunks (pydantic.BaseModel):
    """
    knowledge chunk lists to avoid the typeError in agent_tool.read_note()
    """

    knowledge_chunk: list[KnowledgeChunk]


class Chapter (pydantic.BaseModel):
    """
    chapter blueprints served for building the article outline
    """

    title: str
    key_points: list[str]


class ArticleOutline (pydantic.BaseModel):
    """
    skeleton of the article
    """

    title: str
    chapters: list[Chapter]
    overall_strategy: str = pydantic.Field(min_length=1, max_length=1050)


class FinalDraft (pydantic.BaseModel):
    """
    the final output
    """

    content: str
    outline: ArticleOutline


class Rubric (pydantic.BaseModel):
    """
    ouput class for rubric
    """

    score: int = pydantic.Field(ge=0, le=10)
    feedback: str = pydantic.Field(min_length=1, max_length=2100)
