# MiniGeo Risks And Controls

| Risk | Control |
|---|---|
| Chinese text encoding corruption | Store and read all text as UTF-8; keep tests with Chinese examples. |
| Chinese BM25 underperforms | Use `jieba` when available, with character bigram fallback; compare with dense retrieval later. |
| Benchmark leakage | Do not train on MiniGeo-Bench reference answers. |
| Data license ambiguity | Commit metadata and scripts, not raw copyrighted files. |
| Colab memory limits | Keep Qwen3.5-2B as the default model and run QLoRA smoke tests first. |
| Verifier false positives or false negatives | Keep human-reviewed failure cases in `results/failure_cases.md`. |
| Agent prompt brittleness | Test SQL tools separately before combined document + SQL agent demos. |

