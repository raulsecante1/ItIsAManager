from pathlib import Path
import tiktoken
import typing

from langchain.tools import tool

import itisamanager.schema as isma
import itisamanager.tools.utils as iutl
import itisamanager.config.settings as iset

@tool
def read_note(path: str) -> typing.List[isma.KnowledgeChunk]:
    """
    use this function to read a file and then generate varios KnowledgeChunk based on the file's content
    """

    extractor = iset.EXTRACTION_LLM.with_structured_output(
        typing.List[isma.KnowledgeChunk]
    )

    file_content = iutl.read_file(path)

    encoder = tiktoken.get_encoding("cl100k_base")

    estimate_tokens = len(encoder.encode(file_content.content))
    if estimate_tokens > iset.EXTRACTION_MODEL_TOKEN_LIMIT:
        chunks = iutl.chunking(file_content)

        batch_prompts = [
            f"""
            You are a knowledge extraction expert. 
            Read the following text chunk and extract exactly ONE KnowledgeChunk object per distinct concept.
            - 'title': A concise title for the concept.
            - 'key_terms': A list of 2-5 most relevant technical keywords.
            - 'summary': A brief 1-2 sentence summary (max 100 words).

            Chunk index: {chunk.index}

            Content:
            {chunk.content}
            """
            for chunk in chunks
        ]

        preflatten_result = extractor.batch(
            batch_prompts,
            config={
                "max_concurrency": 3
            }
        )

        result = [b for a in preflatten_result for b in a]

    else:
        result = extractor.invoke(
            f"""
            You are a knowledge extraction expert.
            Read the following text chunk and extract exactly ONE KnowledgeChunk object per distinct concept.
            - 'title': A concise title for the concept.
            - 'key_terms': A list of 2-5 most relevant technical keywords.
            - 'summary': A brief 1-2 sentence summary (max 100 words).
            
            Content:
            {file_content.content}
            """
        )

    return result


@tool
def write_article(finalDraft: isma.FinalDraft):
    """
    use this function to write back the generated FinalDraft into disk
    """
    path = Path(iset.ARTICLE_PATH)

    path.write_text(
        finalDraft.content,
        encoding="utf-8",
    )