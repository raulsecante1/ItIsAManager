import pathlib
import tiktoken
import logging

import itisamanager.schema as isma
import itisamanager.tools.utils as iutl
import itisamanager.config.settings as iset
import itisamanager.agent.agent as iagt

logger = logging.getLogger(__name__)


def read_note(path: str) -> isma.KnowledgeChunks:
    """
    use this function to read a file with the give path and then generate varios KnowledgeChunk based on the file's content
    """

    logger.info(f"[read_note] Called with path: {path}")

    extractor = iset.EXTRACTION_LLM.with_structured_output(
        isma.KnowledgeChunks
    )

    file_content = iutl.read_file(path)

    encoder = tiktoken.get_encoding("cl100k_base") #calculate the token usage to decide if to batch or not

    estimate_tokens = len(encoder.encode(file_content.content))
    if estimate_tokens > iset.EXTRACTION_MODEL_TOKEN_LIMIT:
        chunks = iutl.chunking(file_content)

        batch_prompts = [
            f"""
            You are a knowledge extraction expert. 
            Read the following text chunk and extract exactly ONE KnowledgeChunk object per distinct concept.
            - 'title': A concise title for the concept.
            - 'key_terms': A string of 2-5 most relevant technical keywords, like 'key1, key2, key3'.
            - 'summary': A brief 1-2 sentence summary (max 100 words).

            Chunk index: {chunk.index}

            Content:
            {chunk.content}
            """
            for chunk in chunks
        ]

        try:
            preflatten_result = extractor.batch(
                batch_prompts,
                config={
                    "max_concurrency": 3
                }
            )

            flattened = [item for sublist in preflatten_result for item in sublist]
            result = isma.KnowledgeChunks(knowledge_chunk=flattened)

        except Exception as e:
            error_msg = str(e)
            if hasattr(e, "response") and e.response is not None:
                try:
                    # read the response
                    error_body = e.response.text
                    error_msg = f"{error_msg}\n response: {error_body}"
                except Exception as read_err:
                    error_msg = f"{error_msg}\n can't read the response: {read_err}"
            elif hasattr(e, "body"):
                error_msg = f"{error_msg}\n response: {e.body}"
            
            logger.error(f"calling LLM failed: {error_msg}")
            raise

    else:
        try:
            result = extractor.invoke(
                f"""
                You are a knowledge extraction expert.
                Read the following text chunk and extract exactly ONE KnowledgeChunk object per distinct concept.
                - 'title': A concise title for the concept.
                - 'key_terms': A string of 2-5 most relevant technical keywords, like 'key1, key2, key3'.
                - 'summary': A brief 1-2 sentence summary (max 100 words).
                
                Content:
                {file_content.content}
                """
            )
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, "response") and e.response is not None:
                try:
                    # read the response
                    error_body = e.response.text
                    error_msg = f"{error_msg}\n response: {error_body}"
                except Exception as read_err:
                    error_msg = f"{error_msg}\n can't read the response: {read_err}"
            elif hasattr(e, "body"):
                error_msg = f"{error_msg}\n response: {e.body}"
            
            logger.error(f"calling LLM failed: {error_msg}")
            raise

    logger.info(f"[read_note] Extracted {len(result.knowledge_chunk)} chunks")

    for chunk in result.knowledge_chunk:
        if not chunk.title or chunk.title.strip() == "":

            # take the first 3 words from summary if summary presents
            if chunk.summary:
                words = chunk.summary.split()[:3]
                chunk.title = " ".join(words) + "..."
            else:
                chunk.title = "Untitled"

    return result


def list_readable_files(directory_path: str) -> dict[str, list[str]]:
    """
    use this function to list all the readable files in the given directory path
    """

    files = {}

    path = pathlib.Path(directory_path)
    if not path.exists():
        raise FileNotFoundError(f"directory dose not exist: {directory_path}")
    if not path.is_dir():
        raise ValueError(f"path is not a directory use read_note() instead: {directory_path}")
    
    files["markdown_files"] = [str(p) for p in list(path.rglob("*.md"))]
    files["text_files"] = [str(p) for p in list(path.rglob("*.txt"))]

    return files    


def write_article(finalDraft: isma.FinalDraft):
    """
    use this function to write back the generated FinalDraft into disk
    """
    path = iutl.get_unique_path(pathlib.Path(iset.ARTICLE_PATH))

    path.write_text(
        finalDraft.content,
        encoding="utf-8",
    )

    logger.info(f"[write_article] File written")

    return "file written"


def synthesize_outline(all_chunks: list[isma.KnowledgeChunk]) -> isma.ArticleOutline:
    """
    generate a article outline and chapters from the knowledge chunks using LLM model not agent
    """

    all_content = ""
    for chunk in all_chunks:
        all_content += f"{chunk.title}: {chunk.summary}; key terms: {chunk.key_terms}\n"

    outline_prompt = f"""
    You are a knowledge synthesis expert.
    Read the following text chunks and synthesize the outline and chapter of all the chunks, where the outline object is:
    - 'title': A concise title for the outline.
    - 'chapters': A list of chapter objects.
    - 'overall_strategy': A single phrase that describe the overall logic (max 150 words).

    And the chapter object is like:
    - 'title': A concise title for one chapter.
    - 'key_points': A list of 2-5 most relevant technical keywords.

    Text chunks:
    {all_content}
    """

    structured_llm = iset.MAIN_AGENT_LLM.with_structured_output(isma.ArticleOutline)

    logger.info(f"[synthesize_outline] Synthesizing the outline")

    return structured_llm.invoke(outline_prompt)


def generate_article(outline: isma.ArticleOutline, feedback: str | None = None) -> isma.FinalDraft:
    """
    generate final draft of the article from the outline and the chapters using LLM model not agent
    """

    all_chapters = ""
    for chapter in outline.chapters:
        all_chapters += f"{chapter.title}: {chapter.key_points}; "
    article_prompt = f"""
    You are a knowledge article generation expert.
    Read the following outline and chapters then generate an article about their content, where the article has a format:
    - 'content': The content of the article

    The outline:
    {outline.title}: {outline.overall_strategy}

    The chapters:
    {all_chapters}
    """

    if feedback:
        article_prompt + f"\n\nThe feedback:\n{feedback}"

    content_str = iset.MAIN_AGENT_LLM.invoke(article_prompt)

    logger.info(f"[generate_article] Generated the article")
    
    return isma.FinalDraft(content=content_str.content, outline=outline)