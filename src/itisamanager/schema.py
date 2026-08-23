import pydantic

class Document(pydantic.BaseModel):
    """
    Contents read from files by itisamanager.tools.read_files
    """
    content: str
    source: str

class ChunkText(pydantic.BaseModel):
    """
    chunks of the extracted Document
    """
    content: str
    source: str
    index: int

class KnowledgeChunk (pydantic.BaseModel):
    """
    knowledge fragments retrived from the document
    """

    title: str
    key_terms: str
    summary: str = pydantic.Field(min_length=1, max_length=700) # by avenge 5-6 char = 1 words, so plus 1 ' ', 6-7 chars

class KnowledgeChunks (pydantic.BaseModel):
    """
    knowledge chunk lists to avoid the typeError
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
    overall_strategy: str = pydantic.Field(min_length=1, max_length=350)

class FinalDraft (pydantic.BaseModel):
    """
    the final output
    """

    content: str
    outline: ArticleOutline


