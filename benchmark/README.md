# Benchmark

## What it is?

The project's associated benchmark framework along with some simple test sets

### What it measures

Three systems are evaluated side by side:

| System | Description |
| --- | --- |
| `base_llm` | Directly calls the LLM with no document retrieval |
| `base_rag` | Reads all documents and passes them to the LLM (no reranking, no agents) |
| `mpkm_full` | The full MPKM pipeline (Investigator → Synthesizer → Generator → Reviewer) |

The primary metric is **KIC (Key Information Coverage)** — the weighted fraction of predefined key facts that appear in the generated article.

## How to use?

Prerequisites:

- The MCP server must be running (`cd mcp-server && uv run mcp_server`)
- Environment variables for the LLM provider must be set (see `src/itisamanager/config/settings.py`)

Run `uv run benchmark` if you have `uv` installed, otherwise go to `src/benchmark` and run `python main.py`

## Sub project structure
```
benchmark/
├── dataset/
│   └── questions.jsonl                  # questions + reference answers + key_facts
│                                        #
├── src/benchmark/                       #
│   ├── systems/                         #
│   │   ├── schema.py                    # output schema
│   │   ├── base_llm.py                  # control group 1 directly calling LLM
│   │   ├── base_rag.py                  # control group 2 RAG without using reranker
│   │   └── mpkm_full.py                 # 
│   ├── main.py                          # main entrance
│   ├── metrics/                         #
│   │   ├── answer_accuracy.py           #
│   │   └── hallucination.py             #
│   └── config.py                        #
│                                        #
└── results                              # results of the historical benchmark tests
```

## Dataset format

Each line in `dataset/questions.jsonl` is a self-contained test case:

```json
{
  "id": "question_00001",
  "user_query": "...",
  "category": "how_to | cross_doc_synthesis | ...",
  "difficulty": "T1",
  "reference_answer": "...",
  "key_facts": [
    {"fact_id": "fact_001", "fact": "...", "importance": 1.0}
  ]
}
```


