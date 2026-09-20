import benchmark.systems as bsys
import benchmark.config as bcfg


def main():
    user_query = f"""
    You are an expert article generation agent.
    Now i need you to read the files then generate an article about how to use EU4 console command build a strong country
    """

    res_base_llm = bsys.base_llm.pure_llm_call(user_query)
    res_base_rag = bsys.base_rag.pure_llm_rag(user_query)
    res_mpkm_full = bsys.mpkm_full.mpkm_call(user_query)

    judger_query = f"""
    You are an expert article context quality judage.
    According to the given user query, judge which of the provided article has the best quality.
    User query:\n\n{user_query}\n
    Base llm's article:\n\n{res_base_llm.article}
    Base rag's article:\n\n{res_base_rag.article}
    MPKM's article:\n\n{res_mpkm_full.article}
    """

    judger_model = bcfg.JUDGER_LLM
    
    call_response = judger_model.invoke(judger_query)

    print(call_response.content)


if __name__ == "__main__":
    main()