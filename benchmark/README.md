# Benchmark

## What it is ?

The project's associated benchmark framework along with some simple test sets

## Sub project structure
```
benchmark/
├── dataset/
│   ├── questions.jsonl          # example test sets
│   └── gold_answers.jsonl       # answers
│                                #
├── systems/                     #
│   ├── schema.py                # output schema
│   ├── base_llm.py              # control group 1 directly calling LLM
│   ├── base_rag.py              # control group 2 RAG without using reranker
│   └── mpkm_full.py             # 
│                                #
├── metrics/                     #
│   ├── answer_accuracy.py       #
│   └── hallucination.py         #
│                                #
├── main.py                      # main entrance
├── results                      #
└── config.py                    #
```



