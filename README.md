# A Standardized Re-evaluation of Conversational Recommender Systems on the ReDial Dataset

This repository provides the code and results accompanying the paper *"A Standardized Re-evaluation of Conversational Recommender Systems on the ReDial Dataset"* (SIGIR '26). [[DOI]](https://doi.org/10.1145/3805712.3808573)

## Summary

Recent years have seen a surge of research into conversational recommender systems (CRS). Among existing datasets, ReDial is the most widely used benchmark, cited in hundreds of studies. However, variations in how the dataset is preprocessed and used in experiments, particularly in the definition of ground-truth items, make it difficult to compare results across studies. These comparisons are further complicated by confounding factors such as the choice of the underlying large language model (LLM) and the use of external data sources. In this work, we revisit seven prominent CRS methods across three architectural families and evaluate them under standardized conditions. Our reproducibility study reveals a "granularity gap," where fine-grained ranking (Recall@1) is highly sensitive to implementation details, while our replicability analysis shows that nearly 50% of reported accuracy stems from "repetition shortcuts" that are absent in novelty-focused evaluation. Furthermore, we find that performance gains are often driven more by the capacity of the LLM backbone than by specific architectural innovations. Finally, by applying user-centric utility metrics, we demonstrate that traditional recall frequently overstates a system's actual conversational effectiveness. This work establishes a transparent, controlled baseline and promotes evaluation practices that prioritize novelty and interaction efficiency.

We evaluate seven methods across three architectural families:

- **(i) Modular Fusion Pipelines**: KBRD, KGSF
- **(ii) Shared-Backbone Pipelines**: UniCRS, ECR
- **(iii) Unified Single-Backbone Pipelines**: MESE, PECRS, ReFICR

## ReDial

[ReDial](https://redialdata.github.io/website/) is a dataset of human-human dialogues in which one participant (the recommender) helps another (the seeker) find a movie to watch.

| Split | #Conv | #Rec-Instances | #Movie-Mentions | #Unique Movies |
|---|---|---|---|---|
| Train | 10,006 | 34,591 | 50,597 | 6,084 |
| Test | 1,342 | 4,198 | 6,736 | 1,936 |
| **Total** | **11,348** | **38,789** | **57,333** | **6,486** |

We evaluate all methods on three variants of the ReDial test set, since methods differ in how they preprocess and filter the raw data:

- **original** — original test split from each model's paper
- **full** (`recommender_all`) — all turns where a recommendation is made (3,617 rows)
- **dedup** (`recommender_dedup`) — dedup variant, excluding turns where the recommended item appeared earlier in the same conversation (3,372 rows)

Metric: R@K = fraction of ground-truth movie mentions found in top-K predictions. ReFICR numbers are pre-reranking (50 candidates retrieved; reranker returns top-10).

Per-system code and instructions: [`unicrs/`](unicrs/README.md), [`mese/`](mese/README.md), [`pecrs/`](pecrs/README.md), [`reficr/`](reficr/README.md), [`ecr/`](ecr/README.md). KBRD/KGSF are run via [CRSLab](https://github.com/RUCAIBox/CRSLab).

## Results

The tables below reproduce the paper's main tables. Where a method uses multiple LLM backbones in this repo, the row shown here is the method's *primary* backbone as reported in the paper (UniCRS/ECR: DialoGPT-small, MESE: GPT2-small, PECRS: GPT2-medium).

### Table 1 — Reproducibility: original paper vs. our implementation

Recall on each method's original test split, comparing the numbers reported in the original paper with our reproduced numbers.

| Method | Paper R@1 | Paper R@10 | Paper R@50 | Ours R@1 | Ours R@10 | Ours R@50 |
|---|---|---|---|---|---|---|
| KBRD | 0.030 | 0.163 | 0.338 | 0.036 | 0.176 | 0.334 |
| KGSF | 0.039 | 0.183 | 0.378 | 0.034 | 0.179 | 0.365 |
| UniCRS | 0.051 | 0.224 | 0.428 | 0.049 | 0.213 | 0.421 |
| ECR | 0.049 | 0.220 | 0.428 | 0.046 | 0.217 | 0.426 |
| MESE | 0.056 | 0.256 | 0.455 | 0.048 | 0.243 | 0.452 |
| PECRS | 0.058 | 0.225 | 0.416 | 0.050 | 0.211 | 0.401 |
| ReFICR | 0.061 | 0.305 | 0.532 | 0.049 | 0.280 | 0.522 |

### Table 2 — Replicability: standardized dataset with and without deduplication

Reproduced results on the standardized dataset, with and without deduplication. As a reference we include a naive method that recommends context items in reversed order of mention.

| Method | R@1 (no dedup) | R@10 (no dedup) | R@50 (no dedup) | R@1 (dedup) | R@10 (dedup) | R@50 (dedup) |
|---|---|---|---|---|---|---|
| KBRD | 0.033 | 0.177 | 0.332 | 0.017 | 0.148 | 0.300 |
| KGSF | 0.032 | 0.177 | 0.369 | 0.016 | 0.147 | 0.327 |
| UniCRS | 0.049 | 0.213 | 0.421 | 0.024 | 0.180 | 0.335 |
| ECR | 0.049 | 0.220 | 0.428 | 0.026 | 0.181 | 0.337 |
| MESE | 0.032 | 0.178 | 0.381 | 0.025 | 0.159 | 0.361 |
| PECRS | 0.044 | 0.189 | 0.383 | 0.022 | 0.143 | 0.341 |
| ReFICR | 0.049 | 0.270 | 0.507 | 0.018 | 0.213 | 0.465 |
| **Naive** | **0.043** | **0.090** | **0.090** | **0.000** | **0.000** | **0.000** |

### Table 3 — Generalization: LLM backbone

Cross-backbone generalizability results on the standardized deduplicated test collection (R@1 / R@50 per backbone). Limited to the four methods sharing the GPT2-family backbone group.

| Method | GPT2-small R@1 | GPT2-small R@50 | GPT2-medium R@1 | GPT2-medium R@50 | DialoGPT-small R@1 | DialoGPT-small R@50 |
|---|---|---|---|---|---|---|
| UniCRS | 0.021 | 0.315 | 0.026 | 0.321 | 0.024 | 0.335 |
| ECR | 0.019 | 0.315 | 0.021 | 0.330 | 0.026 | 0.337 |
| MESE | 0.025 | 0.361 | 0.027 | 0.371 | 0.016 | 0.312 |
| PECRS | 0.022 | 0.341 | 0.027 | 0.362 | 0.017 | 0.345 |

### Table 4 — Generalization: user-centric utility metrics

Success Rate (SR) and Reward-per-Dialogue-Length (RDL) are reported alongside R@1 on the standardized dataset, with and without deduplication.

| Method | R@1 (no dedup) | SR (no dedup) | RDL (no dedup) | R@1 (dedup) | SR (dedup) | RDL (dedup) |
|---|---|---|---|---|---|---|
| KBRD | 0.033 | 0.103 | 0.049 | 0.017 | 0.046 | 0.036 |
| KGSF | 0.032 | 0.093 | 0.048 | 0.016 | 0.036 | 0.036 |
| UniCRS | 0.049 | 0.101 | 0.041 | 0.024 | 0.048 | 0.030 |
| ECR | 0.049 | 0.104 | 0.041 | 0.026 | 0.063 | 0.033 |
| MESE | 0.032 | 0.113 | 0.051 | 0.025 | 0.051 | 0.043 |
| PECRS | 0.044 | 0.121 | 0.053 | 0.022 | 0.052 | 0.047 |
| ReFICR | 0.049 | 0.151 | 0.074 | 0.018 | 0.053 | 0.053 |
| **Naive** | **0.043** | **0.100** | **0.009** | **0.000** | **0.000** | **0.000** |

SR = fraction of *dialogues* where the system recommends at least one relevant item (liked or seen by the user) within the top-1 predictions in any turn. RDL = sum(reward / dialogue_length) / n_dialogues, where reward = 1.0 for a liked item and 0.5 for a seen item, accumulated across all turns in the dialogue. Liked/seen annotations from ReDial `initiatorQuestions`.

## Citation

If you use the resources in this repository, please cite:

```bibtex
@inproceedings{Kostric:2026:SIGIR,
author = {Kostric, Ivica and Balog, Krisztian},
title = {A Standardized Re-evaluation of Conversational Recommender Systems on the ReDial Dataset},
year = {2026},
booktitle = {Proceedings of the 49th International ACM SIGIR Conference on Research and Development in Information Retrieval},
pages = {2952–2960},
numpages = {9},
series = {SIGIR '26}
}
```

## Contact

Should you have any questions, please contact Ivica Kostric at ivica.kostric@uis.no.
