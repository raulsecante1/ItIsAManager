from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware

import itisamanager.config.settings as iset
import itisamanager.tools.agent_tools as iagt
import itisamanager.schema as isma

def create_main_agent():
    """
    create the main agent
    """
    return create_agent(
        model=iset.MAIN_AGENT_LLM, 
        tools=[iagt.write_article], 
        middleware=[
            iset.SUBAGENT_MIDDLEWARE, 
            iset.RUBRIC_MIDDLEWARE, 
            TodoListMiddleware(),
        ]
    )

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

    structured_llm = iset.MAIN_AGENT_MODEL.with_structured_output(isma.ArticleOutline)

    return structured_llm.invoke(outline_prompt)


def generate_article(outline: isma.ArticleOutline) -> isma.FinalDraft:
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

    content_str = iset.MAIN_AGENT_MODEL.invoke(article_prompt)
    
    return isma.FinalDraft(content=content_str, outline=outline)


def main_agent_flow(user_query: str):
    """
    the main agent workflow
    """
    main_agent = create_main_agent()
    state = main_agent.invoke({"messages": [{"role": "user", "content": user_query}]})
    
    knowledge_chunks = state.get("knowledge_chunks", [])
    
    if not knowledge_chunks:
        raise ValueError("No knowledge chunks extracted. Check file paths.")

    outline = synthesize_outline(knowledge_chunks)
    final_article = generate_article(outline)

    main_agent.invoke({
        "messages": [{"role": "user", "content": f"Write down the following article to disk{final_article.content}"}],
    })

    return f"Article written on {iset.ARTICLE_PATH}"
