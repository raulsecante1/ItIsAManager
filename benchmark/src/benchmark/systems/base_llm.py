import logging
import time

import itisamanager.config.settings as sics
import benchmark.systems.schema as bsma

logger = logging.getLogger(__name__)


def pure_llm_call(user_query: str) -> bsma.SystemOutput:

    llm_model = sics.MAIN_AGENT_LLM

    prompt = [
        {
            "role": "system",
            "content": (
                "You are an expert article generation agent."
                "You need to generate an article according to user's instructions."
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

