# Benchmark

## What it is?

The project's associated benchmark framework along with some simple test sets

## How to use?

Run `uv run benchmark` if you have `uv` installed, otherwise go to `src/benchmark` and run `python main.py`

## Sub project structure
```
benchmark/
├── dataset/
│   ├── questions.jsonl                  # example test sets
│   └── gold_answers.jsonl               # answers
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
└── results                              #
```



