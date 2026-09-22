import logging
import pydantic

import benchmark.config as bcfg

logger = logging.getLogger(__name__)


class KICJudgerOutput(pydantic.BaseModel):

    coverage: dict[int,int]


def kic(article: str, facts_list: list[str], importance: list[float]) -> float: # key information coverage

    judger_model = bcfg.JUDGER_LLM.with_structured_output(KICJudgerOutput)

    indexed_facts_dict = {a: b for a, b in enumerate(facts_list)}

    judger_query = f"""
    You are an expert article context quality judger.
    According to the given article, judge if the following facts are presented in the article.
    The output should be a dict of fact_id with an integer: As long as the article explicitly contains this information (semantic equivalence is sufficient; an exact wording match is not required), it is classified as 1. If the article only mentions a related concept but does not provide specific information, it is classified as 0.
    article:\n\n{article}
    facts:\n\n{indexed_facts_dict}
    """

    call_response = judger_model.invoke(judger_query)
    coverage = call_response.coverage

    if set(coverage.keys()) != set(range(len(facts_list))):
        raise ValueError(f"LLM returned mismatched keys: {coverage.keys()}; fact_list: {range(len(facts_list))}")
    if sum(importance) == 0:
        raise ValueError("The importance values sum to zero")

    coverage_values = [coverage[i] for i in range(len(facts_list))]

    return sum([a*b for a, b in zip(importance, coverage_values)])/sum(importance)