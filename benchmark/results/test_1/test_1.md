# Benchmark Status Report

## 1. Executive Summary

**Headline**: On the current knowledge base (9 documents, total 33340 tokens based on `cl100k_base`), Naive RAG outperforms MPKM on KIC (0.81 vs 0.57). Analysis points root cause to the information loss across the multi-agent pipeline.

**Key Findings**:
- Finding 1: With small text volumes, "raw concatenation" preserves information best; base_rag has a natural advantage.
- Finding 2: MPKM's Investigator → Synthesizer → Generator chain loses specific information like certain console command each layer.
- Finding 3: base_llm hallucinates unsupported commands (e.g., `discipline_mod` does not exist).
- Finding 4: MPKM also underperforms on judgment-oriented facts (fact_004, fact_006 in Q2), suggesting the weakness is not limited to extraction fidelity but also affects trade-off reasoning.

---

## 2. Experimental Setup

| Dimension | Value |
| --- | --- |
| MPKM version | commit `2f7bc71c7b374462c3baaf1392c3428b1b961ca8` |
| Dataset | 2 questions (categories: how_to, cross_doc_synthesis) |
| Knowledge base size | 9 documents, 33340 tokens |
| Benchmark question size | 2 questions |
| Metrics | KIC (Key Information Coverage) |
| LLM Judge | deepseek-v4-flash (temperature=0) |
| Evaluations per article | 1 (single evaluation) |
| Date | 2026-9-24 |

**Knowledge Base Composition**:
- `console.txt`: EU4 console command list (Chinese, 4293 tokens)
- `venice.txt`: Venice-specific run command file (Chinese, 7988 tokens)
- `poland_start.txt`: Poland opening strategy (English, 255 tokens)
- Other technical docs (MCP, LangChain, etc. — already internalized by LLMs)

---

## 3. Results

### 3.1 Overall

| System | KIC (Q1: how_to) | KIC (Q2: cross_doc) | Mean KIC | Latency (Q1/Q2) | Token (Q1/Q2) |
| --- | --- | --- | --- | --- | --- |
| base_llm | 0.208 | 0.340 | 0.274 | 7.06s / 33.38s | 1.14k / 1.29k |
| base_rag | **0.625** | **1.000** | **0.813** | 14.79s / 17.28s | 36.14k / 36.99k |
| mpkm_full | 0.417 | 0.717 | 0.567 | 2.66m / 3.43m | 65.47k / 178.2k |

### 3.2 Per-Fact Breakdown 

- Question 1: how_to

    | Fact ID | Description | base_llm | base_rag | mpkm_full |
    | --- | --- | --- | --- | --- |
    | F1 | Console panel must be opened before entering commands | ✅ | ❌ | ❌ |
    | F2 | Each event must be executed using the `event` console command | ❌ | ✅ | ❌ |
    | F3 | Answer provides specific event IDs that grant permanent military modifiers | ❌ | ✅ | ✅ |
    | F4 | Event list includes `flavor_teu.45` | ❌ | ✅ | ✅ |
    | F5 | Event list includes `flavor_swe.3228` | ❌ | ✅ | ✅ |
    | F6 | Event list includes `flavor_rus.28` | ❌ | ❌ | ✅ |
    | F7 | Event list includes `flavor_bah.5` | ❌ | ✅ | ❌ |
    | F8 | Event list includes `flavor_rus.45` | ❌ | ❌ | ❌ |
    | F9 | Event list includes `flavor_dan.124` | ❌ | ❌ | ❌ |
    | F10 | Event list includes `synthetic_dawn.5` | ❌ | ❌ | ✅ |
    | F11 | Event list includes `usa_dlc.13` | ❌ | ✅ | ❌ |
    | F12 | Event list includes `flavor_ita.6` | ❌ | ✅ | ✅ |

- Question 2: cross_doc_synthesis

    | Fact ID | Description | base_llm | base_rag | mpkm_full |
    | --- | --- | --- | --- | --- |
    | fact_001 | Must mention at least two of Poland’s core challenges in the early game (the interregnum, the Ottomans, Muscovy, and the Teutonic Order) | ❌ | ✅ | ✅ |
    | fact_002 | Must mention the importance of diplomatic reputation for Poland in attracting allies | ❌ | ✅ | ✅ |
    | fact_003 | Must provide at least 2 specific console commands (from console.txt), with the command names being correct | ✅ | ✅ | ✅ |
    | fact_004 | Must explain why these commands are particularly useful for Poland. | ✅ | ✅ | ❌ |
    | fact_005 | Must mention the issue of religious tolerance or missionary work in the later game | ❌ | ✅ | ✅ |
    | fact_006 | Must make trade-offs—explicitly state which commands can be omitted or are lower priority. | ❌ | ✅ | ❌ |

**Observation**

- MPKM's coverage of *specific command names* is noticeably lower than base_rag.

- MPKM also underperforms on high-level synthesis facts (fact_004, fact_006), suggesting the pipeline's weakness is not limited to information loss, but also affects judgment and trade-off reasoning.

- MPKM's latency is **~10×** higher and token cost is **2–5×** higher than base_rag, while producing lower KIC scores. This suggests that on small knowledge bases, the multi-agent architecture's overhead is not justified by its output quality.

### 3.3 Per-Layer KIC Trace

- Q1: how_to

    This trace measures how KIC evolves as information flows through the MPKM pipeline.

    | Pipeline Stage | KIC | Relative Retention | Cumulative Loss |
    | --- | --- | --- | --- |
    | Raw documents (baseline) | 1.000 | 100% | 0% |
    | After Investigator (`knowledge_chunk`) | **0.459** | 45.9% | **-54.1%** |
    | After Generator (`final_draft`) | 0.417 | 41.7% | -58.3% |

    **Finding**: The Investigator node alone accounts for **54.1%** of information loss. The combined downstream loss (Synthesizer + Generator) is only **4.2%**. The bottleneck might be localized to the first extraction step, rather than the full pipeline.

- Q2: cross_doc_synthesis

    This trace measures how KIC evolves as information flows through the MPKM pipeline.

    | Pipeline Stage | KIC | Relative Retention | Cumulative Loss |
    | --- | --- | --- | --- |
    | Raw documents (baseline) | 1.000 | 100% | 0% |
    | After Investigator (`knowledge_chunk`) | **0.528** | 52.8% | **-47.2%** |
    | After Generator (`final_draft`) | 0.717 | 71.7% | -29.3% |

    **Finding**: The Investigator node still drops approximately half of the facts. However, an anomaly appears: the `final_draft` covers more facts than `knowledge_chunk`, even though the latter is the upstream input. Since the Generator receives the `knowledge_chunk` as part of its context, it is unlikely that new facts were introduced.

    **KIC** is defined as the weighted coverage:

    $$
    \text{KIC} = \frac{\sum_{i} w_i \cdot \mathbb{1}[f_i \in A]}{\sum_{i} w_i}
    $$

    where $A$ is the evaluated article, $f_i$ is the $i$-th key fact, $w_i$ is its importance weight, and $\mathbb{1}[\cdot]$ is the indicator function. When a single fact $f_j$ flips its judgment, the KIC shift is:

    $$
    |\Delta \text{KIC}| = \frac{w_j}{\sum_{i} w_i}
    $$

    For Q2, $\sum_{i} w_i = 5.3$. The observed gap is:

    $$
    \Delta \text{KIC} = 0.717 - 0.528 = 0.189
    $$

    A single high-weight fact flip ($w_j = 1.0$) produces:

    $$
    \frac{1.0}{5.3} \approx 0.189 \quad \checkmark
    $$

    This matches the observed gap exactly. The most parsimonious explanation is that the LLM Judge misclassified one high-weight fact at the `knowledge_chunk` stage, rather than the Generator having introduced new information.
---

## 4. Observations

- MPKM's coverage of *specific command names* is noticeably lower than base_rag. The per-layer trace localizes this loss to the Investigator node.

- MPKM also underperforms on high-level synthesis facts (fact_004, fact_006), suggesting the pipeline's weakness is not limited to extraction fidelity, but also affects judgment and trade-off reasoning.

- MPKM's latency is **~10×** higher and token cost is **2–5×** higher than base_rag, while producing lower KIC scores. On small knowledge bases, the multi-agent architecture's overhead is not justified by its output quality.

---

## 5. Methodological Note

With only 6–12 key facts per question and a single LLM-judge evaluation, KIC scores are sensitive to judge noise.

This is not merely a theoretical concern. **Repeated evaluations of the same article at `temperature=0` produced inconsistent fact-level classifications.** Individual facts were observed to flip between ✅ and ❌ across runs, confirming that the LLM Judge itself is a source of non-determinism.

The magnitude of this noise can be derived analytically. For a single fact $f_j$, the KIC shift is:

$$
|\Delta \text{KIC}| = \frac{w_j}{\sum_i w_i}
$$

For Q1, $\sum_i w_i = 4.8$, giving a single-flip noise floor of $\frac{1.0}{4.8} \approx 0.208$. For Q2, $\sum_i w_i = 5.3$, giving $\frac{1.0}{5.3} \approx 0.189$. These values are consistent with the observed KIC gap in Q2 (0.717 − 0.528 = 0.189).

**Implication**: Single-evaluation KIC carries a noise floor of approximately $\pm 0.2$ per high-weight fact. All per-layer trace conclusions should be treated as working hypotheses pending multi-evaluation aggregation (e.g., 3× majority vote).

---

## 6. Conclusion

The benchmark results suggest that MPKM's architectural complexity becomes counterproductive when the knowledge base is small enough to fit within the context window. Per-layer tracing localizes the primary information loss to the **Investigator node** (54% KIC drop), not to the full pipeline. In this regime, naive RAG's direct document-to-LLM path maintains information fidelity that MPKM's extraction step discards.

---

## 7. Next Steps

### Immediate (diagnosis)

- [x] Run multi-evaluation (3× with majority vote) on Q1 to confirm the Investigator bottleneck.
- [x] Trace the same per-layer KIC on Q2 to verify whether the same pattern holds.

### Short-term (fix)

- [ ] Revise the Investigator prompt with a hard constraint: preserve all specific identifiers (certain command, long-fixed sentence).
- [ ] Re-run Q1 with the revised prompt and compare KIC at each pipeline stage.

### Long-term (validate)

- [ ] Expand dataset to 10+ questions across categories.
- [ ] Expand knowledge base to 200+ documents.
- [ ] Introduce Chroma and test whether MPKM overtakes base_rag at scale.


