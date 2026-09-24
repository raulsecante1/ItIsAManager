import benchmark.systems as bsys
import benchmark.config as bcfg
import benchmark.metrics.answer_accuracy as bmea

import logging
import json
import uuid

logger = logging.getLogger(__name__)


def main():
    path = bcfg.PROJECT_ROOT / "dataset/questions.jsonl"

    results_path = path.parent.parent / "results"

    with path.open("r", encoding="utf-8") as f:
        user_query_dicts = [json.loads(line) for line in f if line.strip()]

    user_query_dicts = [user_query_dicts[1]] # test, read line 2, delete this

    for user_query_dict in user_query_dicts:

        user_query = user_query_dict["user_query"]
        facts_dict_list = user_query_dict["key_facts"]
        facts_list = [the_dict["fact"] for the_dict in facts_dict_list]
    
        importance = [the_dict["importance"] for the_dict in facts_dict_list]

        #---
        
        text1_path = results_path / "base_llm_d4a3d68e.md"
        text1 = text1_path.read_text(encoding="utf-8")

        KIC_res1 = bmea.kic(text1, facts_list, importance)

        text2_path = results_path / "base_rag_d4a3d68e.md"
        text2 = text2_path.read_text(encoding="utf-8")

        KIC_res2 = bmea.kic(text2, facts_list, importance)

        text3_path = results_path / "mpkm_full_d4a3d68e.md"
        text3 = text3_path.read_text(encoding="utf-8")

        KIC_res3 = bmea.kic(text3, facts_list, importance)

        return (KIC_res1, KIC_res2, KIC_res3)
        
        #---

        file_id = uuid.uuid4().hex[:8]

        res_base_llm = bsys.base_llm.pure_llm_call(user_query)

        res_base_rag = bsys.base_rag.pure_llm_rag(user_query)

        res_mpkm_full = bsys.mpkm_full.mpkm_call(user_query)

        base_llm_path = results_path / f"base_llm_{file_id}.md"
        base_rag_path = results_path / f"base_rag_{file_id}.md"
        mpkm_full_path = results_path / f"mpkm_full_{file_id}.md"

        base_llm_path.write_text(
            res_base_llm.article,
            encoding="utf-8",
        )

        base_rag_path.write_text(
            res_base_rag.article,
            encoding="utf-8",
        )

        mpkm_full_path.write_text(
            res_mpkm_full.article,
            encoding="utf-8",
        )

        logger.info(f"File written")

        '''
        judger_query = f"""
        You are an expert article context quality judger.
        According to the given user query, judge which of the provided article has the best quality.
        User query:\n\n{user_query}\n
        Base llm's article:\n\n{res_base_llm.article}
        Base rag's article:\n\n{res_base_rag.article}
        MPKM's article:\n\n{res_mpkm_full.article}
        """

        judger_model = bcfg.JUDGER_LLM
        
        call_response = judger_model.invoke(judger_query)

        print(call_response.content)
        '''


if __name__ == "__main__":
    main()