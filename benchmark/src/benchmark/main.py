import benchmark.systems as bsys
import benchmark.config as bcfg

import logging
import json
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)


def main():
    path = Path("../dataset/questions.jsonl")

    results_path = path.parent.parent / "results"

    with path.open("r", encoding="utf-8") as f:
        user_querys = [json.loads(line) for line in f]

    for user_query in user_querys:

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

        logger.info(f"[write_article] File written")

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


if __name__ == "__main__":
    main()