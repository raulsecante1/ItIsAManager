import logging
import time
import pathlib
import tiktoken

import src.itisamanager.tools.agent_tools as sita
import src.itisamanager.config.settings as sics
import benchmark.systems.schema as bsma

logger = logging.getLogger(__name__)

encoder = tiktoken.get_encoding("cl100k_base")


def direct_invoke(full_text: str, user_query: str) -> bsma.SystemOutput:

    prompt = [
        {
            "role": "system",
            "content": (
                "You are an expert article generation agent."
                "You need to generate an article according to user's instructions."
                "Also you haven been provided relative informations\n\n"
                f"{full_text}"
            )
        },
        {
            "role": "user",
            "content": f"{user_query}"
        }
    ]

    llm_model = sita.MAIN_AGENT_LLM

    start = time.perf_counter()
    call_response = llm_model.invoke(prompt)
    elapsed  = time.perf_counter() - start

    structured_result = bsma.SystemOutput(
        article=call_response.content,
        latency=elapsed,
        token_usage=call_response.usage_metadata.get("total_tokens", 0)
    )

    return structured_result


def one_term_greedy(size_content_pair, user_query: str) -> bsma.SystemOutput:

    aux_size = 0
    info_to_send = []

    capcity = sics.MAIN_AGENT_MODELL_TOKEN_LIMIT

    for doc, tokens in size_content_pair:
        if tokens > capcity:
            logger.info("Caught file that exceeds the context window, bypassing it under this policy")
            continue

        if aux_size + tokens + 1 <= capcity:
            info_to_send.append(doc)
            aux_size = aux_size + tokens + 1 # \n\n takes 1 token

    full_text = "\n\n".join(info_to_send)

    return direct_invoke(full_text, user_query)


def map_reduce(size_content_pair, user_query: str) -> bsma.SystemOutput:

    aux_size = 0
    info_to_send = []

    capcity = sics.MAIN_AGENT_MODELL_TOKEN_LIMIT

    batch = []

    for doc, tokens in size_content_pair:

        if tokens > capcity:
            if info_to_send != []:
                batch.append("\n\n---\n\n".join(info_to_send))
                aux_size = 0
                info_to_send = []

            token_list = encoder.encode(doc)

            for i in range(0, tokens, capcity):
                
                batch.append(encoder.decode(token_list[i:i + capcity]))

            continue

        if aux_size + tokens + 3 <= capcity:
            info_to_send.append(doc)
            aux_size = aux_size + tokens
        else:
            batch.append("\n\n---\n\n".join(info_to_send))
            aux_size = tokens
            info_to_send = [doc]
    if info_to_send: batch.append("\n\n---\n\n".join(info_to_send))

    try:
        synthesized_size = capcity // len(batch)
    except ZeroDivisionError:
        raise ValueError("No valid batches could be created; all files may be too large to fit the context window")

    batch_prompts = [
        [
            {
                "role": "system",
                "content": (
                    "You are an expert research assistant.\n"
                    "Your task is to analyze the provided information "
                    "in relation to the user's request.\n"
                    "Extract all information that may be relevant to "
                    "answering the user's request.\n"
                    f"Do not exceeds the output limit of {synthesized_size} tokens"
                    "Do not write the final article.\n"
                    "Do not invent information that is not supported "
                    "by the provided content.\n\n"
                    "Provided information:\n\n"
                    f"{batch_text}"
                )
            },
            {
                "role": "user",
                "content": user_query
            }
        ]
        for batch_text in batch
    ]

    llm_model = sita.MAIN_AGENT_LLM

    start = time.perf_counter()
    preflatten_response = llm_model.batch(
        batch_prompts,
        config={
            "max_concurrency": 3
        }
    )

    result = [a.content for a in preflatten_response]
    batch_token_usage = [a.usage_metadata.get("total_tokens", 0) for a in preflatten_response]

    full_synthesized_text = "\n\n".join(result)

    full_synthesized_text_size = len(encoder.encode(full_synthesized_text)) # llm will make mistakes

    if full_synthesized_text_size > capcity:
        final_result = one_term_greedy(full_synthesized_text, user_query)
    else:
        final_result = direct_invoke(full_synthesized_text, user_query)

    elapsed  = time.perf_counter() - start

    structured_result = bsma.SystemOutput(
        article = final_result.article,
        latency = elapsed,
        token_usage = sum(batch_token_usage) + final_result.token_usage
    )

    return structured_result


def pure_llm_rag(user_query: str) -> bsma.SystemOutput:

    folder = pathlib.Path(sics.PROJECT_ROOT/ "documents")

    retrived_infos = [
        file.read_text(encoding="utf-8")
        for file in folder.rglob("*.md")
        if file.is_file()
    ] + [
        file.read_text(encoding="utf-8")
        for file in folder.rglob("*.txt")
        if file.is_file()       
    ]

    estimate_tokens = []
    size_content_pair = [] # just in case we store the pair

    for info in retrived_infos:
        size = len(encoder.encode(info))
        estimate_tokens.append(size)
        size_content_pair.append((info, size))

    full_text = "\n\n".join(retrived_infos)

    total_size = sum(estimate_tokens)

    if total_size < sics.MAIN_AGENT_MODELL_TOKEN_LIMIT:
        return direct_invoke(full_text, user_query)
    elif total_size < sics.MAIN_AGENT_MODELL_TOKEN_LIMIT*2:
        return one_term_greedy(size_content_pair, user_query)
    else:
        return map_reduce(size_content_pair, user_query)