import logging
import time

import src.itisamanager.tools.agent_tools as sita
import benchmark.systems.schema as bsma



def pure_llm_rag(user_query: str) -> bsma.SystemOutput:

    llm_model = sita.MAIN_AGENT_LLM

    retrived_info = []

    prompt = [
        {
            "role": "system",
            "content": (
                "You are an expert article generation agent."
                "You need to generate an article according to user's instructions."
                "Also you haven been provided relative informations\n\n"
                f"{retrived_info}"
            )
        },
        {
            "role": "user",
            "content": f"{user_query}"
        }
    ]

    start = time.perf_counter()
    call_response = llm_model.invoke(prompt)
    elapsed  = time.perf_counter() - start

    structured_result = bsma.SystemOutput(
        article=call_response.content,
        latency=elapsed,
        token_usage=call_response.usage_metadata.get("total_tokens", 0)
    )

    return structured_result